#!/usr/bin/env python3

import os
import fileinput
import sys

def fix_api_metadata():
    """Fix the route parameter mismatch in api_metadata.py."""
    file_path = os.path.join('frontend', 'api_metadata.py')
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the route parameter
        fixed_content = content.replace(
            "@metadata_api_bp.route('/providers/<n>', methods=['PUT'])",
            "@metadata_api_bp.route('/providers/<name>', methods=['PUT'])"
        )
        
        # Write the fixed content back to the file
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"Successfully fixed route parameter in {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing api_metadata.py: {e}")
        return False

if __name__ == "__main__":
    fix_api_metadata()
