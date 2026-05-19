import math
from PIL import Image, ImageDraw, ImageFilter

def draw_planet_symbol(draw, x, y, symbol, color, scale=1.0):
    """Draws a simplified, distinct glowing glyph representation."""
    base_width = max(1, int(3 * scale))
    x = int(x)
    y = int(y)

    if symbol == 'sun': # ☉
        coords = [int(x-6*scale), int(y-6*scale), int(x+6*scale), int(y+6*scale)]
        draw.ellipse(coords, outline=color, width=base_width)
        draw.ellipse([int(x-1*scale), int(y-1*scale), int(x+1*scale), int(y+1*scale)], fill=color)

    elif symbol == 'moon': # ☽
        coords = [int(x-7*scale), int(y-8*scale), int(x+3*scale), int(y+8*scale)]
        draw.chord(coords, -120, 120, fill=color, outline=color)

    elif symbol == 'mercury': # ☿
        draw.line([(x, int(y+8*scale)), (x, int(y-5*scale))], fill=color, width=base_width)
        draw.line([(int(x-5*scale), int(y-2*scale)), (int(x+5*scale), int(y-2*scale))], fill=color, width=base_width)
        draw.arc([int(x-4*scale), int(y-9*scale), int(x+4*scale), int(y-1*scale)], 180, 0, fill=color, width=base_width)
        draw.ellipse([int(x-2*scale), int(y+6*scale), int(x+2*scale), int(y+10*scale)], fill=color)

    elif symbol == 'venus': # ♀
        draw.ellipse([int(x-6*scale), int(y-12*scale), int(x+6*scale), int(y)], outline=color, width=base_width)
        draw.line([(x, int(y+8*scale)), (x, int(y+1*scale))], fill=color, width=base_width)
        draw.line([(int(x-5*scale), int(y+5*scale)), (int(x+5*scale), int(y+5*scale))], fill=color, width=base_width)

    elif symbol == 'mars': # ♂
        draw.ellipse([int(x-6*scale), int(y-6*scale), int(x+6*scale), int(y+6*scale)], outline=color, width=base_width)
        draw.line([(int(x+3*scale), int(y-3*scale)), (int(x+10*scale), int(y-10*scale))], fill=color, width=base_width)
        draw.polygon([(int(x+8*scale), int(y-10*scale)), (int(x+10*scale), int(y-8*scale)), (int(x+12*scale), int(y-12*scale))], fill=color)

    elif symbol == 'jupiter': # ♃
        draw.chord([int(x-3*scale), int(y-8*scale), int(x+7*scale), int(y+8*scale)], 120, 300, fill=color, outline=color)
        draw.line([(x, int(y-1*scale)), (x, int(y-10*scale))], fill=color, width=base_width)
        draw.line([(int(x-5*scale), int(y-6*scale)), (int(x+5*scale), int(y-6*scale))], fill=color, width=base_width)

    elif symbol == 'saturn': # ♄
        draw.line([(x, int(y+1*scale)), (x, int(y-10*scale))], fill=color, width=base_width)
        draw.line([(int(x-6*scale), int(y-5*scale)), (int(x+6*scale), int(y-5*scale))], fill=color, width=base_width)
        draw.line([(int(x-3*scale), int(y-2*scale)), (int(x+1*scale), int(y+6*scale)), (int(x-3*scale), int(y+10*scale))], fill=color, width=base_width)

    elif symbol == 'uranus': # ♅
        draw.line([(x, int(y-10*scale)), (x, int(y+3*scale))], fill=color, width=base_width)
        draw.line([(int(x-6*scale), int(y-5*scale)), (int(x+6*scale), int(y-5*scale))], fill=color, width=base_width)
        draw.arc([int(x-5*scale), int(y-10*scale), int(x+5*scale), int(y+0*scale)], 180, 0, fill=color, width=base_width)
        draw.ellipse([int(x-2*scale), int(y+1*scale), int(x+2*scale), int(y+5*scale)], fill=color)

    elif symbol == 'neptune': # ♆
        draw.line([(x, int(y-10*scale)), (x, int(y+3*scale))], fill=color, width=base_width)
        draw.line([(int(x-6*scale), int(y-5*scale)), (int(x+6*scale), int(y-5*scale))], fill=color, width=base_width)
        draw.line([(int(x-5*scale), int(y-10*scale)), (int(x+5*scale), int(y-10*scale))], fill=color, width=base_width)
        draw.polygon([(int(x-7*scale), int(y-8*scale)), (x, int(y-2*scale)), (int(x+7*scale), int(y-8*scale))], outline=color, width=base_width)

    elif symbol == 'pluto': # ♇
        draw.ellipse([int(x-6*scale), int(y-6*scale), int(x+6*scale), int(y+6*scale)], outline=color, width=base_width)
        draw.line([(x, int(y-10*scale)), (x, int(y+1*scale))], fill=color, width=base_width)
        draw.ellipse([int(x-2*scale), int(y-10*scale), int(x+2*scale), int(y-6*scale)], fill=color)
        draw.arc([int(x-4*scale), int(y-8*scale), int(x+4*scale), int(y+0*scale)], -120, 120, fill=color, width=base_width)

