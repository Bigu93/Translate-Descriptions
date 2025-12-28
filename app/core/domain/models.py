"""
Domain models for Translate-Descriptions application.

This module defines the core domain entities used throughout the application.
All models are implemented as dataclasses for type safety and immutability where appropriate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any


@dataclass
class Token:
    """API token entity.
    
    Represents a temporary API token used for authentication.
    Tokens have a fixed expiry time for security.
    
    Attributes:
        token: The token string value
        expires_at: When the token expires
        created_at: When the token was created (defaults to now)
    """
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Check if token is expired.
        
        Returns:
            True if token has expired, False otherwise
        """
        return datetime.now() > self.expires_at
    
    def obfuscate(self) -> str:
        """Return obfuscated token for logging.
        
        Shows only first and last character for security.
        
        Returns:
            Obfuscated token string (e.g., "a****z")
        """
        if len(self.token) <= 8:
            return "****"
        return f"{self.token[:1]}****{self.token[-1:]}"


@dataclass
class AuthToken:
    """Bearer authentication token.
    
    Represents a long-lived authentication token for API access.
    Used for Bearer authentication in Authorization headers.
    
    Attributes:
        token: The bearer token string value
        expires_at: When the token expires
        created_at: When the token was created (defaults to now)
    """
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired).
        
        Returns:
            True if token is valid, False otherwise
        """
        return not self.is_expired()
    
    def is_expired(self) -> bool:
        """Check if token is expired.
        
        Returns:
            True if token has expired, False otherwise
        """
        return datetime.now() > self.expires_at


@dataclass
class Product:
    """Product entity.
    
    Represents a product with its basic information.
    
    Attributes:
        product_id: Unique product identifier
        name: Product name
        description: Optional product description
        category: Optional product category
        producer_name: Optional producer/manufacturer name
        price: Optional product price
    """
    product_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    producer_name: Optional[str] = None
    price: Optional[float] = None


@dataclass
class TranslationRequest:
    """Translation request entity.
    
    Encapsulates all data needed for a translation operation.
    
    Attributes:
        text: Text to translate
        target_languages: List of target language codes (e.g., ["pol", "eng"])
        content_type: Type of content being translated (name, description, etc.)
        category: Optional product category for context
    """
    text: str
    target_languages: List[str]
    content_type: str
    category: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationRequest':
        """Create TranslationRequest from dictionary.
        
        Args:
            data: Dictionary containing request data
            
        Returns:
            TranslationRequest instance
        """
        return cls(
            text=data.get('text', ''),
            target_languages=data.get('target_languages', []),
            content_type=data.get('content_type', ''),
            category=data.get('category')
        )


@dataclass
class TranslationResponse:
    """Translation response entity.
    
    Encapsulates the result of a translation operation.
    
    Attributes:
        translations: Dictionary mapping language codes to translated text
        tokens_used: Number of tokens consumed by the translation
        model: Name of the model/strategy used for translation
        timestamp: When the translation was performed (defaults to now)
    """
    translations: Dict[str, str]
    tokens_used: int
    model: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProductDescription:
    """Product description entity.
    
    Represents product description data for a specific language.
    
    Attributes:
        lang_id: Language code (e.g., "pol", "eng")
        shop_id: Shop identifier
        name: Product name in this language
        description: Product description in this language
        meta_title: SEO meta title in this language
        meta_description: SEO meta description in this language
        meta_keywords: SEO keywords in this language
    """
    lang_id: str
    shop_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


@dataclass
class VATValidationResult:
    """VAT validation result entity.
    
    Represents the result of VAT number validation via VIES service.
    
    Attributes:
        valid: Whether the VAT number is valid
        name: Company name (if valid)
        address: Company address (if valid)
        country_code: Country code validated
        vat_number: VAT number validated
    """
    valid: bool
    name: Optional[str] = None
    address: Optional[str] = None
    country_code: Optional[str] = None
    vat_number: Optional[str] = None


@dataclass
class APIResponse:
    """Generic API response entity.
    
    Represents a standardized API response structure.
    
    Attributes:
        status_code: HTTP status code
        reason: HTTP reason phrase
        data: Response data (JSON parsed)
        success: Whether the request was successful
    """
    status_code: int
    reason: str
    data: Optional[Dict[str, Any]] = None
    success: bool = field(init=False)
    
    def __post_init__(self):
        """Set success based on status code."""
        self.success = 200 <= self.status_code < 300
