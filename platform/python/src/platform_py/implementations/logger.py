"""
Console-based logger implementation for development and basic production use.
Outputs structured JSON logs that can be easily parsed by log aggregation systems.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..interfaces import Logger


class ConsoleLogger(Logger):
    """
    Simple console-based logger implementation with structured JSON output.
    Supports contextual logging with base fields and child loggers.
    """
    
    def __init__(self, base_fields: Optional[Dict[str, Any]] = None):
        """
        Initialize logger with optional base fields.
        
        Args:
            base_fields: Dictionary of fields to include in every log entry
        """
        self.base_fields = {
            "service": "unknown",
            "environment": os.environ.get("ENVIRONMENT", os.environ.get("NODE_ENV", "development")),
            **(base_fields or {})
        }
    
    def info(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log info level message"""
        self._write_log("info", msg, meta)
    
    def error(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log error level message"""
        self._write_log("error", msg, meta)
    
    def warn(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log warning level message"""
        self._write_log("warn", msg, meta)
    
    def debug(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """Log debug level message (filtered in production)"""
        # Only log debug messages in development or when LOG_LEVEL=debug
        environment = self.base_fields.get("environment", "development")
        log_level = os.environ.get("LOG_LEVEL", "").lower()
        
        if environment == "development" or log_level == "debug":
            self._write_log("debug", msg, meta)
    
    def with_fields(self, fields: Dict[str, Any]) -> "ConsoleLogger":
        """
        Create child logger with additional context fields.
        This is useful for adding request-specific context like user_id, correlation_id, etc.
        
        Args:
            fields: Additional fields to include in all log entries from child logger
            
        Returns:
            New ConsoleLogger instance with combined fields
        """
        combined_fields = {**self.base_fields, **fields}
        return ConsoleLogger(combined_fields)
    
    def _write_log(self, level: str, msg: str, meta: Optional[Dict[str, Any]] = None) -> None:
        """
        Internal method to write structured log entries.
        Outputs JSON format for easy parsing by log systems.
        
        Args:
            level: Log level (info, error, warn, debug)
            msg: Log message
            meta: Optional metadata dictionary
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "msg": msg,
            **self.base_fields,
            **(meta or {})
        }
        
        log_string = json.dumps(log_entry, separators=(",", ":"), default=str)
        
        # Use appropriate output stream based on level
        if level == "error":
            print(log_string, file=sys.stderr)
        else:
            print(log_string, file=sys.stdout)