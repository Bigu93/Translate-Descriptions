"""
Domain interfaces for Translate-Descriptions application.

This module defines contracts (interfaces) that services and repositories must implement.
Following the Interface Segregation Principle, each interface is focused and cohesive.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.core.domain.models import (
    TranslationRequest,
    TranslationResponse,
    Product,
    ProductDescription,
    Token,
    AuthToken,
    VATValidationResult
)


class ITranslationService(ABC):
    """Translation service interface.
    
    Defines contract for translation operations.
    Implementations can use different translation providers (OpenAI, DeepL, etc.)
    """
    
    @abstractmethod
    def translate_product_content(
        self,
        request: TranslationRequest
    ) -> TranslationResponse:
        """Translate product content.
        
        Args:
            request: Translation request with text, languages, and content type
            
        Returns:
            Translation response with translated text and metadata
        """
        pass
    
    @abstractmethod
    def translate_text(
        self,
        text: str,
        target_languages: List[str],
        content_type: str,
        category: Optional[str] = None
    ) -> Dict[str, str]:
        """Translate text to target languages.
        
        Args:
            text: Text to translate
            target_languages: List of target language codes
            content_type: Type of content (name, description, etc.)
            category: Optional product category for context
            
        Returns:
            Dictionary mapping language codes to translated text
        """
        pass


class IProductService(ABC):
    """Product service interface.
    
    Defines contract for product-related operations.
    Handles fetching and updating product data from external API.
    """
    
    @abstractmethod
    def get_product_data(
        self,
        product_id: str,
        shop_id: int = 0,
        lang_id: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get product data.
        
        Args:
            product_id: Product identifier
            shop_id: Shop identifier (default: 0)
            lang_id: Language filter (None = all languages)
            fields: List of fields to return (None = all fields)
            
        Returns:
            List of product data dictionaries
        """
        pass
    
    @abstractmethod
    def set_product_description(self, data: Dict[str, Any]) -> bool:
        """Set product description.
        
        Args:
            data: Product description data to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_product_info(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Get product info for multiple products.
        
        Args:
            product_ids: List of product identifiers
            
        Returns:
            List of product info dictionaries
        """
        pass
    
    @abstractmethod
    def get_product_full_info(self, product_id: str) -> Dict[str, Any]:
        """Get full product info.
        
        Args:
            product_id: Product identifier (EAN or product-size format)
            
        Returns:
            Full product information dictionary
        """
        pass
    
    @abstractmethod
    def get_products_info(
        self,
        results_page: int = 0,
        results_limit: int = 50
    ) -> Dict[str, Any]:
        """Get paginated products info.
        
        Args:
            results_page: Page number (default: 0)
            results_limit: Number of results per page (default: 50, max: 100)
            
        Returns:
            Dictionary with 'data' and 'pagination' keys
        """
        pass


class ITokenService(ABC):
    """Token service interface.
    
    Defines contract for temporary API token management.
    """
    
    @abstractmethod
    def generate_token(self) -> Token:
        """Generate a new API token.
        
        Returns:
            Token entity with token string and expiry time
        """
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        """Validate a token.
        
        Args:
            token: Token string to validate
            
        Returns:
            True if token is valid and not expired, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens.
        
        Returns:
            Number of tokens removed
        """
        pass
    
    @abstractmethod
    def get_all_tokens(self) -> List[Token]:
        """Get all tokens.
        
        Returns:
            List of all Token entities
        """
        pass


class IAuthService(ABC):
    """Authentication service interface.
    
    Defines contract for bearer token authentication management.
    """
    
    @abstractmethod
    def generate_auth_token(self) -> AuthToken:
        """Generate a bearer authentication token.
        
        Returns:
            AuthToken entity with token string and expiry time
        """
        pass
    
    @abstractmethod
    def revoke_auth_token(self, token: str) -> bool:
        """Revoke a bearer authentication token.
        
        Args:
            token: Token string to revoke
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_auth_token(self, token: str) -> bool:
        """Validate a bearer authentication token.
        
        Args:
            token: Token string to validate
            
        Returns:
            True if token is valid and not expired, False otherwise
        """
        pass


class IViesService(ABC):
    """VAT validation service interface.
    
    Defines contract for VAT number validation via VIES service.
    """
    
    @abstractmethod
    def validate_vat(self, country_code: str, vat_number: str) -> VATValidationResult:
        """Validate VAT number.
        
        Args:
            country_code: Two-letter country code (e.g., "PL", "DE")
            vat_number: VAT number to validate
            
        Returns:
            VATValidationResult with validation status and company info
        """
        pass


class ICacheProvider(ABC):
    """Cache provider interface.
    
    Defines contract for caching operations.
    Implementations can use in-memory, Redis, etc.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default TTL)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cached values.
        
        Returns:
            True if successful, False otherwise
        """
        pass


class ILogger(ABC):
    """Logger interface.
    
    Defines contract for logging operations.
    Allows for different logger implementations (file, console, cloud, etc.)
    """
    
    @abstractmethod
    def debug(self, message: str, **kwargs):
        """Log debug message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs):
        """Log info message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs):
        """Log warning message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs):
        """Log error message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs):
        """Log critical message.
        
        Args:
            message: Log message
            **kwargs: Additional context (key-value pairs)
        """
        pass
