"""
Rate limiting decorator for Translate-Descriptions application.

This module provides rate limiting functionality to prevent abuse
of API endpoints with configurable limits and time windows.
"""

import time
import functools
from typing import Callable, Optional
from collections import defaultdict
from app.core.domain.exceptions import RateLimitExceededError


class RateLimiter:
    """Simple in-memory rate limiter.
    
    Tracks requests per key within a time window.
    Thread-safe for basic use cases.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self._requests = defaultdict(list)
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request is allowed within rate limit.
        
        Args:
            key: Rate limit key (e.g., function name, IP address)
            limit: Maximum requests allowed within window
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self._requests[key]) >= limit:
            return False
        
        # Record this request
        self._requests[key].append(now)
        return True


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(
    limit: int = 10,
    window_seconds: int = 60,
    key_func: Optional[Callable] = None
):
    """Decorator for rate limiting function calls.
    
    Prevents function from being called more than `limit` times
    within `window_seconds` seconds.
    
    Args:
        limit: Maximum requests allowed (default: 10)
        window_seconds: Time window in seconds (default: 60)
        key_func: Optional function to generate rate limit key
                 (default: function name)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = func.__name__
            
            # Check if allowed
            if not _rate_limiter.is_allowed(key, limit, window_seconds):
                raise RateLimitExceededError(
                    f"Rate limit exceeded: {limit} requests per {window_seconds} seconds"
                )
            
            # Execute function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_rate_limit_stats() -> dict:
    """Get rate limiting statistics.
    
    Returns:
        Dictionary with rate limiting statistics
    """
    stats = {}
    for key, requests in _rate_limiter._requests.items():
        if requests:
            stats[key] = {
                "request_count": len(requests),
                "oldest_request": min(requests),
                "newest_request": max(requests)
            }
    return stats
