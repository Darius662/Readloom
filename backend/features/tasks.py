#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from backend.base.logging import LOGGER
from backend.features.calendar import update_calendar
from backend.internals.settings import Settings


class TaskHandler:
    """Handler for scheduled tasks."""
    
    def __init__(self):
        """Initialize the task handler."""
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_calendar_update: Optional[datetime] = None
    
    def handle_intervals(self) -> None:
        """Start handling intervals."""
        if self.thread is not None and self.thread.is_alive():
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._interval_handler)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_handle(self) -> None:
        """Stop handling intervals."""
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=5)
    
    def _interval_handler(self) -> None:
        """Handle intervals."""
        settings = Settings().get_settings()
        
        while self.running:
            try:
                # Check if calendar needs updating
                current_time = datetime.now()
                if (self.last_calendar_update is None or 
                    current_time - self.last_calendar_update > 
                    timedelta(hours=settings.calendar_refresh_hours)):
                    
                    LOGGER.info("Updating calendar data")
                    update_calendar()
                    self.last_calendar_update = current_time
                
                # Sleep for a minute before checking again
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                LOGGER.error(f"Error in interval handler: {e}")
                # Sleep for a minute before trying again
                time.sleep(60)
