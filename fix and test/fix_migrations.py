#!/usr/bin/env python3
"""
Mark old migrations as applied so only new ones run.
"""

import sys
sys.path.insert(0, '.')

from backend.internals.db import set_db_location, execute_query

set_db_location('data')

# Create migrations table
execute_query("""
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_file TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(migration_file)
)
""", commit=True)

# Mark old migrations as applied (skip them)
old_migrations = [
    '0004_add_confirmed_release_flags.py',
    '0005_add_series_tracking.py',
    '0006_add_notification_system.py',
    '0007_add_collection_stats.py'
]

for migration in old_migrations:
    execute_query(
        "INSERT OR IGNORE INTO migrations (migration_file) VALUES (?)",
        (migration,),
        commit=True
    )
    print(f"Marked {migration} as applied")

print("\n✓ Old migrations marked as applied")
print("Now only migration 0008 will run")
print("\nRestart the app: python Readloom_direct.py")
