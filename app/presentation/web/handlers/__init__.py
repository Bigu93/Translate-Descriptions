"""
Request handlers for API endpoints.
"""
from app.presentation.web.handlers.product_handlers import ProductHandlers
from app.presentation.web.handlers.translation_handlers import TranslationHandlers
from app.presentation.web.handlers.auth_handlers import AuthHandlers
from app.presentation.web.handlers.handler_registry import get_handler_registry

__all__ = [
    "ProductHandlers",
    "TranslationHandlers",
    "AuthHandlers",
    "get_handler_registry",
]
