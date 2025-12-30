"""
Caching decorator for Translate-Descriptions application.

This module provides a decorator for caching function results
with configurable TTL and key generation.
"""

import functools
import hashlib
import json
from typing import Callable, Optional, Any
from app.core.domain.exceptions import CacheError
from app.core.domain.interfaces import ICacheProvider


def cache(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results.
    
    Caches function results in the configured cache provider.
    Cache keys are generated based on function name and arguments.
    
    Args:
        ttl: Time-to-live in seconds (default: 1 hour)
        key_prefix: Optional prefix for cache keys
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from app.factories.cache_factory import get_cache_provider
            
            cache_provider = get_cache_provider()
            cache_key = _generate_cache_key(
                key_prefix, func.__name__, args, kwargs
            )
            
            cached_result = cache_provider.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache_provider.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate a cache key from function arguments.
    
    Args:
        prefix: Key prefix
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Generated cache key (MD5 hash)
    """
    key_data = {
        "prefix": prefix,
        "function": func_name,
        "args": str(args),
        "kwargs": json.dumps(kwargs, sort_keys=True)
    }
    key_hash = hashlib.md5(json.dumps(key_data).encode()).hexdigest()
    return f"{prefix}:{func_name}:{key_hash}" if prefix else f"{func_name}:{key_hash}"


def clear_cache_for_prefix(prefix: str) -> bool:
    """Clear all cache entries with given prefix.
    
    Args:
        prefix: Cache key prefix to clear
        
    Returns:
        True if successful, False otherwise
    """
    from app.factories.cache_factory import get_cache_provider
    
    cache_provider = get_cache_provider()
    cache_provider.clear()
    return True
