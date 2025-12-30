"""
Service for generating product descriptions using AI.
"""
from typing import Dict, List, Tuple
from app.infrastructure.logging.structured_logger import get_logger
from app.core.strategies.base_strategy import TranslationStrategy
from app.core.domain.exceptions import TranslationError
from app.config.settings import load_prompt


logger = get_logger("generation_service")


class GenerationService:
    """
    Service for generating product descriptions using AI strategies.
    """

    def __init__(self, translation_strategy: TranslationStrategy):
        """
        Initialize the generation service.

        Args:
            translation_strategy: The translation strategy to use for generation
        """
        self.translation_strategy = translation_strategy
        logger.info("GenerationService initialized")

    def generate_description(
        self,
        product_name: str,
        languages: List[str]
    ) -> Tuple[Dict[str, str], int]:
        """
        Generate product descriptions for multiple languages.

        Args:
            product_name: The name of the product
            languages: List of language codes to generate descriptions for

        Returns:
            Tuple of (descriptions dict, tokens_used)

        Raises:
            TranslationError: If generation fails

        Example:
            >>> service = GenerationService(strategy)
            >>> descriptions, tokens = service.generate_description(
            ...     product_name="T-Shirt",
            ...     languages=["eng", "ger", "fra"]
            ... )
            >>> descriptions["eng"]
            'A comfortable t-shirt made from...'
        """
        try:
            prompt = load_prompt("generate")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{product_name}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to generate descriptions: empty response")

            logger.info(
                f"Generated descriptions for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error generating descriptions: {e}")
            raise TranslationError(f"Failed to generate descriptions: {e}") from e

    def generate_meta_title(
        self,
        product_name: str,
        languages: List[str]
    ) -> Tuple[Dict[str, str], int]:
        """
        Generate meta titles for multiple languages.

        Args:
            product_name: The name of the product
            languages: List of language codes to generate meta titles for

        Returns:
            Tuple of (meta_titles dict, tokens_used)

        Raises:
            TranslationError: If generation fails

        Example:
            >>> service = GenerationService(strategy)
            >>> titles, tokens = service.generate_meta_title(
            ...     product_name="T-Shirt",
            ...     languages=["eng", "ger"]
            ... )
            >>> titles["eng"]
            'T-Shirt - Buy Online'
        """
        try:
            prompt = load_prompt("meta_title")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{product_name}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to generate meta titles: empty response")

            logger.info(
                f"Generated meta titles for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error generating meta titles: {e}")
            raise TranslationError(f"Failed to generate meta titles: {e}") from e

    def generate_meta_description(
        self,
        product_name: str,
        languages: List[str]
    ) -> Tuple[Dict[str, str], int]:
        """
        Generate meta descriptions for multiple languages.

        Args:
            product_name: The name of the product
            languages: List of language codes to generate meta descriptions for

        Returns:
            Tuple of (meta_descriptions dict, tokens_used)

        Raises:
            TranslationError: If generation fails

        Example:
            >>> service = GenerationService(strategy)
            >>> descriptions, tokens = service.generate_meta_description(
            ...     product_name="T-Shirt",
            ...     languages=["eng", "ger"]
            ... )
            >>> descriptions["eng"]
            'Discover our high-quality t-shirt...'
        """
        try:
            prompt = load_prompt("meta_description")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{product_name}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to generate meta descriptions: empty response")

            logger.info(
                f"Generated meta descriptions for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error generating meta descriptions: {e}")
            raise TranslationError(f"Failed to generate meta descriptions: {e}") from e

    def generate_keywords(
        self,
        product_name: str,
        languages: List[str]
    ) -> Tuple[Dict[str, List[str]], int]:
        """
        Generate keywords for multiple languages.

        Args:
            product_name: The name of the product
            languages: List of language codes to generate keywords for

        Returns:
            Tuple of (keywords dict, tokens_used)

        Raises:
            TranslationError: If generation fails

        Example:
            >>> service = GenerationService(strategy)
            >>> keywords, tokens = service.generate_keywords(
            ...     product_name="T-Shirt",
            ...     languages=["eng", "ger"]
            ... )
            >>> keywords["eng"]
            ['t-shirt', 'clothing', 'fashion']
        """
        try:
            prompt = load_prompt("keywords")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{product_name}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to generate keywords: empty response")

            logger.info(
                f"Generated keywords for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error generating keywords: {e}")
            raise TranslationError(f"Failed to generate keywords: {e}") from e
