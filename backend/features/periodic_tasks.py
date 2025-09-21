#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from backend.base.logging import LOGGER
from backend.features.ebook_files import scan_for_ebooks
from backend.internals.settings import Settings


class PeriodicTaskManager:
    """Manager for periodic tasks."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PeriodicTaskManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._stop_event = threading.Event()
        self._thread = None
        self._last_scan_time = None
        self._settings = Settings().get_settings()
        self._scan_interval_minutes = self._settings.task_interval_minutes
    
    def start(self):
        """Start the periodic task manager."""
        if self._thread is not None and self._thread.is_alive():
            LOGGER.warning("Periodic task manager is already running")
            return
            
        LOGGER.info("Starting periodic task manager")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the periodic task manager."""
        if self._thread is None or not self._thread.is_alive():
            LOGGER.warning("Periodic task manager is not running")
            return
            
        LOGGER.info("Stopping periodic task manager")
        self._stop_event.set()
        self._thread.join(timeout=5)
        self._thread = None
    
    def _run(self):
        """Run the periodic tasks."""
        LOGGER.info(f"Periodic task manager running with scan interval: {self._scan_interval_minutes} minutes")
        
        while not self._stop_event.is_set():
            try:
                # Check if it's time to run the scan
                current_time = datetime.now()
                
                if (self._last_scan_time is None or 
                    current_time - self._last_scan_time > timedelta(minutes=self._scan_interval_minutes)):
                    
                    LOGGER.info("Running periodic e-book scan")
                    stats = scan_for_ebooks()
                    self._last_scan_time = current_time
                    
                    LOGGER.info(f"Periodic scan complete: {stats}")
                
                # Sleep for a minute before checking again
                for _ in range(60):  # Check every second if we should stop
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                LOGGER.error(f"Error in periodic task manager: {e}")
                time.sleep(60)  # Wait a minute before trying again
    
    def update_settings(self):
        """Update settings from the database."""
        self._settings = Settings().get_settings()
        self._scan_interval_minutes = self._settings.task_interval_minutes
        LOGGER.info(f"Updated scan interval: {self._scan_interval_minutes} minutes")


# Create a singleton instance
periodic_task_manager = PeriodicTaskManager()
