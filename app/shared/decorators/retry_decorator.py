"""
Retry decorator for Translate-Descriptions application.

This module provides a decorator for retrying failed function calls
with exponential backoff and configurable exceptions.
"""

import time
import functools
from typing import Callable, Type, Tuple, Any
from app.core.domain.exceptions import TranslateDescriptionsError


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying failed function calls.
    
    Implements retry logic with exponential backoff.
    Useful for handling transient failures in external API calls.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for delay between retries (default: 2.0)
        exceptions: Tuple of exception types to catch (default: all exceptions)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        raise last_exception
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            raise last_exception
        
        return wrapper
    return decorator


def retry_with_jitter(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: float = 0.1,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying with random jitter.
    
    Similar to retry decorator but adds random jitter to
    prevent thundering herd problem when multiple clients retry simultaneously.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for delay between retries (default: 2.0)
        jitter: Random jitter factor (default: 0.1 = 10%)
        exceptions: Tuple of exception types to catch (default: all exceptions)
        
    Returns:
        Decorated function
    """
    import random
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        raise last_exception
                    
                    jitter_amount = current_delay * jitter
                    actual_delay = current_delay + (random.random() * jitter_amount - jitter_amount / 2)
                    time.sleep(actual_delay)
                    current_delay *= backoff_factor
            
            raise last_exception
        
        return wrapper
    return decorator
