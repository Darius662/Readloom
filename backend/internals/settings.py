#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, List, Optional, Union

from backend.base.custom_exceptions import InvalidSettingValue
from backend.base.definitions import Constants, Settings as SettingsType
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


class Settings:
    """Class for managing application settings."""
    
    def __init__(self):
        """Initialize the settings."""
        self.restart_on_hosting_changes = True
        self._initialize_default_settings()
    
    def _initialize_default_settings(self) -> None:
        """Initialize default settings if they don't exist."""
        default_settings = {
            "host": Constants.DEFAULT_HOST,
            "port": Constants.DEFAULT_PORT,
            "url_base": Constants.DEFAULT_URL_BASE,
            "log_level": Constants.DEFAULT_LOG_LEVEL,
            "log_rotation": Constants.DEFAULT_LOG_ROTATION,
            "log_size": Constants.DEFAULT_LOG_SIZE,
            "metadata_cache_days": Constants.DEFAULT_METADATA_CACHE_DAYS,
            "calendar_range_days": Constants.DEFAULT_CALENDAR_RANGE_DAYS,
            "calendar_refresh_hours": Constants.DEFAULT_CALENDAR_REFRESH_HOURS,
            "task_interval_minutes": Constants.DEFAULT_TASK_INTERVAL_MINUTES,
            "ebook_storage": Constants.DEFAULT_EBOOK_STORAGE,
            "root_folders": Constants.DEFAULT_ROOT_FOLDERS
        }
        
        # Ensure settings table exists
        try:
            execute_query("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """, commit=True)
            LOGGER.info("Settings table created or verified")
        except Exception as e:
            LOGGER.error(f"Error creating settings table: {e}")
            return
        
        # Check which settings already exist
        try:
            existing_settings = execute_query("SELECT key FROM settings")
            existing_keys = {setting["key"] for setting in existing_settings}
            
            # Insert default settings that don't exist
            for key, value in default_settings.items():
                if key not in existing_keys:
                    execute_query(
                        "INSERT INTO settings (key, value) VALUES (?, ?)",
                        (key, json.dumps(value)),
                        commit=True
                    )
                    LOGGER.info(f"Initialized default setting: {key} = {value}")
        except Exception as e:
            LOGGER.error(f"Error initializing settings: {e}")
    
    def get_settings(self) -> SettingsType:
        """Get all settings.

        Returns:
            SettingsType: All settings.
        """
        settings_rows = execute_query("SELECT key, value FROM settings")
        settings_dict = {row["key"]: json.loads(row["value"]) for row in settings_rows}
        
        return SettingsType(
            host=settings_dict.get("host", Constants.DEFAULT_HOST),
            port=settings_dict.get("port", Constants.DEFAULT_PORT),
            url_base=settings_dict.get("url_base", Constants.DEFAULT_URL_BASE),
            log_level=settings_dict.get("log_level", Constants.DEFAULT_LOG_LEVEL),
            log_rotation=settings_dict.get("log_rotation", Constants.DEFAULT_LOG_ROTATION),
            log_size=settings_dict.get("log_size", Constants.DEFAULT_LOG_SIZE),
            metadata_cache_days=settings_dict.get("metadata_cache_days", Constants.DEFAULT_METADATA_CACHE_DAYS),
            calendar_range_days=settings_dict.get("calendar_range_days", Constants.DEFAULT_CALENDAR_RANGE_DAYS),
            calendar_refresh_hours=settings_dict.get("calendar_refresh_hours", Constants.DEFAULT_CALENDAR_REFRESH_HOURS),
            task_interval_minutes=settings_dict.get("task_interval_minutes", Constants.DEFAULT_TASK_INTERVAL_MINUTES),
            ebook_storage=settings_dict.get("ebook_storage", Constants.DEFAULT_EBOOK_STORAGE),
            root_folders=settings_dict.get("root_folders", Constants.DEFAULT_ROOT_FOLDERS)
        )
    
    def get_setting(self, key: str) -> Any:
        """Get a setting.

        Args:
            key (str): The key of the setting.

        Returns:
            Any: The value of the setting.

        Raises:
            KeyError: If the setting does not exist.
        """
        result = execute_query("SELECT value FROM settings WHERE key = ?", (key,))
        if not result:
            raise KeyError(f"Setting {key} does not exist")
        
        return json.loads(result[0]["value"])
    
    def update(self, settings: Dict[str, Any]) -> None:
        """Update settings.

        Args:
            settings (Dict[str, Any]): The settings to update.

        Raises:
            InvalidSettingValue: If a setting value is invalid.
        """
        need_restart = False
        
        for key, value in settings.items():
            # Validate settings
            if key == "host":
                if not isinstance(value, str):
                    raise InvalidSettingValue("Host must be a string")
                need_restart = True
            
            elif key == "port":
                if not isinstance(value, int) or value < 1 or value > 65535:
                    raise InvalidSettingValue("Port must be an integer between 1 and 65535")
                need_restart = True
            
            elif key == "url_base":
                if not isinstance(value, str):
                    raise InvalidSettingValue("URL base must be a string")
                # Ensure URL base starts with a slash if not empty
                if value and not value.startswith("/"):
                    value = f"/{value}"
                # Ensure URL base does not end with a slash
                if value.endswith("/"):
                    value = value[:-1]
                need_restart = True
            
            elif key == "log_level":
                valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                if not isinstance(value, str) or value.upper() not in valid_levels:
                    raise InvalidSettingValue(f"Log level must be one of {', '.join(valid_levels)}")
            
            elif key == "log_rotation":
                if not isinstance(value, int) or value < 1:
                    raise InvalidSettingValue("Log rotation must be a positive integer")
            
            elif key == "log_size":
                if not isinstance(value, int) or value < 1:
                    raise InvalidSettingValue("Log size must be a positive integer")
            
            elif key == "metadata_cache_days":
                if not isinstance(value, int) or value < 1:
                    raise InvalidSettingValue("Metadata cache days must be a positive integer")
            
            elif key == "calendar_range_days":
                if not isinstance(value, int) or value < 1:
                    raise InvalidSettingValue("Calendar range days must be a positive integer")
            
            elif key == "calendar_refresh_hours":
                if not isinstance(value, int) or value < 1:
                    raise InvalidSettingValue("Calendar refresh hours must be a positive integer")
            
            elif key == "task_interval_minutes":
                if not isinstance(value, int) or value < 1:
                    raise InvalidSettingValue("Task interval minutes must be a positive integer")
                    
            elif key == "ebook_storage":
                if not isinstance(value, str):
                    raise InvalidSettingValue("E-book storage path must be a string")
                    
            elif key == "root_folders":
                if not isinstance(value, list):
                    raise InvalidSettingValue("Root folders must be a list")
                
                # Validate each root folder has path and name
                for folder in value:
                    if not isinstance(folder, dict) or "path" not in folder or "name" not in folder:
                        raise InvalidSettingValue("Each root folder must have a path and name")
                    if not isinstance(folder["path"], str) or not isinstance(folder["name"], str):
                        raise InvalidSettingValue("Root folder path and name must be strings")
            
            # Update setting
            execute_query(
                "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (json.dumps(value), key),
                commit=True
            )
            
            LOGGER.info(f"Updated setting {key} to {value}")
        
        if need_restart and self.restart_on_hosting_changes:
            from backend.internals.server import SERVER
            SERVER.start_type = Constants.StartType.RESTART
