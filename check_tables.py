#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from backend.internals.db import set_db_location, execute_query

set_db_location('data')

# Get all tables
tables = execute_query('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
print("\nDatabase Tables:")
print("="*60)
for table in tables:
    print(f"  - {table['name']}")

# Check if manga_volume_cache exists
if any(t['name'] == 'manga_volume_cache' for t in tables):
    print("\n✓ manga_volume_cache table EXISTS")
    
    # Show schema
    schema = execute_query('PRAGMA table_info(manga_volume_cache)')
    print("\nSchema:")
    for col in schema:
        print(f"  - {col['name']}: {col['type']}")
    
    # Show count
    count = execute_query('SELECT COUNT(*) as count FROM manga_volume_cache')[0]['count']
    print(f"\nCached entries: {count}")
else:
    print("\n✗ manga_volume_cache table DOES NOT EXIST")
    print("  Migration may not have run. Let's run it manually...")
    
    from backend.internals.migrations import run_migrations
    run_migrations()
    print("\n  Migration complete! Check again.")
