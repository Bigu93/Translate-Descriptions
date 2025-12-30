"""
Cache factory for Translate-Descriptions application.

This module provides a factory for creating cache provider instances
with support for different backends (memory, Redis, etc.).
"""

from typing import Optional

from app.core.domain.interfaces import ICacheProvider
from app.core.domain.exceptions import ConfigurationError
from app.config.settings import Settings
from app.infrastructure.cache.memory_cache import MemoryCache


class CacheFactory:
    """Factory for creating cache provider instances.
    
    Implements Factory Pattern for cache instantiation.
    Allows for different cache backends via configuration.
    """
    
    _instance: Optional[ICacheProvider] = None
    
    @classmethod
    def get_cache_provider(cls) -> ICacheProvider:
        """Get cache provider instance (Singleton).
        
        Creates appropriate cache provider based on configuration.
        Currently supports: memory, redis (placeholder for future)
        
        Returns:
            ICacheProvider instance
        """
        if cls._instance is None:
            settings = Settings.get_instance()
            
            if not settings.cache.enabled:
                from app.infrastructure.cache.noop_cache import NoopCache
                cls._instance = NoopCache()
            elif settings.cache.backend == "memory":
                cls._instance = MemoryCache(
                    default_ttl=settings.cache.ttl
                )
            elif settings.cache.backend == "redis":
                # Placeholder for Redis implementation
                # Would require redis-py package
                raise ConfigurationError(
                    "Redis cache backend not yet implemented. "
                    "Use 'memory' backend instead."
                )
            else:
                raise ConfigurationError(
                    f"Unknown cache backend: {settings.cache.backend}"
                )
        
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset factory instance (for testing).
        
        Clears the singleton instance.
        """
        cls._instance = None


def get_cache_provider() -> ICacheProvider:
    """Convenience function to get cache provider.
    
    Returns:
        ICacheProvider instance
    """
    return CacheFactory.get_cache_provider()
