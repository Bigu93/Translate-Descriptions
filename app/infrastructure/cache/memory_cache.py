"""
In-memory cache implementation for Translate-Descriptions application.

This module provides a simple in-memory cache with TTL support.
For production, consider using Redis or similar distributed cache.
"""

import time
import hashlib
import json
from typing import Optional, Any
from app.core.domain.interfaces import ICacheProvider
from app.core.domain.exceptions import CacheError


class MemoryCache(ICacheProvider):
    """In-memory cache with TTL support.
    
    Simple thread-safe in-memory cache implementation.
    Suitable for development and small-scale deployments.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize in-memory cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: dict = {}
        self._timestamps: dict = {}
        self._default_ttl = default_ttl
        self._lock = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            return None
        
        if self._is_expired(key):
            self.delete(key)
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default TTL)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._cache[key] = value
            self._timestamps[key] = time.time() + (ttl or self._default_ttl)
            return True
        except Exception as e:
            raise CacheError(f"Failed to set cache value: {e}") from e
    
    def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cached values.
        
        Returns:
            True if successful
        """
        self._cache.clear()
        self._timestamps.clear()
        return True
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if expired, False otherwise
        """
        if key not in self._timestamps:
            return True
        return time.time() > self._timestamps[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "total_entries": len(self._cache),
            "expired_entries": sum(
                1 for key in self._cache 
                if self._is_expired(key)
            ),
            "valid_entries": sum(
                1 for key in self._cache 
                if not self._is_expired(key)
            )
        }


def generate_cache_key(prefix: str, *args) -> str:
    """Generate a cache key from arguments.
    
    Args:
        prefix: Key prefix (e.g., "translation:", "product:")
        *args: Values to include in key
            
    Returns:
        Generated cache key (MD5 hash for consistency)
    """
    key_data = json.dumps(args, sort_keys=True)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}{key_hash}" if prefix else key_hash
