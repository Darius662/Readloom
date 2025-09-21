#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Schema setup for notifications.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def setup_notifications_tables():
    """Set up the notifications tables if they don't exist."""
    try:
        # Create notifications table
        execute_query("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('INFO', 'WARNING', 'ERROR', 'SUCCESS')),
            read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """, commit=True)
        
        # Create subscriptions table
        execute_query("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            notify_new_volumes INTEGER DEFAULT 1,
            notify_new_chapters INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
            UNIQUE(series_id)
        )
        """, commit=True)
        
        # Create notification_settings table
        execute_query("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_enabled INTEGER DEFAULT 0,
            email_address TEXT,
            browser_enabled INTEGER DEFAULT 1,
            discord_enabled INTEGER DEFAULT 0,
            discord_webhook TEXT,
            telegram_enabled INTEGER DEFAULT 0,
            telegram_bot_token TEXT,
            telegram_chat_id TEXT,
            notify_new_volumes INTEGER DEFAULT 1,
            notify_new_chapters INTEGER DEFAULT 1,
            notify_releases_days_before INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """, commit=True)
        
        # Insert default notification settings if they don't exist
        execute_query("""
        INSERT OR IGNORE INTO notification_settings (id) VALUES (1)
        """, commit=True)
        
        LOGGER.info("Notification tables set up successfully")
    except Exception as e:
        LOGGER.error(f"Error setting up notification tables: {e}")
        raise
