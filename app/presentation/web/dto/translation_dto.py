"""
Data Transfer Objects for translation-related requests and responses.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TranslationRequest:
    """DTO for translation requests."""
    user_prompt: str
    translate_type: str
    languages: List[str]

    def validate(self) -> Optional[str]:
        """
        Validate the translation request.

        Returns:
            Error message if validation fails, None otherwise
        """
        valid_types = ["name", "description", "meta_title", "meta_description", "keywords"]

        if not self.user_prompt:
            return "userPrompt is required"

        if not self.translate_type:
            return "translateType is required"

        if self.translate_type not in valid_types:
            return f"Invalid translateType. Must be one of: {', '.join(valid_types)}"

        if not self.languages or not isinstance(self.languages, list):
            return "languages list is required"

        if len(self.languages) == 0:
            return "languages list cannot be empty"

        return None


@dataclass
class TranslationResponse:
    """DTO for translation responses."""
    translations: Dict[str, str]
    tokens_used: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "translations": self.translations,
            "tokens_used": self.tokens_used
        }


@dataclass
class GenerationRequest:
    """DTO for description generation requests."""
    product_name: str
    languages: List[str]

    def validate(self) -> Optional[str]:
        """
        Validate the generation request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.product_name:
            return "productName is required"

        if not self.languages or not isinstance(self.languages, list):
            return "languages list is required"

        if len(self.languages) == 0:
            return "languages list cannot be empty"

        return None


@dataclass
class GenerationResponse:
    """DTO for description generation responses."""
    descriptions: Dict[str, str]
    tokens_used: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "descriptions": self.descriptions,
            "tokens_used": self.tokens_used
        }


@dataclass
class RephraseRequest:
    """DTO for description rephrasing requests."""
    description: str
    languages: List[str]

    def validate(self) -> Optional[str]:
        """
        Validate the rephrase request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.description:
            return "description is required"

        if not self.languages or not isinstance(self.languages, list):
            return "languages list is required"

        if len(self.languages) == 0:
            return "languages list cannot be empty"

        return None


@dataclass
class RephraseResponse:
    """DTO for description rephrasing responses."""
    rephrased: Dict[str, str]
    tokens_used: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "rephrased": self.rephrased,
            "tokens_used": self.tokens_used
        }
