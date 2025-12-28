"""
Base translation strategy for Translate-Descriptions application.

This module defines the abstract base class for translation strategies,
implementing the Strategy Pattern for interchangeable translation providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class TranslationStrategy(ABC):
    """Abstract base class for translation strategies.
    
    Defines the contract that all translation strategies must implement.
    Allows for runtime selection of translation providers (OpenAI, DeepL, Google, etc.)
    """
    
    @abstractmethod
    def translate(
        self,
        text: str,
        target_languages: List[str],
        content_type: str,
        category: Optional[str] = None
    ) -> Dict[str, str]:
        """Translate text to target languages.
        
        Args:
            text: Text to translate
            target_languages: List of target language codes (e.g., ["pol", "eng"])
            content_type: Type of content being translated (name, description, etc.)
            category: Optional product category for context
            
        Returns:
            Dictionary mapping language codes to translated text
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes.
        
        Returns:
            List of language codes supported by this strategy
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of the translation provider.
        
        Returns:
            Provider name (e.g., "OpenAI", "DeepL")
        """
        pass
