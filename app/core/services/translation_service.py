"""
Translation service for Translate-Descriptions application.

This module implements the business logic for translation operations,
using the Strategy Pattern for pluggable translation providers.
"""

from typing import List, Dict, Optional
from app.core.domain.interfaces import ITranslationService
from app.core.domain.models import TranslationRequest, TranslationResponse
from app.core.domain.exceptions import TranslationError
from app.core.domain.interfaces import ICacheProvider, ILogger


class TranslationService(ITranslationService):
    """Service for handling translation operations.
    
    Implements ITranslationService interface using dependency injection.
    Provides caching and delegates to translation strategy.
    """
    
    def __init__(
        self,
        translation_strategy,
        cache_provider: ICacheProvider,
        logger: ILogger
    ):
        """Initialize translation service.
        
        Args:
            translation_strategy: Translation strategy implementation
            cache_provider: Cache provider for caching results
            logger: Logger instance
        """
        self._strategy = translation_strategy
        self._cache = cache_provider
        self._logger = logger
    
    def translate_product_content(
        self,
        request: TranslationRequest
    ) -> TranslationResponse:
        """Translate product content using configured strategy.
        
        Args:
            request: Translation request with text, languages, and content type
            
        Returns:
            Translation response with translated text and metadata
        """
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get from cache
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            if self._logger:
                self._logger.debug(f"Cache hit for translation: {cache_key}")
            return TranslationResponse(**cached_result)
        
        # Perform translation
        translations = self._strategy.translate(
            text=request.text,
            target_languages=request.target_languages,
            content_type=request.content_type,
            category=request.category
        )
        
        # Create response
        response = TranslationResponse(
            translations=translations,
            tokens_used=0,  # Would be set by strategy
            model=self._strategy.get_provider_name(),
            timestamp=request.timestamp if hasattr(request, 'timestamp') else None
        )
        
        # Cache result
        cache_data = {
            "translations": translations,
            "tokens_used": response.tokens_used,
            "model": response.model,
            "timestamp": response.timestamp.isoformat() if response.timestamp else None
        }
        self._cache.set(cache_key, cache_data, ttl=3600)  # 1 hour
        
        if self._logger:
            self._logger.info(
                f"Translation completed",
                content_type=request.content_type,
                languages_count=len(request.target_languages),
                cached=False
            )
        
        return response
    
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
        request = TranslationRequest(
            text=text,
            target_languages=target_languages,
            content_type=content_type,
            category=category
        )
        
        response = self.translate_product_content(request)
        return response.translations
    
    def _generate_cache_key(self, request: TranslationRequest) -> str:
        """Generate cache key for translation request.
        
        Args:
            request: Translation request
            
        Returns:
            Cache key string
        """
        import hashlib
        import json
        
        key_data = {
            "text": request.text,
            "languages": sorted(request.target_languages),
            "type": request.content_type,
            "category": request.category
        }
        key_hash = hashlib.md5(json.dumps(key_data).encode()).hexdigest()
        return f"translation:{key_hash}"
