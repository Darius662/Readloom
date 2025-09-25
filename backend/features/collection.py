#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Dict, List, Optional, Union

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def setup_collection_tables():
    """Set up the collection tracking tables if they don't exist."""
    try:
        # Create collection items table
        execute_query("""
        CREATE TABLE IF NOT EXISTS collection_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            volume_id INTEGER NULL,
            chapter_id INTEGER NULL,
            item_type TEXT NOT NULL CHECK(item_type IN ('SERIES', 'VOLUME', 'CHAPTER')),
            ownership_status TEXT NOT NULL CHECK(ownership_status IN ('OWNED', 'WANTED', 'ORDERED', 'LOANED', 'NONE')),
            read_status TEXT NOT NULL CHECK(read_status IN ('READ', 'READING', 'UNREAD', 'NONE')),
            format TEXT CHECK(format IN ('PHYSICAL', 'DIGITAL', 'BOTH', 'NONE')),
            digital_format TEXT CHECK(digital_format IN ('PDF', 'EPUB', 'CBZ', 'CBR', 'MOBI', 'AZW', 'NONE')),
            has_file INTEGER DEFAULT 0,
            ebook_file_id INTEGER,
            condition TEXT CHECK(condition IN ('NEW', 'LIKE_NEW', 'VERY_GOOD', 'GOOD', 'FAIR', 'POOR', 'NONE')),
            purchase_date TEXT,
            purchase_price REAL,
            purchase_location TEXT,
            notes TEXT,
            custom_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
            FOREIGN KEY (volume_id) REFERENCES volumes(id) ON DELETE CASCADE,
            FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
            FOREIGN KEY (ebook_file_id) REFERENCES ebook_files(id) ON DELETE SET NULL
        )
        """, commit=True)
        
        # Create collection stats table
        execute_query("""
        CREATE TABLE IF NOT EXISTS collection_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            total_series INTEGER DEFAULT 0,
            total_volumes INTEGER DEFAULT 0,
            total_chapters INTEGER DEFAULT 0,
            owned_series INTEGER DEFAULT 0,
            owned_volumes INTEGER DEFAULT 0,
            owned_chapters INTEGER DEFAULT 0,
            read_volumes INTEGER DEFAULT 0,
            read_chapters INTEGER DEFAULT 0,
            total_value REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
        """, commit=True)
        
        # Insert default stats record if it doesn't exist
        execute_query("""
        INSERT OR IGNORE INTO collection_stats (user_id) VALUES (1)
        """, commit=True)
        
        LOGGER.info("Collection tracking tables set up successfully")
    except Exception as e:
        LOGGER.error(f"Error setting up collection tables: {e}")
        raise


