import os
from PIL import Image, ImageStat, ImageOps

def analyze_area(region):
    """
    Returns average brightness and standard deviation (chaos).
    """
    stat = ImageStat.Stat(region.convert('L'))
    brightness = stat.mean[0]
    # Standard deviation indicates how much pixels vary from each other
    # Useful to detect "busy" areas vs "empty" areas
    chaos = stat.stddev[0] 
    return brightness, chaos

def apply_watermark(
    input_folder, 
    output_folder, 
    watermark_path, 
    recursive=True, 
    width_percent=20, 
    bottom_padding=10,       # NEW: User-defined padding from the bottom in pixels
    auto_invert=True,
    inversion_threshold=180,
    check_empty_space=True,  # Looks for "calm" space
    chaos_threshold=30       # Below this value, the area is considered "empty/calm"
):
    if not os.path.exists(input_folder): return
    
    wm_original = Image.open(watermark_path).convert("RGBA")
    wm_dark = ImageOps.invert(wm_original.convert("RGB")).convert("RGBA")
    wm_dark.putalpha(wm_original.getchannel('A'))

    count = 0
    for root, _, files in os.walk(input_folder):
        if not recursive and root != input_folder: continue

        for filename in files:
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                source_path = os.path.join(root, filename)
                target_dir = os.path.join(output_folder, os.path.relpath(root, input_folder))
                os.makedirs(target_dir, exist_ok=True)

                try:
                    with Image.open(source_path).convert("RGBA") as img:
                        img_w, img_h = img.size
                        
                        # Calculate watermark dimensions based on width percentage
                        tw = int(img_w * width_percent / 100)
                        th = int(float(wm_original.size[1]) * (tw / float(wm_original.size[0])))
                        
                        # Side margin (horizontal) remains 3% of width for balance
                        side_margin = int(img_w * 0.03)
                        
                        # --- POSITIONING LOGIC ---
                        # Use bottom_padding for the Y coordinate
                        y_pos = img_h - th - bottom_padding

                        # Position A: Bottom Right
                        pos_a = (img_w - tw - side_margin, y_pos)
                        region_a = img.crop((pos_a[0], pos_a[1], pos_a[0] + tw, pos_a[1] + th))
                        lum_a, chaos_a = analyze_area(region_a)

                        final_pos = pos_a
                        final_lum = lum_a
                        log_pos = "Bottom-Right"

                        if check_empty_space and chaos_a > chaos_threshold:
                            # Position B: Bottom Center
                            pos_b = ((img_w // 2) - (tw // 2), y_pos)
                            region_b = img.crop((pos_b[0], pos_b[1], pos_b[0] + tw, pos_b[1] + th))
                            lum_b, chaos_b = analyze_area(region_b)
                            
                            if chaos_b < chaos_a:
                                final_pos = pos_b
                                final_lum = lum_b
                                log_pos = "Bottom-Center"

                        # --- COLOR SELECTION ---
                        if auto_invert and final_lum > inversion_threshold:
                            wm_working = wm_dark.copy()
                        else:
                            wm_working = wm_original.copy()

                        wm_working = wm_working.resize((tw, th), Image.Resampling.LANCZOS)

                        # --- OPACITY ---
                        opacity_level = 255 if 100 < final_lum < 200 else 220
                        alpha = wm_working.getchannel('A')
                        alpha = alpha.point(lambda i: i * (opacity_level / 255.0))
                        wm_working.putalpha(alpha)

                        # --- APPLY AND SAVE ---
                        img.paste(wm_working, final_pos, wm_working)
                        img.save(os.path.join(target_dir, filename), "PNG")
                        
                        print(f"✅ {filename} | Pos: {log_pos} | Chaos: {int(chaos_a)} | Op: {opacity_level}")
                        count += 1

                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")

    print(f"\nTask Finished. Total images processed: {count}")
    print(f"Saved in: {output_folder}")

# --- EXECUTION ---
apply_watermark(
    input_folder="inputs",
    output_folder="output",
    watermark_path="Watermark.png",
    width_percent=25,
    bottom_padding=10,       # Adjust this value to move the watermark up or down
    check_empty_space=True,
    chaos_threshold=30,      
    inversion_threshold=180
)