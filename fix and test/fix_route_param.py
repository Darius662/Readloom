#!/usr/bin/env python3

def fix_route_parameter():
    """Fix the route parameter in the API endpoint for updating providers."""
    file_path = 'frontend/api_metadata.py'
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the route parameter
    # Using a more flexible approach that doesn't require exact string matching
    modified_content = content.replace("'/providers/<n>'", "'/providers/<name>'")
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Route parameter fixed!")

if __name__ == "__main__":
    fix_route_parameter()
