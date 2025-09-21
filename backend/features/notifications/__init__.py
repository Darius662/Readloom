#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notifications package for MangaArr.
"""

from .schema import setup_notifications_tables
from .notifications import (
    create_notification,
    get_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification,
    delete_all_notifications,
    send_notification,
)
from .subscriptions import (
    subscribe_to_series,
    unsubscribe_from_series,
    get_subscriptions,
    is_subscribed,
)
from .settings import (
    get_notification_settings,
    update_notification_settings,
)
from .releases import check_upcoming_releases

__all__ = [
    # Schema
    "setup_notifications_tables",
    
    # Notifications
    "create_notification",
    "get_notifications",
    "mark_notification_as_read",
    "mark_all_notifications_as_read",
    "delete_notification",
    "delete_all_notifications",
    "send_notification",
    
    # Subscriptions
    "subscribe_to_series",
    "unsubscribe_from_series",
    "get_subscriptions",
    "is_subscribed",
    
    # Settings
    "get_notification_settings",
    "update_notification_settings",
    
    # Releases
    "check_upcoming_releases",
]
