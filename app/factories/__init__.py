"""
Factory classes for creating service instances.
"""
from app.factories.cache_factory import get_cache_provider
from app.factories.api_client_factory import create_products_client, create_auth_client

__all__ = [
    "get_cache_provider",
    "create_products_client",
    "create_auth_client",
]
