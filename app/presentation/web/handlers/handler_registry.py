"""
Handler registry for lazy initialization of route handlers.

This module provides a singleton registry that allows blueprints to be registered
at module load time while handlers are initialized lazily on first request.
"""
from typing import Optional
from app.presentation.web.handlers.product_handlers import ProductHandlers
from app.presentation.web.handlers.translation_handlers import TranslationHandlers
from app.presentation.web.handlers.auth_handlers import AuthHandlers


class HandlerRegistry:
    """Singleton registry for route handlers.
    
    This registry holds references to all handlers and allows them to be
    initialized lazily after blueprint registration.
    """
    
    _instance: Optional['HandlerRegistry'] = None
    
    def __new__(cls) -> 'HandlerRegistry':
        """Create or return existing registry instance (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize registry with None handlers."""
        # Skip if already initialized (Singleton pattern)
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.product_handlers: Optional[ProductHandlers] = None
        self.translation_handlers: Optional[TranslationHandlers] = None
        self.auth_handlers: Optional[AuthHandlers] = None
        self._initialized = True
    
    def initialize(
        self,
        product_handlers: ProductHandlers,
        translation_handlers: TranslationHandlers,
        auth_handlers: AuthHandlers
    ) -> None:
        """Initialize all handlers in the registry.
        
        Args:
            product_handlers: Product handlers instance
            translation_handlers: Translation handlers instance
            auth_handlers: Auth handlers instance
        """
        self.product_handlers = product_handlers
        self.translation_handlers = translation_handlers
        self.auth_handlers = auth_handlers
    
    def is_initialized(self) -> bool:
        """Check if all handlers have been initialized.
        
        Returns:
            True if all handlers are initialized, False otherwise
        """
        return all([
            self.product_handlers is not None,
            self.translation_handlers is not None,
            self.auth_handlers is not None
        ])


# Global registry instance
_registry: Optional[HandlerRegistry] = None


def get_handler_registry() -> HandlerRegistry:
    """Get the singleton handler registry instance.
    
    Returns:
        HandlerRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = HandlerRegistry()
    return _registry
