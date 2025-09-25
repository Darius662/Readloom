#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from datetime import datetime

def get_safe_folder_name(name):
    """Create a safe folder name from a string."""
    # Replace spaces with underscores and remove invalid characters
    safe_name = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in name)
    safe_name = safe_name.replace(' ', '_')
    
    # Ensure the name is not empty
    if not safe_name:
        safe_name = "unnamed"
    
    return safe_name

def create_series_folder(series_title, content_type="MANGA", series_id=1):
    """Create folder structure for a series."""
    # Create safe directory name
    safe_series_title = get_safe_folder_name(series_title)
    print(f"Safe series title: {safe_series_title}")
    
    # Organize by content type and series title
    data_dir = Path("data")
    ebook_dir = data_dir / "ebooks"
    print(f"E-book directory: {ebook_dir}")
    
    content_type_dir = ebook_dir / content_type
    print(f"Content type directory: {content_type_dir}")
    
    # Create content type directory if it doesn't exist
    os.makedirs(content_type_dir, exist_ok=True)
    print(f"Ensured content type directory exists: {content_type_dir}")
    
    series_dir = content_type_dir / safe_series_title
    print(f"Series directory: {series_dir}")
    
    # Create series directory
    os.makedirs(series_dir, exist_ok=True)
    print(f"Ensured series directory exists: {series_dir}")
    
    # Create a README file with series information
    readme_path = series_dir / "README.txt"
    print(f"README path: {readme_path}")
    
    if not readme_path.exists():
        try:
            with open(readme_path, 'w') as f:
                f.write(f"Series: {series_title}\n")
                f.write(f"ID: {series_id}\n")
                f.write(f"Type: {content_type}\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\nThis folder is managed by Readlook. Place your e-book files here.\n")
            print(f"Created README file: {readme_path}")
        except Exception as e:
            print(f"Error creating README file: {e}")
    
    return series_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_series_folder.py <series_title> [content_type]")
        sys.exit(1)
    
    series_title = sys.argv[1]
    content_type = sys.argv[2] if len(sys.argv) > 2 else "MANGA"
    
    series_dir = create_series_folder(series_title, content_type)
    print(f"Series folder created at: {series_dir}")