def add_to_collection(
    series_id: int,
    item_type: str,
    volume_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    ownership_status: str = 'OWNED',
    read_status: str = 'UNREAD',
    format: str = 'PHYSICAL',
    digital_format: str = 'NONE',
    has_file: int = 0,
    ebook_file_id: Optional[int] = None,
    condition: str = 'NONE',
    purchase_date: Optional[str] = None,
    purchase_price: Optional[float] = None,
    purchase_location: Optional[str] = None,
    notes: Optional[str] = None,
    custom_tags: Optional[str] = None
) -> int:
    """Add an item to the collection.
    
    Args:
        series_id (int): The series ID.
        item_type (str): The item type (SERIES, VOLUME, CHAPTER).
        volume_id (Optional[int], optional): The volume ID. Defaults to None.
        chapter_id (Optional[int], optional): The chapter ID. Defaults to None.
        ownership_status (str, optional): The ownership status. Defaults to 'OWNED'.
        read_status (str, optional): The read status. Defaults to 'UNREAD'.
        format (str, optional): The format. Defaults to 'PHYSICAL'.
        condition (str, optional): The condition. Defaults to 'NONE'.
        purchase_date (Optional[str], optional): The purchase date. Defaults to None.
        purchase_price (Optional[float], optional): The purchase price. Defaults to None.
        purchase_location (Optional[str], optional): The purchase location. Defaults to None.
        notes (Optional[str], optional): Notes about the item. Defaults to None.
        custom_tags (Optional[str], optional): Custom tags. Defaults to None.
        
    Returns:
        int: The ID of the created collection item.
    """
    try:
        # Check if item already exists in collection
        existing_query = """
        SELECT id FROM collection_items 
        WHERE series_id = ? AND item_type = ?
        """
        params = [series_id, item_type]
        
        if item_type == 'VOLUME' and volume_id:
            existing_query += " AND volume_id = ?"
            params.append(volume_id)
        elif item_type == 'CHAPTER' and chapter_id:
            existing_query += " AND chapter_id = ?"
            params.append(chapter_id)
            
        existing = execute_query(existing_query, tuple(params))
        
        if existing:
            # Update existing item
            update_query = """
            UPDATE collection_items SET
                ownership_status = ?,
                read_status = ?,
                format = ?,
                digital_format = ?,
                has_file = ?,
                ebook_file_id = ?,
                condition = ?,
                purchase_date = ?,
                purchase_price = ?,
                purchase_location = ?,
                notes = ?,
                custom_tags = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            execute_query(update_query, (
                ownership_status,
                read_status,
                format,
                digital_format,
                has_file,
                ebook_file_id,
                condition,
                purchase_date,
                purchase_price,
                purchase_location,
                notes,
                custom_tags,
                existing[0]['id']
            ), commit=True)
            
            item_id = existing[0]['id']
        else:
            # Insert new item
            insert_query = """
            INSERT INTO collection_items (
                series_id, volume_id, chapter_id, item_type,
                ownership_status, read_status, format, digital_format, has_file, ebook_file_id,
                condition, purchase_date, purchase_price, purchase_location,
                notes, custom_tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            item_id = execute_query(insert_query, (
                series_id,
                volume_id,
                chapter_id,
                item_type,
                ownership_status,
                read_status,
                format,
                digital_format,
                has_file,
                ebook_file_id,
                condition,
                purchase_date,
                purchase_price,
                purchase_location,
                notes,
                custom_tags
            ), commit=True)
        
        # Update collection stats
        update_collection_stats()
        
        return item_id
    
    except Exception as e:
        LOGGER.error(f"Error adding item to collection: {e}")
        raise


def remove_from_collection(item_id: int) -> bool:
    """Remove an item from the collection.
    
    Args:
        item_id (int): The collection item ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Check if item exists
        item = execute_query("SELECT id FROM collection_items WHERE id = ?", (item_id,))
        
        if not item:
            return False
        
        # Delete the item
        execute_query("DELETE FROM collection_items WHERE id = ?", (item_id,), commit=True)
        
        # Update collection stats
        update_collection_stats()
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error removing item from collection: {e}")
        return False


def update_collection_item(
    item_id: int,
    ownership_status: Optional[str] = None,
    read_status: Optional[str] = None,
    format: Optional[str] = None,
    digital_format: Optional[str] = None,
    has_file: Optional[int] = None,
    ebook_file_id: Optional[int] = None,
    condition: Optional[str] = None,
    purchase_date: Optional[str] = None,
    purchase_price: Optional[float] = None,
    purchase_location: Optional[str] = None,
    notes: Optional[str] = None,
    custom_tags: Optional[str] = None
) -> bool:
    """Update a collection item.
    
    Args:
        item_id (int): The collection item ID.
        ownership_status (Optional[str], optional): The ownership status. Defaults to None.
        read_status (Optional[str], optional): The read status. Defaults to None.
        format (Optional[str], optional): The format. Defaults to None.
        condition (Optional[str], optional): The condition. Defaults to None.
        purchase_date (Optional[str], optional): The purchase date. Defaults to None.
        purchase_price (Optional[float], optional): The purchase price. Defaults to None.
        purchase_location (Optional[str], optional): The purchase location. Defaults to None.
        notes (Optional[str], optional): Notes about the item. Defaults to None.
        custom_tags (Optional[str], optional): Custom tags. Defaults to None.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Check if item exists
        item = execute_query("SELECT id FROM collection_items WHERE id = ?", (item_id,))
        
        if not item:
            return False
        
        # Build update query
        update_fields = []
        params = []
        
        if ownership_status is not None:
            update_fields.append("ownership_status = ?")
            params.append(ownership_status)
        
        if read_status is not None:
            update_fields.append("read_status = ?")
            params.append(read_status)
        
        if format is not None:
            update_fields.append("format = ?")
            params.append(format)
        
        if digital_format is not None:
            update_fields.append("digital_format = ?")
            params.append(digital_format)
            
        if has_file is not None:
            update_fields.append("has_file = ?")
            params.append(has_file)
            
        if ebook_file_id is not None:
            update_fields.append("ebook_file_id = ?")
            params.append(ebook_file_id)
        
        if condition is not None:
            update_fields.append("condition = ?")
            params.append(condition)
        
        if purchase_date is not None:
            update_fields.append("purchase_date = ?")
            params.append(purchase_date)
        
        if purchase_price is not None:
            update_fields.append("purchase_price = ?")
            params.append(purchase_price)
        
        if purchase_location is not None:
            update_fields.append("purchase_location = ?")
            params.append(purchase_location)
        
        if notes is not None:
            update_fields.append("notes = ?")
            params.append(notes)
        
        if custom_tags is not None:
            update_fields.append("custom_tags = ?")
            params.append(custom_tags)
        
        if not update_fields:
            return True  # Nothing to update
        
        # Add updated_at and item_id
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(item_id)
        
        # Execute update
        execute_query(f"""
        UPDATE collection_items
        SET {", ".join(update_fields)}
        WHERE id = ?
        """, tuple(params), commit=True)
        
        # Update collection stats if ownership or read status changed
        if ownership_status is not None or read_status is not None:
            update_collection_stats()
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating collection item: {e}")
        return False


def get_collection_items(
    series_id: Optional[int] = None,
    item_type: Optional[str] = None,
    ownership_status: Optional[str] = None,
    read_status: Optional[str] = None,
    format: Optional[str] = None
) -> List[Dict]:
    """Get collection items with optional filters.
    
    Args:
        series_id (Optional[int], optional): Filter by series ID. Defaults to None.
        item_type (Optional[str], optional): Filter by item type. Defaults to None.
        ownership_status (Optional[str], optional): Filter by ownership status. Defaults to None.
        read_status (Optional[str], optional): Filter by read status. Defaults to None.
        format (Optional[str], optional): Filter by format. Defaults to None.
        
    Returns:
        List[Dict]: The collection items.
    """
    try:
        query = """
        SELECT 
            ci.*,
            s.title as series_title, s.author as series_author, s.cover_url as series_cover_url,
            v.volume_number, v.title as volume_title,
            c.chapter_number, c.title as chapter_title
        FROM collection_items ci
        LEFT JOIN series s ON ci.series_id = s.id
        LEFT JOIN volumes v ON ci.volume_id = v.id
        LEFT JOIN chapters c ON ci.chapter_id = c.id
        WHERE 1=1
        """
        params = []
        
        if series_id:
            query += " AND ci.series_id = ?"
            params.append(series_id)
        
        if item_type:
            query += " AND ci.item_type = ?"
            params.append(item_type)
        
        if ownership_status:
            query += " AND ci.ownership_status = ?"
            params.append(ownership_status)
        
        if read_status:
            query += " AND ci.read_status = ?"
            params.append(read_status)
        
        if format:
            query += " AND ci.format = ?"
            params.append(format)
        
        query += " ORDER BY s.title, v.volume_number, c.chapter_number"
        
        return execute_query(query, tuple(params))
    
    except Exception as e:
        LOGGER.error(f"Error getting collection items: {e}")
        return []


def get_collection_stats() -> Dict:
    """Get collection statistics.
    
    Returns:
        Dict: The collection statistics.
    """
    try:
        stats = execute_query("SELECT * FROM collection_stats WHERE user_id = 1")
        
        if stats:
            return stats[0]
        
        return {}
    
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return {}


def update_collection_stats() -> bool:
    """Update collection statistics.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Count total series, volumes, and chapters
        total_series = execute_query("""
        SELECT COUNT(DISTINCT series_id) as count
        FROM collection_items
        """)
        
        total_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME'
        """)
        
        total_chapters = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'CHAPTER'
        """)
        
        # Count owned series, volumes, and chapters
        owned_series = execute_query("""
        SELECT COUNT(DISTINCT series_id) as count
        FROM collection_items
        WHERE ownership_status = 'OWNED'
        """)
        
        owned_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND ownership_status = 'OWNED'
        """)
        
        owned_chapters = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'CHAPTER' AND ownership_status = 'OWNED'
        """)
        
        # Count read volumes and chapters
        read_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND read_status = 'READ'
        """)
        
        read_chapters = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'CHAPTER' AND read_status = 'READ'
        """)
        
        # Calculate total value
        total_value = execute_query("""
        SELECT SUM(purchase_price) as total
        FROM collection_items
        WHERE purchase_price IS NOT NULL
        """)
        
        # Update stats
        execute_query("""
        UPDATE collection_stats
        SET
            total_series = ?,
            total_volumes = ?,
            total_chapters = ?,
            owned_series = ?,
            owned_volumes = ?,
            owned_chapters = ?,
            read_volumes = ?,
            read_chapters = ?,
            total_value = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = 1
        """, (
            total_series[0]['count'] if total_series else 0,
            total_volumes[0]['count'] if total_volumes else 0,
            total_chapters[0]['count'] if total_chapters else 0,
            owned_series[0]['count'] if owned_series else 0,
            owned_volumes[0]['count'] if owned_volumes else 0,
            owned_chapters[0]['count'] if owned_chapters else 0,
            read_volumes[0]['count'] if read_volumes else 0,
            read_chapters[0]['count'] if read_chapters else 0,
            total_value[0]['total'] if total_value and total_value[0]['total'] else 0.0
        ), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating collection stats: {e}")
        return False


def import_collection(data: List[Dict]) -> Dict:
    """Import collection data.
    
    Args:
        data (List[Dict]): The collection data to import.
        
    Returns:
        Dict: Import statistics.
    """
    try:
        stats = {
            'total': len(data),
            'imported': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for item in data:
            try:
                # Check required fields
                if 'series_id' not in item or 'item_type' not in item:
                    stats['skipped'] += 1
                    continue
                
                # Add to collection
                add_to_collection(
                    series_id=item['series_id'],
                    item_type=item['item_type'],
                    volume_id=item.get('volume_id'),
                    chapter_id=item.get('chapter_id'),
                    ownership_status=item.get('ownership_status', 'OWNED'),
                    read_status=item.get('read_status', 'UNREAD'),
                    format=item.get('format', 'PHYSICAL'),
                    condition=item.get('condition', 'NONE'),
                    purchase_date=item.get('purchase_date'),
                    purchase_price=item.get('purchase_price'),
                    purchase_location=item.get('purchase_location'),
                    notes=item.get('notes'),
                    custom_tags=item.get('custom_tags')
                )
                
                stats['imported'] += 1
            
            except Exception:
                stats['errors'] += 1
        
        # Update collection stats
        update_collection_stats()
        
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error importing collection: {e}")
        raise


def export_collection() -> List[Dict]:
    """Export collection data.
    
    Returns:
        List[Dict]: The collection data.
    """
    try:
        return execute_query("""
        SELECT
            id, series_id, volume_id, chapter_id, item_type,
            ownership_status, read_status, format, condition,
            purchase_date, purchase_price, purchase_location,
            notes, custom_tags, created_at, updated_at
        FROM collection_items
        ORDER BY series_id, volume_id, chapter_id
        """)
    
    except Exception as e:
        LOGGER.error(f"Error exporting collection: {e}")
        return []
