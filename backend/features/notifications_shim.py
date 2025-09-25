#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notifications module for Readloom - compatibility shim.

This module re-exports all public functions from the notifications package.
The implementation has been moved to backend.features.notifications.
"""

from backend.features.notifications import (
    # Schema
    setup_notifications_tables,
    
    # Notifications
    create_notification,
    get_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification,
    delete_all_notifications,
    send_notification,
    
    # Subscriptions
    subscribe_to_series,
    unsubscribe_from_series,
    get_subscriptions,
    is_subscribed,
    
    # Settings
    get_notification_settings,
    update_notification_settings,
    
    # Releases
    check_upcoming_releases,
)

# Re-export all public functions
__all__ = [
    "setup_notifications_tables",
    "create_notification",
    "get_notifications",
    "mark_notification_as_read",
    "mark_all_notifications_as_read",
    "delete_notification",
    "delete_all_notifications",
    "send_notification",
    "subscribe_to_series",
    "unsubscribe_from_series",
    "get_subscriptions",
    "is_subscribed",
    "get_notification_settings",
    "update_notification_settings",
    "check_upcoming_releases",
]
