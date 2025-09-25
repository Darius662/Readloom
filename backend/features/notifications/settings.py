#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notification settings management.
"""

from typing import Dict, Optional

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


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
        email_enabled: Whether email notifications are enabled.
        email_address: The email address to send notifications to.
        browser_enabled: Whether browser notifications are enabled.
        discord_enabled: Whether Discord notifications are enabled.
        discord_webhook: The Discord webhook URL.
        telegram_enabled: Whether Telegram notifications are enabled.
        telegram_bot_token: The Telegram bot token.
        telegram_chat_id: The Telegram chat ID.
        notify_new_volumes: Whether to notify for new volumes.
        notify_new_chapters: Whether to notify for new chapters.
        notify_releases_days_before: How many days before release to notify.
        
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
