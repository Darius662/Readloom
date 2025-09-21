#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notification management functions.
"""

from typing import Dict, List, Optional

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from .settings import get_notification_settings
from .channels import send_email_notification, send_discord_notification, send_telegram_notification


def create_notification(title: str, message: str, type: str = 'INFO') -> int:
    """Create a new notification.
    
    Args:
        title: The notification title.
        message: The notification message.
        type: The notification type. Defaults to 'INFO'.
        
    Returns:
        int: The ID of the created notification.
    """
    try:
        notification_id = execute_query("""
        INSERT INTO notifications (title, message, type)
        VALUES (?, ?, ?)
        """, (title, message, type), commit=True)
        
        return notification_id
    
    except Exception as e:
        LOGGER.error(f"Error creating notification: {e}")
        raise


def get_notifications(limit: int = 50, unread_only: bool = False) -> List[Dict]:
    """Get notifications.
    
    Args:
        limit: The maximum number of notifications to return. Defaults to 50.
        unread_only: Whether to only return unread notifications. Defaults to False.
        
    Returns:
        List[Dict]: The notifications.
    """
    try:
        query = """
        SELECT id, title, message, type, read, created_at
        FROM notifications
        """
        
        if unread_only:
            query += " WHERE read = 0"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        
        return execute_query(query, (limit,))
    
    except Exception as e:
        LOGGER.error(f"Error getting notifications: {e}")
        return []


def mark_notification_as_read(notification_id: int) -> bool:
    """Mark a notification as read.
    
    Args:
        notification_id: The notification ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        execute_query("""
        UPDATE notifications
        SET read = 1
        WHERE id = ?
        """, (notification_id,), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error marking notification as read: {e}")
        return False


def mark_all_notifications_as_read() -> bool:
    """Mark all notifications as read.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        execute_query("""
        UPDATE notifications
        SET read = 1
        """, commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error marking all notifications as read: {e}")
        return False


def delete_notification(notification_id: int) -> bool:
    """Delete a notification.
    
    Args:
        notification_id: The notification ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        execute_query("""
        DELETE FROM notifications
        WHERE id = ?
        """, (notification_id,), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error deleting notification: {e}")
        return False


def delete_all_notifications() -> bool:
    """Delete all notifications.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        execute_query("""
        DELETE FROM notifications
        """, commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error deleting all notifications: {e}")
        return False


def send_notification(title: str, message: str, type: str = 'INFO') -> bool:
    """Send a notification through all enabled channels.
    
    Args:
        title: The notification title.
        message: The notification message.
        type: The notification type. Defaults to 'INFO'.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Create in-app notification
        create_notification(title, message, type)
        
        # Get notification settings
        settings = get_notification_settings()
        
        # Send browser notification
        if settings.get('browser_enabled'):
            # Browser notifications are handled by the frontend
            pass
        
        # Send email notification
        if settings.get('email_enabled') and settings.get('email_address'):
            try:
                send_email_notification(
                    settings.get('email_address'),
                    title,
                    message
                )
            except Exception as e:
                LOGGER.error(f"Error sending email notification: {e}")
        
        # Send Discord notification
        if settings.get('discord_enabled') and settings.get('discord_webhook'):
            try:
                send_discord_notification(
                    settings.get('discord_webhook'),
                    title,
                    message,
                    type
                )
            except Exception as e:
                LOGGER.error(f"Error sending Discord notification: {e}")
        
        # Send Telegram notification
        if settings.get('telegram_enabled') and settings.get('telegram_bot_token') and settings.get('telegram_chat_id'):
            try:
                send_telegram_notification(
                    settings.get('telegram_bot_token'),
                    settings.get('telegram_chat_id'),
                    title,
                    message
                )
            except Exception as e:
                LOGGER.error(f"Error sending Telegram notification: {e}")
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error sending notification: {e}")
        return False
