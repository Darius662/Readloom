-- Fix collections table constraint issue
-- This script will recreate the collections table without the problematic constraint

-- First, create a backup of the collections table
CREATE TABLE IF NOT EXISTS collections_backup AS SELECT * FROM collections;

-- Drop the old table
DROP TABLE IF EXISTS collections;

-- Create the new table with correct constraints
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (is_default IN (0, 1))
);

-- Create a unique index to ensure only one default collection
CREATE UNIQUE INDEX idx_unique_default 
ON collections(is_default) WHERE is_default = 1;

-- Copy data from backup, ensuring only one default collection
INSERT INTO collections (id, name, description, is_default, created_at, updated_at)
SELECT 
    id, 
    name, 
    description, 
    CASE WHEN is_default = 1 AND rowid = (SELECT MIN(rowid) FROM collections_backup WHERE is_default = 1) THEN 1 ELSE 0 END as is_default,
    created_at, 
    updated_at
FROM collections_backup;

-- Fix the auto-increment sequence
UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM collections) WHERE name = 'collections';

-- Recreate any foreign key relationships
-- collection_root_folders table
CREATE TABLE IF NOT EXISTS collection_root_folders_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    root_folder_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, root_folder_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

INSERT INTO collection_root_folders_new
SELECT * FROM collection_root_folders;

DROP TABLE collection_root_folders;
ALTER TABLE collection_root_folders_new RENAME TO collection_root_folders;

-- series_collections table
CREATE TABLE IF NOT EXISTS series_collections_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series_id, collection_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

INSERT INTO series_collections_new
SELECT * FROM series_collections;

DROP TABLE series_collections;
ALTER TABLE series_collections_new RENAME TO series_collections;
