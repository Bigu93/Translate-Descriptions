"""
Request handlers for API endpoints.
"""
from app.presentation.web.handlers.product_handlers import ProductHandlers
from app.presentation.web.handlers.translation_handlers import TranslationHandlers
from app.presentation.web.handlers.auth_handlers import AuthHandlers

__all__ = [
    "ProductHandlers",
    "TranslationHandlers",
    "AuthHandlers",
]
