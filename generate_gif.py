import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Canvas setup - Render at 2x resolution for retina anti-aliasing
SUPER_W = 1400
SUPER_H = 700
FINAL_W = 700
FINAL_H = 350
TOTAL_FRAMES = 72

frames = []

def ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * math.pow(t - 1, 3) + c1 * math.pow(t - 1, 2)

for f in range(TOTAL_FRAMES):
    # Base Canvas (Dark GitHub Theme #0d1117)
    img = Image.new("RGBA", (SUPER_W, SUPER_H), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)

    # Keyframe timeline (72 frames @ ~25 fps = 2.88s loop)
    # 0..14: Calm wearing glasses
    # 14..32: Glasses slide up smoothly onto head
    # 32..50: Eyes narrow into intense sinister glare + red glowing aura
    # 50..62: Evil glare hold with subtle pulsing light
    # 62..72: Smooth return/reset transition

    if f < 14:
        slide_t = 0.0
        squint_t = 0.0
        evil_glow = 0.0
    elif f < 32:
        slide_t = ease_in_out_cubic((f - 14) / 18.0)
        squint_t = 0.0
        evil_glow = 0.0
    elif f < 50:
        slide_t = 1.0
        squint_t = ease_in_out_cubic((f - 32) / 18.0)
        evil_glow = squint_t
    elif f < 62:
        slide_t = 1.0
        squint_t = 1.0
        pulse = (math.sin((f - 50) * 0.45) + 1) / 2.0
        evil_glow = 0.75 + 0.25 * pulse
    else:
        return_t = (f - 62) / 10.0
        slide_t = 1.0 - ease_in_out_cubic(return_t)
        squint_t = 1.0 - ease_in_out_cubic(return_t)
        evil_glow = (1.0 - return_t) * 0.75

    left_center = (SUPER_W // 2 - 230, SUPER_H // 2 + 25)
    right_center = (SUPER_W // 2 + 230, SUPER_H // 2 + 25)

    # 1. Sinister Background Ambient Aura (Glow behind eyes)
    if evil_glow > 0.001:
        glow_layer = Image.new("RGBA", (SUPER_W, SUPER_H), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        r_alpha = int(180 * evil_glow)
        
        # Outer deep red aura
        glow_draw.ellipse(
            [left_center[0]-240, left_center[1]-150, left_center[0]+240, left_center[1]+150],
            fill=(255, 10, 50, r_alpha)
        )
        glow_draw.ellipse(
            [right_center[0]-240, right_center[1]-150, right_center[0]+240, right_center[1]+150],
            fill=(255, 10, 50, r_alpha)
        )
        
        # Core intense crimson glow
        glow_draw.ellipse(
            [left_center[0]-140, left_center[1]-90, left_center[0]+140, left_center[1]+90],
            fill=(255, 60, 90, int(r_alpha * 0.6))
        )
        glow_draw.ellipse(
            [right_center[0]-140, right_center[1]-90, right_center[0]+140, right_center[1]+90],
            fill=(255, 60, 90, int(r_alpha * 0.6))
        )
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(50))
        img = Image.alpha_composite(img, glow_layer)
        draw = ImageDraw.Draw(img)

    # 2. Draw High-Detail Cyberpunk/Anime Eyes
    def draw_eye(center, is_left, squint):
        cx, cy = center
        
        # Sclera (White base) dynamic morphing
        # Neutral: Wide almond shape (rx=150, ry=90)
        # Squint: Sharp razor slit (rx=155, ry=32)
        ry_top = 90 - squint * 62
        ry_bot = 80 - squint * 52
        
        num_pts = 40
        sclera_pts = []
        
        # Upper eyelid contour
        for i in range(num_pts + 1):
            t = i / num_pts
            x = cx - 155 + t * 310
            arch = math.sin(t * math.pi)
            # Slanted inward drop when squinting
            tilt = (1 if is_left else -1) * (t - 0.5) * 36 * squint
            y = cy - arch * ry_top + tilt
            sclera_pts.append((x, y))
            
        # Lower eyelid contour
        for i in range(num_pts + 1):
            t = 1.0 - (i / num_pts)
            x = cx - 155 + t * 310
            arch = math.sin(t * math.pi)
            tilt = (1 if is_left else -1) * (t - 0.5) * 14 * squint
            y = cy + arch * ry_bot + tilt
            sclera_pts.append((x, y))

        # Sclera Color (Off-white -> Sinister tint)
        sclera_r = int(245 + 10 * squint)
        sclera_g = int(248 - 85 * squint)
        sclera_b = int(252 - 95 * squint)
        sclera_color = (sclera_r, sclera_g, sclera_b, 255)

        draw.polygon(sclera_pts, fill=sclera_color)
        
        # Iris & Pupil
        iris_r = 60 - squint * 8
        iris_dx = (22 if is_left else -22) * squint # Eyes focus sharply inward
        iris_cx = cx + iris_dx
        iris_cy = cy + 4 * squint
        
        # Iris Color Transition: Glowing Cyan/Teal -> Menacing Crimson Red
        r_i = int(40 + (255 - 40) * squint)
        g_i = int(200 - (200 - 20) * squint)
        b_i = int(250 - (250 - 65) * squint)
        
        # Outer Iris Ring
        draw.ellipse(
            [iris_cx - iris_r, iris_cy - iris_r, iris_cx + iris_r, iris_cy + iris_r],
            fill=(r_i, g_i, b_i, 255),
            outline=(20, 25, 35, 255),
            width=4
        )
        
        # Inner Iris Ring (Luminous Core)
        inner_r = iris_r * 0.7
        r_core = min(255, int(r_i * 1.2))
        g_core = max(0, int(g_i * 0.5))
        b_core = max(0, int(b_i * 0.5))
        draw.ellipse(
            [iris_cx - inner_r, iris_cy - inner_r, iris_cx + inner_r, iris_cy + inner_r],
            fill=(r_core, g_core, b_core, 255)
        )

        # Pupil (Deep black center)
        pupil_r = 26 - squint * 10
        draw.ellipse(
            [iris_cx - pupil_r, iris_cy - pupil_r, iris_cx + pupil_r, iris_cy + pupil_r],
            fill=(8, 10, 16, 255)
        )
        
        # Glint / Highlights
        if squint < 0.5:
            # Neutral soft highlights
            draw.ellipse([iris_cx - 24, iris_cy - 28, iris_cx - 8, iris_cy - 12], fill=(255, 255, 255, 230))
            draw.ellipse([iris_cx + 12, iris_cy + 10, iris_cx + 22, iris_cy + 20], fill=(255, 255, 255, 140))
        else:
            # Evil Sharp Glint
            draw.ellipse([iris_cx - 20, iris_cy - 24, iris_cx - 4, iris_cy - 8], fill=(255, 255, 255, 255))
            draw.ellipse([iris_cx + 8, iris_cy + 8, iris_cx + 20, iris_cy + 20], fill=(255, 50, 90, 240))

        # Eyelid Dark Outline & Lashes
        draw.line(sclera_pts[:num_pts+1], fill=(16, 20, 28, 255), width=10)
        draw.line(sclera_pts[num_pts+1:], fill=(16, 20, 28, 255), width=6)

        # Eyebrows (Crucial for Sinister glare `\   /`)
        brow_y_base = cy - 120
        if is_left:
            start_x, start_y = cx - 170, brow_y_base + 10 - squint * 10
            mid_x, mid_y = cx - 20, brow_y_base - 20 + squint * 45
            end_x, end_y = cx + 140, brow_y_base + 70 * squint
        else:
            start_x, start_y = cx - 140, brow_y_base + 70 * squint
            mid_x, mid_y = cx + 20, brow_y_base - 20 + squint * 45
            end_x, end_y = cx + 170, brow_y_base + 10 - squint * 10

        brow_color = (240, 245, 250, 255) if squint < 0.5 else (255, 50, 80, 255)
        draw.line([(start_x, start_y), (mid_x, mid_y), (end_x, end_y)], fill=brow_color, width=14)

    draw_eye(left_center, is_left=True, squint=squint_t)
    draw_eye(right_center, is_left=False, squint=squint_t)

    # 3. Glasses (Wireframe Glasses with Neon Edge & Sheen)
    # Glasses slide up vertically from y=0 to y=-190
    glasses_offset_y = -190 * slide_t
    g_ly = left_center[1] + glasses_offset_y
    g_lx = left_center[0]
    g_ry = right_center[1] + glasses_offset_y
    g_rx = right_center[0]
    
    frame_w = 320
    frame_h = 190
    
    lf_box = [g_lx - frame_w//2, g_ly - frame_h//2, g_lx + frame_w//2, g_ly + frame_h//2]
    rf_box = [g_rx - frame_w//2, g_ry - frame_h//2, g_rx + frame_w//2, g_ry + frame_h//2]
    
    # Lens Sheen / Reflection
    sheen_overlay = Image.new("RGBA", (SUPER_W, SUPER_H), (0, 0, 0, 0))
    sheen_draw = ImageDraw.Draw(sheen_overlay)
    sheen_draw.polygon([
        (lf_box[0]+30, lf_box[1]+15), (lf_box[0]+130, lf_box[1]+15),
        (lf_box[0]+50, lf_box[3]-15), (lf_box[0]+15, lf_box[3]-15)
    ], fill=(255, 255, 255, 45))
    sheen_draw.polygon([
        (rf_box[0]+30, rf_box[1]+15), (rf_box[0]+130, rf_box[1]+15),
        (rf_box[0]+50, rf_box[3]-15), (rf_box[0]+15, rf_box[3]-15)
    ], fill=(255, 255, 255, 45))
    img = Image.alpha_composite(img, sheen_overlay)
    draw = ImageDraw.Draw(img)

    frame_border_color = (35, 43, 58, 255)
    frame_glow = (56, 189, 248, 255) if slide_t < 0.5 else (255, 70, 100, 255)
    
    # Outer Rounded Frame
    draw.rounded_rectangle(lf_box, radius=36, outline=frame_border_color, width=14)
    draw.rounded_rectangle(rf_box, radius=36, outline=frame_border_color, width=14)
    
    # Inner Luminous Ring
    draw.rounded_rectangle(
        [lf_box[0]+6, lf_box[1]+6, lf_box[2]-6, lf_box[3]-6],
        radius=30, outline=frame_glow, width=4
    )
    draw.rounded_rectangle(
        [rf_box[0]+6, rf_box[1]+6, rf_box[2]-6, rf_box[3]-6],
        radius=30, outline=frame_glow, width=4
    )

    # Bridge & Temples
    bridge_y = g_ly - 8
    draw.line([(g_lx + frame_w//2, bridge_y), (g_rx - frame_w//2, bridge_y)], fill=frame_border_color, width=12)
    draw.line([(g_lx + frame_w//2, bridge_y), (g_rx - frame_w//2, bridge_y)], fill=frame_glow, width=4)

    draw.line([(lf_box[0], g_ly - 15), (lf_box[0] - 110, g_ly - 45)], fill=frame_border_color, width=10)
    draw.line([(rf_box[2], g_ry - 15), (rf_box[2] + 110, g_ry - 45)], fill=frame_border_color, width=10)

    # 4. Star Sparkle Effect during Glare Peak
    if 36 <= f <= 56:
        sparkle_t = (f - 36) / 20.0
        s_alpha = int(255 * math.sin(sparkle_t * math.pi))
        
        # Left Eye Sparkle
        gx, gy = left_center[0] + 90, left_center[1] - 25
        draw.line([(gx-28, gy), (gx+28, gy)], fill=(255, 255, 255, s_alpha), width=6)
        draw.line([(gx, gy-28), (gx, gy+28)], fill=(255, 255, 255, s_alpha), width=6)
        draw.line([(gx-14, gy-14), (gx+14, gy+14)], fill=(255, 70, 100, s_alpha), width=3)
        draw.line([(gx-14, gy+14), (gx+14, gy-14)], fill=(255, 70, 100, s_alpha), width=3)
        
        # Right Eye Sparkle
        gx2, gy2 = right_center[0] - 90, right_center[1] - 25
        draw.line([(gx2-28, gy2), (gx2+28, gy2)], fill=(255, 255, 255, s_alpha), width=6)
        draw.line([(gx2, gy2-28), (gx2, gy2+28)], fill=(255, 255, 255, s_alpha), width=6)
        draw.line([(gx2-14, gy2-14), (gx2+14, gy2+14)], fill=(255, 70, 100, s_alpha), width=3)
        draw.line([(gx2-14, gy2+14), (gx2+14, gy2-14)], fill=(255, 70, 100, s_alpha), width=3)

    # Downsample (2x -> 1x) with LANCZOS for ultra crisp anti-aliasing
    final_img = img.resize((FINAL_W, FINAL_H), resample=Image.LANCZOS)
    
    bg_rgb = Image.new("RGB", (FINAL_W, FINAL_H), (13, 17, 23))
    bg_rgb.paste(final_img, mask=final_img.split()[3])
    quantized = bg_rgb.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
    frames.append(quantized)

output_path = r"c:\Users\THINKPAD X13\Vibes Codes\GitHub Gustavo\real_eyes_animation.gif"
frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=45,
    loop=0
)
print("Ultra-aesthetic GIF generated successfully at:", output_path)
