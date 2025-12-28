"""
No-op cache implementation for Translate-Descriptions application.

This module provides a no-operation cache used when caching is disabled.
"""

from typing import Optional, Any
from app.core.domain.interfaces import ICacheProvider


class NoopCache(ICacheProvider):
    """No-operation cache (does nothing).
    
    Used when caching is disabled in configuration.
    All methods return None or False without side effects.
    """
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (always returns None).
        
        Args:
            key: Cache key (ignored)
            
        Returns:
            Always None
        """
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache (does nothing).
        
        Args:
            key: Cache key (ignored)
            value: Value to cache (ignored)
            ttl: Time-to-live in seconds (ignored)
            
        Returns:
            Always True (no-op)
        """
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache (does nothing).
        
        Args:
            key: Cache key (ignored)
            
        Returns:
            Always True (no-op)
        """
        return True
    
    def clear(self) -> bool:
        """Clear all cached values (does nothing).
        
        Returns:
            Always True (no-op)
        """
        return True
