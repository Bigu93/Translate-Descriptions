"""
Structured logger implementation for Translate-Descriptions application.

This module provides a singleton structured logger with consistent formatting
and multiple handlers (console and file rotation).
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from app.core.domain.interfaces import ILogger


class StructuredLogger(ILogger):
    """Singleton structured logger with consistent formatting.
    
    Implements ILogger interface and provides:
    - Console output for development
    - File rotation for production
    - Structured logging with context
    - Singleton pattern per logger name
    """
    
    _instances: Dict[str, 'StructuredLogger'] = {}
    
    def __new__(cls, name: str) -> 'StructuredLogger':
        """Create or return existing logger instance (Singleton pattern).
        
        Args:
            name: Logger name (typically module or class name)
            
        Returns:
            StructuredLogger instance for the given name
        """
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        return cls._instances[name]
    
    def __init__(self, name: str):
        """Initialize logger with handlers.
        
        Args:
            name: Logger name
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.name = name
        self._logger = logging.getLogger(name)
        self._setup_logger()
        self._initialized = True
    
    def _setup_logger(self):
        """Setup logger with handlers and formatters."""
        from app.config.settings import Settings
        
        settings = Settings.get_instance()
        
        log_level = getattr(logging, settings.logging.level, logging.INFO)
        self._logger.setLevel(log_level)
        
        self._logger.handlers.clear()
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        log_dir = settings.logging.log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, f"{self.name}.log"),
            maxBytes=settings.logging.max_bytes,
            backupCount=settings.logging.backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        self._logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Log debug message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        self._logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        self._logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        self._logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        self._logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        self._logger.critical(message, extra=kwargs)
    
    def set_level(self, level: str):
        """Change log level dynamically.
        
        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(log_level)
        for handler in self._logger.handlers:
            handler.setLevel(log_level)


def get_logger(name: str) -> StructuredLogger:
    """Get a logger instance by name.
    
    This is a convenience function that creates or returns an existing
    StructuredLogger instance for the given name.
    
    Args:
        name: Logger name (typically module or class name)
        
    Returns:
        StructuredLogger instance for the given name
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return StructuredLogger(name)
