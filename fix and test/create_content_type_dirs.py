#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Get the data directory
data_dir = Path("data")
ebook_dir = data_dir / "ebooks"

# Create content type directories
content_types = ["MANGA", "MANHWA", "MANHUA", "COMICS", "NOVEL", "BOOK", "OTHER"]

for content_type in content_types:
    content_type_dir = ebook_dir / content_type
    os.makedirs(content_type_dir, exist_ok=True)
    print(f"Created directory: {content_type_dir}")

print("Content type directories created successfully!")
