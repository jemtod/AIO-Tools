"""
Progress Logger Module
Provides logging functionality with progress tracking
"""

from enum import Enum
from typing import Optional
from datetime import datetime


class LogLevel(Enum):
    """Log levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    SUCCESS = 4


class ProgressLogger:
    """Logger with progress tracking capabilities"""
    
    def __init__(self, log_level: LogLevel = LogLevel.INFO):
        self.log_level = log_level
        self.total = 0
        self.current = 0
        self.start_time: Optional[datetime] = None
    
    def set_log_level(self, level: LogLevel) -> None:
        """Set logging level"""
        self.log_level = level
    
    def set_total(self, total: int) -> None:
        """Set total items for progress tracking"""
        self.total = total
        self.start_time = datetime.now()
    
    def update_progress(self, current: int, message: str = "") -> None:
        """Update progress"""
        self.current = current
        if self.total > 0:
            percentage = int((current / self.total) * 100)
            msg = f"[{percentage}%] {message}" if message else f"[{percentage}%] Progress: {current}/{self.total}"
            print(msg)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        if self.log_level.value <= LogLevel.DEBUG.value:
            print(f"[DEBUG] {message}")
    
    def info(self, message: str) -> None:
        """Log info message"""
        if self.log_level.value <= LogLevel.INFO.value:
            print(f"[INFO] {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        if self.log_level.value <= LogLevel.WARNING.value:
            print(f"[WARNING] {message}")
    
    def error(self, message: str) -> None:
        """Log error message"""
        if self.log_level.value <= LogLevel.ERROR.value:
            print(f"[ERROR] {message}")
    
    def success(self, message: str) -> None:
        """Log success message"""
        print(f"[SUCCESS] {message}")
    
    def complete(self, message: str = "Complete") -> None:
        """Log completion message"""
        elapsed = ""
        if self.start_time:
            elapsed_time = datetime.now() - self.start_time
            elapsed = f" (Time: {elapsed_time.total_seconds():.1f}s)"
        print(f"[COMPLETE] {message}{elapsed}")
