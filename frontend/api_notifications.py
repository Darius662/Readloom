#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for notifications.
"""

from flask import Blueprint, jsonify

# Create API blueprint
notifications_api_bp = Blueprint('api_notifications', __name__, url_prefix='/api')


@notifications_api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications."""
    return jsonify({
        "success": True,
        "notifications": []
    })


@notifications_api_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """Get all subscriptions."""
    return jsonify({
        "success": True,
        "subscriptions": []
    })


@notifications_api_bp.route('/notifications/settings', methods=['GET'])
def get_notification_settings():
    """Get notification settings."""
    return jsonify({
        "notify_new_volumes": 1,
        "notify_new_chapters": 1,
        "notify_releases_days_before": 1,
        "browser_enabled": 1,
        "email_enabled": 0,
        "email_address": "",
        "discord_enabled": 0,
        "discord_webhook": "",
        "telegram_enabled": 0,
        "telegram_bot_token": "",
        "telegram_chat_id": ""
    })
