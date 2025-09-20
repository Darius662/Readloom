#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

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


def create_notification(title: str, message: str, type: str = 'INFO') -> int:
    """Create a new notification.
    
    Args:
        title (str): The notification title.
        message (str): The notification message.
        type (str, optional): The notification type. Defaults to 'INFO'.
        
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
        limit (int, optional): The maximum number of notifications to return. Defaults to 50.
        unread_only (bool, optional): Whether to only return unread notifications. Defaults to False.
        
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
        notification_id (int): The notification ID.
        
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
        notification_id (int): The notification ID.
        
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


def subscribe_to_series(series_id: int, notify_new_volumes: bool = True, notify_new_chapters: bool = True) -> int:
    """Subscribe to a series.
    
    Args:
        series_id (int): The series ID.
        notify_new_volumes (bool, optional): Whether to notify for new volumes. Defaults to True.
        notify_new_chapters (bool, optional): Whether to notify for new chapters. Defaults to True.
        
    Returns:
        int: The ID of the created subscription.
    """
    try:
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            raise ValueError(f"Series with ID {series_id} not found")
        
        # Check if subscription already exists
        existing = execute_query("SELECT id FROM subscriptions WHERE series_id = ?", (series_id,))
        
        if existing:
            # Update existing subscription
            execute_query("""
            UPDATE subscriptions
            SET notify_new_volumes = ?, notify_new_chapters = ?
            WHERE series_id = ?
            """, (int(notify_new_volumes), int(notify_new_chapters), series_id), commit=True)
            
            return existing[0]['id']
        else:
            # Create new subscription
            subscription_id = execute_query("""
            INSERT INTO subscriptions (series_id, notify_new_volumes, notify_new_chapters)
            VALUES (?, ?, ?)
            """, (series_id, int(notify_new_volumes), int(notify_new_chapters)), commit=True)
            
            return subscription_id
    
    except Exception as e:
        LOGGER.error(f"Error subscribing to series: {e}")
        raise


def unsubscribe_from_series(series_id: int) -> bool:
    """Unsubscribe from a series.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        execute_query("""
        DELETE FROM subscriptions
        WHERE series_id = ?
        """, (series_id,), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error unsubscribing from series: {e}")
        return False


def get_subscriptions() -> List[Dict]:
    """Get all subscriptions.
    
    Returns:
        List[Dict]: The subscriptions.
    """
    try:
        return execute_query("""
        SELECT 
            s.id, s.series_id, s.notify_new_volumes, s.notify_new_chapters, s.created_at,
            series.title as series_title, series.author as series_author, series.cover_url as series_cover_url
        FROM subscriptions s
        JOIN series ON s.series_id = series.id
        ORDER BY series.title
        """)
    
    except Exception as e:
        LOGGER.error(f"Error getting subscriptions: {e}")
        return []


def is_subscribed(series_id: int) -> bool:
    """Check if a series is subscribed to.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        bool: True if subscribed, False otherwise.
    """
    try:
        result = execute_query("SELECT id FROM subscriptions WHERE series_id = ?", (series_id,))
        return len(result) > 0
    
    except Exception as e:
        LOGGER.error(f"Error checking subscription: {e}")
        return False


def get_notification_settings() -> Dict:
    """Get notification settings.
    
    Returns:
        Dict: The notification settings.
    """
    try:
        settings = execute_query("SELECT * FROM notification_settings WHERE id = 1")
        
        if settings:
            return settings[0]
        
        return {}
    
    except Exception as e:
        LOGGER.error(f"Error getting notification settings: {e}")
        return {}


def update_notification_settings(
    email_enabled: Optional[bool] = None,
    email_address: Optional[str] = None,
    browser_enabled: Optional[bool] = None,
    discord_enabled: Optional[bool] = None,
    discord_webhook: Optional[str] = None,
    telegram_enabled: Optional[bool] = None,
    telegram_bot_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
    notify_new_volumes: Optional[bool] = None,
    notify_new_chapters: Optional[bool] = None,
    notify_releases_days_before: Optional[int] = None
) -> bool:
    """Update notification settings.
    
    Args:
        email_enabled (Optional[bool], optional): Whether email notifications are enabled. Defaults to None.
        email_address (Optional[str], optional): The email address to send notifications to. Defaults to None.
        browser_enabled (Optional[bool], optional): Whether browser notifications are enabled. Defaults to None.
        discord_enabled (Optional[bool], optional): Whether Discord notifications are enabled. Defaults to None.
        discord_webhook (Optional[str], optional): The Discord webhook URL. Defaults to None.
        telegram_enabled (Optional[bool], optional): Whether Telegram notifications are enabled. Defaults to None.
        telegram_bot_token (Optional[str], optional): The Telegram bot token. Defaults to None.
        telegram_chat_id (Optional[str], optional): The Telegram chat ID. Defaults to None.
        notify_new_volumes (Optional[bool], optional): Whether to notify for new volumes. Defaults to None.
        notify_new_chapters (Optional[bool], optional): Whether to notify for new chapters. Defaults to None.
        notify_releases_days_before (Optional[int], optional): How many days before release to notify. Defaults to None.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Build update query
        update_fields = []
        params = []
        
        if email_enabled is not None:
            update_fields.append("email_enabled = ?")
            params.append(int(email_enabled))
        
        if email_address is not None:
            update_fields.append("email_address = ?")
            params.append(email_address)
        
        if browser_enabled is not None:
            update_fields.append("browser_enabled = ?")
            params.append(int(browser_enabled))
        
        if discord_enabled is not None:
            update_fields.append("discord_enabled = ?")
            params.append(int(discord_enabled))
        
        if discord_webhook is not None:
            update_fields.append("discord_webhook = ?")
            params.append(discord_webhook)
        
        if telegram_enabled is not None:
            update_fields.append("telegram_enabled = ?")
            params.append(int(telegram_enabled))
        
        if telegram_bot_token is not None:
            update_fields.append("telegram_bot_token = ?")
            params.append(telegram_bot_token)
        
        if telegram_chat_id is not None:
            update_fields.append("telegram_chat_id = ?")
            params.append(telegram_chat_id)
        
        if notify_new_volumes is not None:
            update_fields.append("notify_new_volumes = ?")
            params.append(int(notify_new_volumes))
        
        if notify_new_chapters is not None:
            update_fields.append("notify_new_chapters = ?")
            params.append(int(notify_new_chapters))
        
        if notify_releases_days_before is not None:
            update_fields.append("notify_releases_days_before = ?")
            params.append(notify_releases_days_before)
        
        if not update_fields:
            return True  # Nothing to update
        
        # Add updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Execute update
        execute_query(f"""
        UPDATE notification_settings
        SET {", ".join(update_fields)}
        WHERE id = 1
        """, tuple(params), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating notification settings: {e}")
        return False


def send_notification(title: str, message: str, type: str = 'INFO') -> bool:
    """Send a notification through all enabled channels.
    
    Args:
        title (str): The notification title.
        message (str): The notification message.
        type (str, optional): The notification type. Defaults to 'INFO'.
        
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
                _send_email_notification(
                    settings.get('email_address'),
                    title,
                    message
                )
            except Exception as e:
                LOGGER.error(f"Error sending email notification: {e}")
        
        # Send Discord notification
        if settings.get('discord_enabled') and settings.get('discord_webhook'):
            try:
                _send_discord_notification(
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
                _send_telegram_notification(
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


def _send_email_notification(email_address: str, title: str, message: str) -> bool:
    """Send an email notification.
    
    Args:
        email_address (str): The email address to send to.
        title (str): The notification title.
        message (str): The notification message.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    # This is a placeholder for actual email sending logic
    # In a real implementation, you would use a library like smtplib
    LOGGER.info(f"Email notification to {email_address}: {title} - {message}")
    return True


def _send_discord_notification(webhook_url: str, title: str, message: str, type: str) -> bool:
    """Send a Discord notification.
    
    Args:
        webhook_url (str): The Discord webhook URL.
        title (str): The notification title.
        message (str): The notification message.
        type (str): The notification type.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    # This is a placeholder for actual Discord webhook logic
    # In a real implementation, you would use requests to post to the webhook
    LOGGER.info(f"Discord notification: {title} - {message}")
    return True


def _send_telegram_notification(bot_token: str, chat_id: str, title: str, message: str) -> bool:
    """Send a Telegram notification.
    
    Args:
        bot_token (str): The Telegram bot token.
        chat_id (str): The Telegram chat ID.
        title (str): The notification title.
        message (str): The notification message.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    # This is a placeholder for actual Telegram API logic
    # In a real implementation, you would use requests to post to the Telegram API
    LOGGER.info(f"Telegram notification to {chat_id}: {title} - {message}")
    return True


def check_upcoming_releases() -> List[Dict]:
    """Check for upcoming releases and send notifications if needed.
    
    Returns:
        List[Dict]: The upcoming releases that were notified about.
    """
    try:
        settings = get_notification_settings()
        days_before = settings.get('notify_releases_days_before', 1)
        
        # Get date range
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days_before)).strftime('%Y-%m-%d')
        
        # Get subscribed series
        subscriptions = get_subscriptions()
        subscribed_series_ids = [sub['series_id'] for sub in subscriptions]
        
        if not subscribed_series_ids:
            return []
        
        # Get upcoming volume releases
        upcoming_volumes = []
        if settings.get('notify_new_volumes', True):
            volume_query = """
            SELECT 
                v.id, v.series_id, v.volume_number, v.title, v.release_date,
                s.title as series_title, s.author as series_author
            FROM volumes v
            JOIN series s ON v.series_id = s.id
            WHERE v.series_id IN ({}) AND v.release_date BETWEEN ? AND ?
            """.format(','.join('?' * len(subscribed_series_ids)))
            
            upcoming_volumes = execute_query(
                volume_query,
                tuple(subscribed_series_ids) + (today, future_date)
            )
        
        # Get upcoming chapter releases
        upcoming_chapters = []
        if settings.get('notify_new_chapters', True):
            chapter_query = """
            SELECT 
                c.id, c.series_id, c.volume_id, c.chapter_number, c.title, c.release_date,
                s.title as series_title, s.author as series_author
            FROM chapters c
            JOIN series s ON c.series_id = s.id
            WHERE c.series_id IN ({}) AND c.release_date BETWEEN ? AND ?
            """.format(','.join('?' * len(subscribed_series_ids)))
            
            upcoming_chapters = execute_query(
                chapter_query,
                tuple(subscribed_series_ids) + (today, future_date)
            )
        
        # Send notifications for upcoming releases
        notified_releases = []
        
        for volume in upcoming_volumes:
            # Check if this series subscription has volume notifications enabled
            for sub in subscriptions:
                if sub['series_id'] == volume['series_id'] and sub['notify_new_volumes']:
                    # Send notification
                    release_date = datetime.fromisoformat(volume['release_date']).strftime('%Y-%m-%d')
                    title = f"Upcoming Volume Release: {volume['series_title']}"
                    message = f"Volume {volume['volume_number']} of {volume['series_title']} will be released on {release_date}."
                    
                    send_notification(title, message, 'INFO')
                    notified_releases.append(volume)
                    break
        
        for chapter in upcoming_chapters:
            # Check if this series subscription has chapter notifications enabled
            for sub in subscriptions:
                if sub['series_id'] == chapter['series_id'] and sub['notify_new_chapters']:
                    # Send notification
                    release_date = datetime.fromisoformat(chapter['release_date']).strftime('%Y-%m-%d')
                    title = f"Upcoming Chapter Release: {chapter['series_title']}"
                    message = f"Chapter {chapter['chapter_number']} of {chapter['series_title']} will be released on {release_date}."
                    
                    send_notification(title, message, 'INFO')
                    notified_releases.append(chapter)
                    break
        
        return notified_releases
    
    except Exception as e:
        LOGGER.error(f"Error checking upcoming releases: {e}")
        return []
