#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection mutation functions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from .stats import update_collection_stats


def add_to_collection(
    series_id: int,
    item_type: str,
    volume_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    ownership_status: str = 'OWNED',
    read_status: str = 'UNREAD',
    format: str = 'PHYSICAL',
    condition: str = 'NONE',
    purchase_date: Optional[str] = None,
    purchase_price: Optional[float] = None,
    purchase_location: Optional[str] = None,
    notes: Optional[str] = None,
    custom_tags: Optional[str] = None
) -> int:
    """Add an item to the collection.
    
    Args:
        series_id: The series ID.
        item_type: The item type (SERIES, VOLUME, CHAPTER).
        volume_id: The volume ID.
        chapter_id: The chapter ID.
        ownership_status: The ownership status.
        read_status: The read status.
        format: The format.
        condition: The condition.
        purchase_date: The purchase date.
        purchase_price: The purchase price.
        purchase_location: The purchase location.
        notes: Notes about the item.
        custom_tags: Custom tags.
        
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
                ownership_status, read_status, format, condition,
                purchase_date, purchase_price, purchase_location,
                notes, custom_tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            item_id = execute_query(insert_query, (
                series_id,
                volume_id,
                chapter_id,
                item_type,
                ownership_status,
                read_status,
                format,
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
        item_id: The collection item ID.
        
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
    condition: Optional[str] = None,
    purchase_date: Optional[str] = None,
    purchase_price: Optional[float] = None,
    purchase_location: Optional[str] = None,
    notes: Optional[str] = None,
    custom_tags: Optional[str] = None
) -> bool:
    """Update a collection item.
    
    Args:
        item_id: The collection item ID.
        ownership_status: The ownership status.
        read_status: The read status.
        format: The format.
        condition: The condition.
        purchase_date: The purchase date.
        purchase_price: The purchase price.
        purchase_location: The purchase location.
        notes: Notes about the item.
        custom_tags: Custom tags.
        
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


def import_collection(data: List[Dict]) -> Dict:
    """Import collection data.
    
    Args:
        data: The collection data to import.
        
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
