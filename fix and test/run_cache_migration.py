#!/usr/bin/env python3
import sys
import importlib
sys.path.insert(0, '.')

from backend.internals.db import set_db_location

print("Running manga_volume_cache migration...")
set_db_location('data')

try:
    # Import the migration module
    migration_module = importlib.import_module('backend.migrations.0008_add_manga_volume_cache')
    migration_module.migrate()
    print("✓ Migration completed successfully!")
except Exception as e:
    print(f"✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
