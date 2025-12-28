"""
External API clients for communicating with third-party services.
"""
from app.infrastructure.external_api.base_client import BaseClient, APIRequestError, APIResponseError
from app.infrastructure.external_api.auth_client import AuthClient
from app.infrastructure.external_api.products_client import ProductsClient

__all__ = [
    "BaseClient",
    "APIRequestError",
    "APIResponseError",
    "AuthClient",
    "ProductsClient",
]
