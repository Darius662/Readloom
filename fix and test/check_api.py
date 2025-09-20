#!/usr/bin/env python3

from frontend.api_metadata import metadata_api_bp

# Print blueprint info
print(f"Blueprint name: {metadata_api_bp.name}")
print(f"Blueprint url_prefix: {metadata_api_bp.url_prefix}")

# Check the routes
print("\nRoutes:")
for rule in metadata_api_bp.url_map._rules:
    print(f"  {rule.rule} -> {rule.endpoint}")

# Check the update_provider route specifically
print("\nChecking update_provider route:")
for rule in metadata_api_bp.url_map._rules:
    if "providers" in rule.rule and "PUT" in rule.methods:
        print(f"  Route: {rule.rule}")
        print(f"  Methods: {rule.methods}")
        print(f"  Endpoint: {rule.endpoint}")
