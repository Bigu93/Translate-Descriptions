"""
OpenAI translation strategy for Translate-Descriptions application.

This module implements the translation strategy using OpenAI's API,
following the Strategy Pattern for pluggable translation providers.
"""

import json
from typing import List, Dict, Optional
from openai import OpenAI, APIError, APIConnectionError
from app.core.strategies.base_strategy import TranslationStrategy
from app.core.domain.exceptions import TranslationError, ExternalAPIError
from app.core.domain.interfaces import ILogger
from app.shared.constants.languages import get_language_name


class OpenAIStrategy(TranslationStrategy):
    """OpenAI-based translation strategy.
    
    Implements TranslationStrategy interface using OpenAI's API.
    Features:
    - Retry logic with exponential backoff
    - Proper error handling
    - Structured logging
    """
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 30,
        logger: ILogger = None
    ):
        """Initialize OpenAI strategy.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (e.g., "gpt-4")
            timeout: Request timeout in seconds
            logger: Logger instance
        """
        self._logger = logger
        self._model = model
        self._client = OpenAI(api_key=api_key, timeout=timeout)
        if self._logger:
            self._logger.info(
                f"Initialized OpenAI strategy with model: {model}"
            )
    
    def translate(
        self,
        text: str,
        target_languages: List[str],
        content_type: str,
        category: Optional[str] = None
    ) -> Dict[str, str]:
        """Translate text to target languages using OpenAI.
        
        Args:
            text: Text to translate
            target_languages: List of target language codes (e.g., ["pol", "eng"])
            content_type: Type of content (name, description, etc.)
            category: Optional product category for context
            
        Returns:
            Dictionary mapping language codes to translated text
            
        Raises:
            TranslationError: If translation fails
        """
        # Get system prompt based on content type
        system_prompt = self._get_system_prompt(content_type)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": self._build_user_prompt(text, target_languages, category)
            }
        ]
        
        try:
            if self._logger:
                self._logger.debug(
                    f"Translating text with OpenAI",
                    content_type=content_type,
                    target_languages=target_languages,
                    category=category
                )
            
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.6,
                max_tokens=4096
            )
            
            # Parse response
            response_content = response.choices[0].message.content.strip()
            translations = self._parse_response(response_content)
            
            if self._logger:
                self._logger.info(
                    f"Translation successful",
                    tokens_used=response.usage.total_tokens,
                    languages_count=len(translations)
                )
            
            return translations
            
        except APIError as e:
            error_msg = f"OpenAI API error: {e}"
            if self._logger:
                self._logger.error(error_msg, status_code=e.status_code)
            raise ExternalAPIError(error_msg, status_code=e.status_code) from e
        except APIConnectionError as e:
            error_msg = f"OpenAI connection error: {e}"
            if self._logger:
                self._logger.error(error_msg)
            raise TranslationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during translation: {e}"
            if self._logger:
                self._logger.error(error_msg)
            raise TranslationError(error_msg) from e
    
    def _get_system_prompt(self, content_type: str) -> str:
        """Get system prompt based on content type.
        
        Args:
            content_type: Type of content being translated
            
        Returns:
            System prompt string
        """
        from app.config.settings import Settings
        import yaml
        
        settings = Settings.get_instance()
        
        # Map content types to prompt files
        prompt_files = {
            "productName": "product_name.yaml",
            "productLongDescription": "product_description.yaml",
            "productMetaTitle": "meta_title.yaml",
            "productMetaDescription": "meta_description.yaml",
            "productMetaKeywords": "keywords.yaml",
        }
        
        prompt_file = prompt_files.get(content_type)
        if not prompt_file:
            return "You are a language translator. Translate the provided text."
        
        # Load prompt from YAML file
        prompt_path = f"app/config/prompts/{prompt_file}"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
                return prompt_data.get('prompt', '')
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Failed to load prompt file: {e}")
            return "You are a language translator. Translate the provided text."
    
    def _build_user_prompt(
        self,
        text: str,
        target_languages: List[str],
        category: Optional[str]
    ) -> str:
        """Build user prompt for translation.
        
        Args:
            text: Text to translate
            target_languages: List of target language codes
            category: Optional product category
            
        Returns:
            Formatted user prompt string
        """
        # Convert language codes to full names
        language_names = [
            get_language_name(lang) for lang in target_languages
        ]
        
        prompt = f"[{text}] Langs:[{','.join(language_names)}]"
        
        if category:
            prompt += f" Category:[{category}]"
        
        return prompt
    
    def _parse_response(self, response_content: str) -> Dict[str, str]:
        """Parse OpenAI response content.
        
        Args:
            response_content: Raw response content from OpenAI
            
        Returns:
            Dictionary mapping language codes to translated text
        """
        # Log the raw response for debugging
        if self._logger:
            self._logger.debug(f"Raw OpenAI response content: {repr(response_content)}")
        
        try:
            # Try to parse as JSON directly
            parsed = json.loads(response_content)
            
            # Convert language names back to codes
            translations = {}
            for lang_name, translated_text in parsed.items():
                # Map back to language code
                from app.shared.constants.languages import REVERSE_LANGUAGE_MAP
                lang_code = REVERSE_LANGUAGE_MAP.get(lang_name, lang_name)
                if lang_code:
                    translations[lang_code] = translated_text
            
            return translations
            
        except json.JSONDecodeError as e:
            # Log the JSON decode error
            if self._logger:
                self._logger.warning(f"Direct JSON parse failed: {e}")
            
            # Try to extract JSON from response
            try:
                json_start = response_content.index("{")
                json_end = response_content.rindex("}") + 1
                json_str = response_content[json_start:json_end]
                
                if self._logger:
                    self._logger.debug(f"Extracted JSON substring: {repr(json_str)}")
                
                parsed = json.loads(json_str)
                
                # Convert language names back to codes
                translations = {}
                for lang_name, translated_text in parsed.items():
                    from app.shared.constants.languages import REVERSE_LANGUAGE_MAP
                    lang_code = REVERSE_LANGUAGE_MAP.get(lang_name, lang_name)
                    if lang_code:
                        translations[lang_code] = translated_text
                
                return translations
                
            except ValueError as e:
                # This is the "substring not found" error
                if self._logger:
                    self._logger.error(
                        f"Failed to find JSON delimiters in response. "
                        f"Response length: {len(response_content)}. "
                        f"Error: {e}"
                    )
                raise TranslationError(f"Failed to parse translation response: substring not found") from e
            except json.JSONDecodeError as e:
                if self._logger:
                    self._logger.error(
                        f"Found JSON delimiters but failed to parse JSON. "
                        f"Error: {e}"
                    )
                raise TranslationError(f"Failed to parse translation response: invalid JSON") from e
    
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        from app.shared.constants.languages import LANGUAGE_MAP
        return list(LANGUAGE_MAP.keys())
    
    def get_provider_name(self) -> str:
        """Return the name of this translation provider.
        
        Returns:
            Provider name string
        """
        return "OpenAI"
