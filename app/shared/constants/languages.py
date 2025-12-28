"""
Language mappings for Translate-Descriptions application.

This module provides language code to full name mappings
and reverse mappings for translation operations.
"""

# Language code to full name mapping
LANGUAGE_MAP = {
    "pol": "Polish",
    "bul": "Bulgarian",
    "cze": "Czech",
    "dut": "Dutch",
    "eng": "English",
    "est": "Estonian",
    "fre": "French",
    "ger": "German",
    "gre": "Greek",
    "hun": "Hungarian",
    "ita": "Italian",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "rum": "Romanian",
    "scr": "Croatian",
    "slo": "Slovak",
    "slv": "Slovenian",
    "spa": "Spanish",
    "ukr": "Ukrainian",
}

# Reverse mapping: full name to language code
REVERSE_LANGUAGE_MAP = {v: k for k, v in LANGUAGE_MAP.items()}

# Translation type constants
TRANSLATION_TYPES = {
    "productName": "product_name",
    "productLongDescription": "product_description",
    "productMetaTitle": "meta_title",
    "productMetaDescription": "meta_description",
    "productMetaKeywords": "keywords",
}


def get_language_name(lang_code: str) -> str:
    """Get full language name from code.
    
    Args:
        lang_code: Language code (e.g., "pol", "eng")
        
    Returns:
        Full language name or the code if not found
    """
    return LANGUAGE_MAP.get(lang_code, lang_code)


def get_language_code(lang_name: str) -> str:
    """Get language code from full name.
    
    Args:
        lang_name: Full language name (e.g., "Polish", "English")
        
    Returns:
        Language code or the name if not found
    """
    return REVERSE_LANGUAGE_MAP.get(lang_name, lang_name)
