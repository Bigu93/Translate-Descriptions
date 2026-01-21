"""
Factory for creating API client instances.
"""
from typing import Optional
from app.infrastructure.logging.structured_logger import get_logger
from app.infrastructure.external_api.auth_client import AuthClient
from app.infrastructure.external_api.products_client import ProductsClient


logger = get_logger("api_client_factory")


def create_products_client(
    base_url: str,
    client_username: str,
    client_secret: str,
    api_version: str = "v3",
    ssl_verify: bool = True,
    api_key: str = "",
) -> ProductsClient:
    """
    Create and return a ProductsClient instance with authentication.

    Args:
        base_url: The base URL for the API
        client_username: The API username
        client_secret: The API secret
        api_version: The API version (default: "v3")
        ssl_verify: Whether to verify SSL certificates (default: True)

    Returns:
        Configured ProductsClient instance

    Example:
        >>> client = create_products_client(
        ...     base_url="https://api.example.com",
        ...     client_username="user",
        ...     client_secret="secret"
        ... )
    """
    try:
        auth_client = None
        token = ""

        # Prefer X-API-KEY auth if configured.
        if not api_key:
            auth_client = AuthClient(
                base_url=base_url,
                client_username=client_username,
                client_secret=client_secret,
                logger=logger,
            )
            token = auth_client.get_token()

        products_client = ProductsClient(
            hostname=base_url,
            auth_token=token,
            version=api_version,
            ssl_verify=ssl_verify,
            auth_client=auth_client,
            api_key=api_key,
            logger=logger,
        )

        logger.info("ProductsClient created successfully")
        return products_client

    except Exception as e:
        logger.error(f"Failed to create ProductsClient: {e}")
        raise


def create_auth_client(
    base_url: str,
    client_username: str,
    client_secret: str,
    logger: Optional[object] = None,
) -> AuthClient:
    """
    Create and return an AuthClient instance.

    Args:
        base_url: The base URL for the API
        client_username: The API username
        client_secret: The API secret
        logger: Optional logger instance

    Returns:
        Configured AuthClient instance

    Example:
        >>> client = create_auth_client(
        ...     base_url="https://api.example.com",
        ...     client_username="user",
        ...     client_secret="secret"
        ... )
    """
    try:
        effective_logger = logger or get_logger("auth")
        auth_client = AuthClient(
            base_url=base_url,
            client_username=client_username,
            client_secret=client_secret,
            logger=effective_logger,
        )

        effective_logger.info("AuthClient created successfully")
        return auth_client

    except Exception as e:
        (logger or get_logger("auth")).error(f"Failed to create AuthClient: {e}")
        raise
