#!/usr/bin/env python3

import sys
from backend.features.metadata_service import init_metadata_service, search_manga

def main():
    print("Initializing metadata service...")
    try:
        init_metadata_service()
        print("Metadata service initialized successfully!")
        
        print("\nTesting search functionality...")
        results = search_manga("One Piece", None, 1)
        print(f"Search results: {results}")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
