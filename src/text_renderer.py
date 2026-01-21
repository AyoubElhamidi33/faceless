import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

def create_text_clip(text, fontsize=70, font="Arial", color="white", stroke_color="black", stroke_width=3, size=None, duration=None):
    """
    Creates a MoviePy ImageClip containing text rendered via Pillow.
    Bypasses ImageMagick dependency.
    """
    
    # 1. Estimate Size if not provided
    if size is None:
        size = (1080, 200) # Default strip width
        
    width, height = size
    if height is None: height = fontsize * 2 # auto height estimate

    # 2. Create PIL Image
    img = Image.new('RGBA', (int(width), int(height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 3. Load Font
    try:
        # Try common windows fonts
        font_obj = ImageFont.truetype("arial.ttf", fontsize)
    except IOError:
        try:
             font_obj = ImageFont.truetype("seguiemj.ttf", fontsize) # Windows default
        except:
             font_obj = ImageFont.load_default()

    # 4. Draw Stroke (Simple simulation)
    x, y = width / 2, height / 2
    
    # Get Text Size for centering
    try:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font_obj)
        w = right - left
        h = bottom - top
    except:
        w, h = draw.textsize(text, font=font_obj) # Deprecated fallback

    # Recenter based on text size
    # Draw at center of image
    x_pos = (width - w) / 2
    y_pos = (height - h) / 2
    
    # Stroke simulation (Draw 8 times around)
    if stroke_width > 0:
        for offset_x in range(-stroke_width, stroke_width + 1):
            for offset_y in range(-stroke_width, stroke_width + 1):
                draw.text((x_pos + offset_x, y_pos + offset_y), text, font=font_obj, fill=stroke_color)

    # Main Text
    draw.text((x_pos, y_pos), text, font=font_obj, fill=color)
    
    # 5. Convert to Numpy for MoviePy
    img_np = np.array(img)
    
    # 6. Create Clip
    clip = ImageClip(img_np, transparent=True)
    
    if duration:
        clip = clip.set_duration(duration)
        
    return clip