def generate_astrological_icon(filename="diamond_chart_icon.ico"):
    size = 256
    cx, cy = size // 2, size // 2
    
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # --- 1. Soft Divine Background Gradient ---

    # --- Divine Palette ---
    pure_gold = (212, 175, 55, 255)       
    halo_gold = (255, 223, 100, 180)      
    ethereal_cyan = (150, 230, 255, 200)  
    crimson_red = (220, 60, 80, 200)       # Functional red color for details

    # --- 2. Diamond Chart Geometry Setup ---
    margin = 32
    W = size - 2 * margin # Inner width
    
    top_left = (margin, margin)
    top_right = (size - margin, margin)
    bottom_right = (size - margin, size - margin)
    bottom_left = (margin, size - margin)
    
    mid_top = (cx, margin)
    mid_right = (size - margin, cy)
    mid_bottom = (cx, size - margin)
    mid_left = (margin, cy)

    d_margin = margin + 8
    dtl, dtr = (d_margin, d_margin), (size - d_margin, d_margin)
    dbr, dbl = (size - d_margin, size - d_margin), (d_margin, size - d_margin)
    
    # --- 3. Drawing the Double-Lined Grid ---
    draw.polygon([top_left, top_right, bottom_right, bottom_left], outline=pure_gold, width=3)
    draw.polygon([dtl, dtr, dbr, dbl], outline=pure_gold, width=2)
    
    # REDUCED SOME ELEMENTS TO RED IN THE HOUSES
    # Making the diagonal crossing lines (which form house borders) red while leaving the main frame gold
    draw.line([top_left, bottom_right], fill=crimson_red, width=2)
    draw.line([top_right, bottom_left], fill=crimson_red, width=2)
    draw.line([dtl, dbr], fill=crimson_red, width=1)
    draw.line([dtr, dbl], fill=crimson_red, width=1)
    
    draw.polygon([mid_top, mid_right, mid_bottom, mid_left], outline=pure_gold, width=3)
    draw.polygon([(cx, d_margin), (size - d_margin, cy), (cx, size - d_margin), (d_margin, cy)], outline=pure_gold, width=2)

    # --- 4. Advanced Geometric Central Star ---
    star_radius_outer = 32
    star_radius_inner = 12

    # Draw 8 individual alternating kites (blades)
    for i in range(8):
        angle = math.radians(i * 45 - 90) 
        angle_next_inner = math.radians(i * 45 - 90 + 22.5)
        angle_prev_inner = math.radians(i * 45 - 90 - 22.5)
        
        blade_fill = halo_gold if i % 2 == 0 else ethereal_cyan
        blade_outline = pure_gold
        
        tip_x = cx + star_radius_outer * math.cos(angle)
        tip_y = cy + star_radius_outer * math.sin(angle)
        
        in_r_x = cx + star_radius_inner * math.cos(angle_next_inner)
        in_r_y = cy + star_radius_inner * math.sin(angle_next_inner)
        
        in_l_x = cx + star_radius_inner * math.cos(angle_prev_inner)
        in_l_y = cy + star_radius_inner * math.sin(angle_prev_inner)
        
        kite_points = [(cx, cy), (in_l_x, in_l_y), (tip_x, tip_y), (in_r_x, in_r_y)]
        draw.polygon(kite_points, fill=blade_fill, outline=blade_outline, width=1)
        
        draw.line([(cx, cy), (tip_x, tip_y)], fill=(255, 255, 255, 120), width=1)
        
        # Red node details
        node_x = cx + (star_radius_outer * 0.7) * math.cos(angle)
        node_y = cy + (star_radius_outer * 0.7) * math.sin(angle)
        draw.ellipse([node_x-2, node_y-2, node_x+2, node_y+2], fill=crimson_red)

    # --- REINTRODUCED DOUBLE-LINED CIRCULAR ELEMENT (Elegant & Colorful) ---
    # Placed right around the star to beautifully frame the center
    draw.ellipse([cx-42, cy-42, cx+42, cy+42], outline=ethereal_cyan, width=2)
    draw.ellipse([cx-47, cy-47, cx+47, cy+47], outline=crimson_red, width=2)

    # Multi-layered glowing core
    draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=(255, 255, 255, 220), outline=crimson_red, width=2)
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=pure_gold)
    draw.ellipse([cx-1, cy-1, cx+1, cy+1], fill=(255, 255, 255, 255))
    
    # --- 5. Precise Planet Placement (Geometric Centroids) ---
    U = W / 4 
    tri_offset = 1.66 * U 
    
    sym_positions = [
        # Center houses, replacing some with crimson_red to fulfill "elements in house themselves are red"
        ('sun',     (cx, cy - U), crimson_red),        # H1 - Top (Red)
        ('moon',    (cx - U, cy), ethereal_cyan),      # H4 - Left
        ('jupiter', (cx, cy + U), halo_gold),          # H7 - Bottom
        ('saturn',  (cx + U, cy), pure_gold),          # H10 - Right
        
        # Triangles 
        ('mercury', (cx - U, cy - tri_offset), halo_gold),         # H2
        ('venus',   (cx - tri_offset, cy - U), pure_gold),         # H3 
        ('mars',    (cx - tri_offset, cy + U), crimson_red),       # H5 (Red)
        ('uranus',  (cx - U, cy + tri_offset), pure_gold),         # H6 
        ('neptune', (cx + tri_offset, cy + U), ethereal_cyan),     # H9 
        ('pluto',   (cx + tri_offset, cy - U), halo_gold),         # H11 
    ]

    sym_scale = 0.8 

    for sym_name, sym_pos, sym_color in sym_positions:
        sym_halo_color = list(sym_color)
        sym_halo_color[3] = 100 
        sym_halo_color = tuple(sym_halo_color)
        
        draw_planet_symbol(draw, sym_pos[0], sym_pos[1], sym_name, sym_halo_color, scale=sym_scale*1.15) 
        draw_planet_symbol(draw, sym_pos[0], sym_pos[1], sym_name, sym_color, scale=sym_scale) 

    # --- 6. Final Enhancing and Glow Effects ---
    heavy_glow = img.filter(ImageFilter.GaussianBlur(radius=6))
    soft_glow = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    blended = Image.blend(img.convert("RGBA"), soft_glow.convert("RGBA"), alpha=0.35)
    heavy_glow.putalpha(heavy_glow.split()[3].point(lambda p: p * 0.3))
    final_img = Image.alpha_composite(blended, heavy_glow)

    # --- 7. Save as ICO ---
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    try:
        final_img.save(filename, format='ICO', sizes=icon_sizes)
        print(f"Successfully generated precision diamond chart icon with red details: {filename}")
    except Exception as e:
        print(f"Error saving icon: {e}")

if __name__ == "__main__":
    try:
        import PIL
    except ImportError:
        print("Error: The 'Pillow' library is required to run this script.")
        print("Please install it using: pip install Pillow")
        exit(1)
        
    print("Generating precision geometric diamond chart icon with retained central star, circular double rings, and red details...")
    generate_astrological_icon()