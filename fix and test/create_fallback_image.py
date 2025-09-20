#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create a fallback 'no-cover.png' image.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_no_cover_image(output_path, width=200, height=300):
    """
    Create a simple 'No Cover Available' placeholder image.
    
    Args:
        output_path: Path to save the image.
        width: Image width in pixels.
        height: Image height in pixels.
    """
    # Create a new image with white background
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a border
    border_color = (200, 200, 200)
    border_width = 2
    draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=border_width)
    
    # Draw a book icon (simplified)
    icon_color = (150, 150, 150)
    margin = 30
    # Book cover
    draw.rectangle([margin, margin, width-margin, height-margin], outline=icon_color, width=2)
    # Book spine
    draw.line([(margin, margin), (margin+20, margin+10)], fill=icon_color, width=2)
    draw.line([(margin, height-margin), (margin+20, height-margin-10)], fill=icon_color, width=2)
    draw.line([(margin+20, margin+10), (margin+20, height-margin-10)], fill=icon_color, width=2)
    
    # Add text
    try:
        # Try to load a font, fall back to default if not available
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    text = "No Cover"
    text_width = draw.textlength(text, font=font)
    text_position = ((width - text_width) / 2, height - 70)
    draw.text(text_position, text, font=font, fill=(100, 100, 100))
    
    # Save the image
    img.save(output_path)
    
    print(f"Created fallback image: {output_path}")
    print(f"Size: {os.path.getsize(output_path)} bytes")

if __name__ == "__main__":
    output_dir = "frontend/static/img"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "no-cover.png")
    create_no_cover_image(output_path)
