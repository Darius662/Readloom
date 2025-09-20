#!/usr/bin/env python3

import re

def fix_route():
    """Fix the route parameter in api_metadata.py."""
    file_path = 'frontend/api_metadata.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Use regex to find and replace the route
    pattern = r"@metadata_api_bp\.route\('/providers/<n>'"
    replacement = r"@metadata_api_bp.route('/providers/<name>'"
    
    new_content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("Route parameter fixed!")

if __name__ == "__main__":
    fix_route()
