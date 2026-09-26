import math
import os
from PIL import Image, ImageDraw, ImageFilter

WIDTH = 600
HEIGHT = 300
TOTAL_FRAMES = 64

frames = []

def ease_in_out(t):
    return t * t * (3 - 2 * t)

for f in range(TOTAL_FRAMES):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)

    # Timeline (64 frames at 50ms = 3.2 seconds total loop)
    # 0..12: Neutral wearing glasses
    # 12..26: Glasses slide up
    # 26..40: Squinting into evil glare
    # 40..54: Evil glare pause + red glowing aura
    # 54..64: Reset back to neutral

    if f < 12:
        slide_t = 0.0
        squint_t = 0.0
        evil_glow = 0.0
    elif f < 26:
        slide_t = ease_in_out((f - 12) / 14.0)
        squint_t = 0.0
        evil_glow = 0.0
    elif f < 40:
        slide_t = 1.0
        squint_t = ease_in_out((f - 26) / 14.0)
        evil_glow = squint_t
    elif f < 54:
        slide_t = 1.0
        squint_t = 1.0
        pulse = (math.sin((f - 40) * 0.4) + 1) / 2.0
        evil_glow = 0.7 + 0.3 * pulse
    else:
        return_t = (f - 54) / 10.0
        slide_t = 1.0 - ease_in_out(return_t)
        squint_t = 1.0 - ease_in_out(return_t)
        evil_glow = (1.0 - return_t) * 0.7

    left_center = (WIDTH // 2 - 100, HEIGHT // 2 + 10)
    right_center = (WIDTH // 2 + 100, HEIGHT // 2 + 10)

    # Red sinister background aura when evil
    if evil_glow > 0.01:
        glow_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_overlay)
        r_glow = int(140 * evil_glow)
        glow_draw.ellipse(
            [left_center[0]-110, left_center[1]-70, left_center[0]+110, left_center[1]+70],
            fill=(255, 20, 50, r_glow)
        )
        glow_draw.ellipse(
            [right_center[0]-110, right_center[1]-70, right_center[0]+110, right_center[1]+70],
            fill=(255, 20, 50, r_glow)
        )
        glow_overlay = glow_overlay.filter(ImageFilter.GaussianBlur(30))
        img = Image.alpha_composite(img, glow_overlay)
        draw = ImageDraw.Draw(img)

    def draw_eye(center, is_left, squint):
        cx, cy = center
        ry_top = 40 - squint * 30
        ry_bot = 35 - squint * 25
        
        num_pts = 24
        sclera_pts = []
        
        for i in range(num_pts + 1):
            t = i / num_pts
            x = cx - 65 + t * 130
            arch = math.sin(t * math.pi)
            tilt = (1 if is_left else -1) * (t - 0.5) * 16 * squint
            y = cy - arch * ry_top + tilt
            sclera_pts.append((x, y))
            
        for i in range(num_pts + 1):
            t = 1.0 - (i / num_pts)
            x = cx - 65 + t * 130
            arch = math.sin(t * math.pi)
            tilt = (1 if is_left else -1) * (t - 0.5) * 6 * squint
            y = cy + arch * ry_bot + tilt
            sclera_pts.append((x, y))

        sclera_color = (240, 243, 246, 255)
        if squint > 0.3:
            sclera_color = (255, int(240 - 70*squint), int(240 - 80*squint), 255)

        draw.polygon(sclera_pts, fill=sclera_color)
        
        iris_r = 26 - squint * 4
        iris_dx = (10 if is_left else -10) * squint
        iris_cx = cx + iris_dx
        iris_cy = cy + 2 * squint
        
        # Cyan -> Sinister Crimson Red
        r_i = int(56 + (255 - 56) * squint)
        g_i = int(189 - (189 - 15) * squint)
        b_i = int(248 - (248 - 50) * squint)
        
        draw.ellipse(
            [iris_cx - iris_r, iris_cy - iris_r, iris_cx + iris_r, iris_cy + iris_r],
            fill=(r_i, g_i, b_i, 255)
        )
        
        pupil_r = 12 - squint * 4
        draw.ellipse(
            [iris_cx - pupil_r, iris_cy - pupil_r, iris_cx + pupil_r, iris_cy + pupil_r],
            fill=(10, 10, 15, 255)
        )
        
        if squint < 0.5:
            draw.ellipse([iris_cx - 10, iris_cy - 12, iris_cx - 3, iris_cy - 5], fill=(255, 255, 255, 220))
        else:
            draw.ellipse([iris_cx - 8, iris_cy - 10, iris_cx - 2, iris_cy - 4], fill=(255, 255, 255, 255))
            draw.ellipse([iris_cx + 3, iris_cy + 3, iris_cx + 8, iris_cy + 8], fill=(255, 40, 70, 240))

        draw.line(sclera_pts[:num_pts+1], fill=(18, 22, 30, 255), width=5)
        draw.line(sclera_pts[num_pts+1:], fill=(18, 22, 30, 255), width=3)

        # Eyebrows
        brow_y_base = cy - 55
        if is_left:
            start_x, start_y = cx - 75, brow_y_base + 5 - squint * 5
            mid_x, mid_y = cx - 10, brow_y_base - 10 + squint * 22
            end_x, end_y = cx + 65, brow_y_base + 30 * squint
        else:
            start_x, start_y = cx - 65, brow_y_base + 30 * squint
            mid_x, mid_y = cx + 10, brow_y_base - 10 + squint * 22
            end_x, end_y = cx + 75, brow_y_base + 5 - squint * 5

        brow_color = (235, 240, 245, 255) if squint < 0.5 else (255, 50, 70, 255)
        draw.line([(start_x, start_y), (mid_x, mid_y), (end_x, end_y)], fill=brow_color, width=6)

    draw_eye(left_center, is_left=True, squint=squint_t)
    draw_eye(right_center, is_left=False, squint=squint_t)

    # Glasses
    glasses_offset_y = -85 * slide_t
    g_ly = left_center[1] + glasses_offset_y
    g_lx = left_center[0]
    g_ry = right_center[1] + glasses_offset_y
    g_rx = right_center[0]
    
    frame_w = 150
    frame_h = 85
    
    lf_box = [g_lx - frame_w//2, g_ly - frame_h//2, g_lx + frame_w//2, g_ly + frame_h//2]
    rf_box = [g_rx - frame_w//2, g_ry - frame_h//2, g_rx + frame_w//2, g_ry + frame_h//2]
    
    sheen_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sheen_draw = ImageDraw.Draw(sheen_overlay)
    sheen_draw.polygon([
        (lf_box[0]+15, lf_box[1]+8), (lf_box[0]+60, lf_box[1]+8),
        (lf_box[0]+25, lf_box[3]-8), (lf_box[0]+8, lf_box[3]-8)
    ], fill=(255, 255, 255, 40))
    sheen_draw.polygon([
        (rf_box[0]+15, rf_box[1]+8), (rf_box[0]+60, rf_box[1]+8),
        (rf_box[0]+25, rf_box[3]-8), (rf_box[0]+8, rf_box[3]-8)
    ], fill=(255, 255, 255, 40))
    img = Image.alpha_composite(img, sheen_overlay)
    draw = ImageDraw.Draw(img)

    frame_border_color = (35, 42, 56, 255)
    frame_inner_glow = (56, 189, 248, 255) if slide_t < 0.5 else (255, 60, 90, 255)
    
    draw.rounded_rectangle(lf_box, radius=18, outline=frame_border_color, width=7)
    draw.rounded_rectangle(rf_box, radius=18, outline=frame_border_color, width=7)
    
    draw.rounded_rectangle(
        [lf_box[0]+3, lf_box[1]+3, lf_box[2]-3, lf_box[3]-3],
        radius=15, outline=frame_inner_glow, width=2
    )
    draw.rounded_rectangle(
        [rf_box[0]+3, rf_box[1]+3, rf_box[2]-3, rf_box[3]-3],
        radius=15, outline=frame_inner_glow, width=2
    )

    bridge_y = g_ly - 4
    draw.line([(g_lx + frame_w//2, bridge_y), (g_rx - frame_w//2, bridge_y)], fill=frame_border_color, width=6)
    draw.line([(g_lx + frame_w//2, bridge_y), (g_rx - frame_w//2, bridge_y)], fill=frame_inner_glow, width=2)

    draw.line([(lf_box[0], g_ly - 8), (lf_box[0] - 50, g_ly - 20)], fill=frame_border_color, width=5)
    draw.line([(rf_box[2], g_ry - 8), (rf_box[2] + 50, g_ry - 20)], fill=frame_border_color, width=5)

    if 30 <= f <= 46:
        sparkle_t = (f - 30) / 16.0
        s_alpha = int(255 * math.sin(sparkle_t * math.pi))
        
        gx, gy = left_center[0] + 42, left_center[1] - 12
        draw.line([(gx-12, gy), (gx+12, gy)], fill=(255, 255, 255, s_alpha), width=3)
        draw.line([(gx, gy-12), (gx, gy+12)], fill=(255, 255, 255, s_alpha), width=3)
        
        gx2, gy2 = right_center[0] - 42, right_center[1] - 12
        draw.line([(gx2-12, gy2), (gx2+12, gy2)], fill=(255, 255, 255, s_alpha), width=3)
        draw.line([(gx2, gy2-12), (gx2, gy2+12)], fill=(255, 255, 255, s_alpha), width=3)

    bg_rgb = Image.new("RGB", (WIDTH, HEIGHT), (13, 17, 23))
    bg_rgb.paste(img, mask=img.split()[3])
    # Quantize palette for compact file size
    quantized = bg_rgb.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
    frames.append(quantized)

output_path = r"c:\Users\THINKPAD X13\Vibes Codes\GitHub Gustavo\real_eyes_animation.gif"
frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=50,
    loop=0
)
print("Optimized GIF saved to:", output_path)
