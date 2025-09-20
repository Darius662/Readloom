#!/usr/bin/env python3

with open('frontend/api_metadata.py', 'r') as f:
    content = f.read()

# Replace the problematic line
fixed_content = content.replace("@metadata_api_bp.route('/providers/<n>", "@metadata_api_bp.route('/providers/<name>")

with open('frontend/api_metadata.py', 'w') as f:
    f.write(fixed_content)

print("Fixed parameter name mismatch in api_metadata.py")
