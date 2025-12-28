"""
Input validators for API requests.
"""
from typing import Optional, List
from app.infrastructure.logging.structured_logger import get_logger
from app.core.domain.exceptions import ValidationError


logger = get_logger("input_validators")


def validate_translation_request(data: dict) -> Optional[str]:
    """
    Validate translation request data.

    Args:
        data: Request data dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    user_prompt = data.get("userPrompt")
    translate_type = data.get("translateType")
    languages = data.get("languages")

    if not user_prompt:
        return "userPrompt is required"

    if not translate_type:
        return "translateType is required"

    valid_types = ["name", "description", "meta_title", "meta_description", "keywords"]
    if translate_type not in valid_types:
        return f"Invalid translateType. Must be one of: {', '.join(valid_types)}"

    if not languages or not isinstance(languages, list):
        return "languages list is required"

    if len(languages) == 0:
        return "languages list cannot be empty"

    return None


def validate_generation_request(data: dict) -> Optional[str]:
    """
    Validate description generation request data.

    Args:
        data: Request data dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    product_name = data.get("productName")
    languages = data.get("languages")

    if not product_name:
        return "productName is required"

    if not languages or not isinstance(languages, list):
        return "languages list is required"

    if len(languages) == 0:
        return "languages list cannot be empty"

    return None


def validate_rephrase_request(data: dict) -> Optional[str]:
    """
    Validate description rephrasing request data.

    Args:
        data: Request data dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    description = data.get("description")
    languages = data.get("languages")

    if not description:
        return "description is required"

    if not languages or not isinstance(languages, list):
        return "languages list is required"

    if len(languages) == 0:
        return "languages list cannot be empty"

    return None


def validate_product_description_request(data: dict) -> Optional[str]:
    """
    Validate product description request data.

    Args:
        data: Request data dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    product_id = data.get("product_id")
    shop_id = data.get("shop_id")

    if not product_id:
        return "product_id is required"

    if not shop_id:
        return "shop_id is required"

    return None


def validate_product_images_request(data: dict) -> Optional[str]:
    """
    Validate product images request data.

    Args:
        data: Request data dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    product_ids = data.get("product_ids")

    if not product_ids or not isinstance(product_ids, list):
        return "product_ids list is required"

    if len(product_ids) == 0:
        return "product_ids list cannot be empty"

    return None


def validate_authentication_request(data: dict) -> Optional[str]:
    """
    Validate authentication request data.

    Args:
        data: Request data dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    username = data.get("username")
    password = data.get("password")

    if not username:
        return "username is required"

    if not password:
        return "password is required"

    if len(username) < 3:
        return "username must be at least 3 characters"

    if len(password) < 6:
        return "password must be at least 6 characters"

    return None


def validate_language_codes(languages: List[str]) -> Optional[str]:
    """
    Validate language codes.

    Args:
        languages: List of language codes

    Returns:
        Error message if validation fails, None otherwise
    """
    valid_languages = [
        "eng", "ger", "fra", "spa", "ita", "pol", "rus", "chi", "jpn", "kor"
    ]

    for lang in languages:
        if lang not in valid_languages:
            return f"Invalid language code: {lang}. Valid codes are: {', '.join(valid_languages)}"

    return None


def validate_pagination_params(page: int, limit: int) -> Optional[str]:
    """
    Validate pagination parameters.

    Args:
        page: Page number
        limit: Results per page

    Returns:
        Error message if validation fails, None otherwise
    """
    if page < 0:
        return "page must be >= 0"

    if limit < 1 or limit > 100:
        return "limit must be between 1 and 100"

    return None
