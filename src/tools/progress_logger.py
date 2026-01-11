"""
Progress Logger Module
Logs scan progress for UI display
"""

from typing import Callable, Optional, List
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class ProgressLogger:
    """Progress logger with callbacks for UI"""
    
    def __init__(self):
        self.logs = []
        self.progress = 0
        self.total_items = 0
        self.current_item = 0
        
        # Callbacks for UI updates
        self.on_log: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_entry = {
            'timestamp': timestamp,
            'level': level.value,
            'message': message,
            'full_text': f"[{timestamp}] [{level.value}] {message}"
        }
        
        self.logs.append(log_entry)
        
        # Trigger callback
        if self.on_log:
            self.on_log(log_entry)
    
    def set_total(self, total: int) -> None:
        """Set total items to process"""
        self.total_items = total
        self.current_item = 0
        self.log(f"Starting process with {total} items", LogLevel.INFO)
    
    def update_progress(self, current: int, message: str = "") -> None:
        """Update progress"""
        self.current_item = current
        
        if self.total_items > 0:
            self.progress = int((current / self.total_items) * 100)
        
        if message:
            self.log(message, LogLevel.INFO)
        
        # Trigger callback
        if self.on_progress:
            self.on_progress(self.progress, current, self.total_items)
    
    def increment_progress(self, message: str = "") -> None:
        """Increment progress by 1"""
        self.update_progress(self.current_item + 1, message)
    
    def success(self, message: str) -> None:
        """Log success message"""
        self.log(message, LogLevel.SUCCESS)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.log(message, LogLevel.ERROR)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.log(message, LogLevel.WARNING)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.log(message, LogLevel.INFO)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.log(message, LogLevel.DEBUG)
    
    def complete(self, message: str = "") -> None:
        """Mark process as complete"""
        if message:
            self.success(message)
        else:
            self.success(f"Process complete! Processed {self.current_item}/{self.total_items} items")
        
        self.progress = 100
        
        if self.on_complete:
            self.on_complete()
    
    def get_logs(self) -> List[dict]:
        """Get all logs"""
        return self.logs
    
    def clear_logs(self) -> None:
        """Clear all logs"""
        self.logs = []
    
    def get_progress(self) -> dict:
        """Get current progress status"""
        return {
            'progress': self.progress,
            'current': self.current_item,
            'total': self.total_items,
            'percentage': f"{self.progress}%"
        }
