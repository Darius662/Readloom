#!/usr/bin/env python3

# Script to fix the route parameter in api_metadata_fixed.py
with open('/home/darius/Documents/Git/Readloom/frontend/api_metadata_fixed.py', 'r') as f:
    content = f.read()

# Replace the route decorator
fixed_content = content.replace("@metadata_api_bp.route('/providers/<n>', methods=['PUT'])", 
                               "@metadata_api_bp.route('/providers/<name>', methods=['PUT'])")

# Write the fixed content back
with open('/home/darius/Documents/Git/Readloom/frontend/api_metadata_fixed.py', 'w') as f:
    f.write(fixed_content)

print("Route parameter fixed successfully.")
