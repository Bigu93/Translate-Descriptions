"""
Service for rephrasing product descriptions using AI.
"""
from typing import Dict, List, Tuple
from app.infrastructure.logging.structured_logger import get_logger
from app.core.strategies.base_strategy import TranslationStrategy
from app.core.domain.exceptions import TranslationError
from app.config.settings import load_prompt


logger = get_logger("rephrase_service")


class RephraseService:
    """
    Service for rephrasing product descriptions using AI strategies.
    """

    def __init__(self, translation_strategy: TranslationStrategy):
        """
        Initialize rephrase service.

        Args:
            translation_strategy: The translation strategy to use for rephrasing
        """
        self.translation_strategy = translation_strategy
        logger.info("RephraseService initialized")

    def rephrase_description(
        self,
        description: str,
        languages: List[str]
    ) -> Tuple[Dict[str, str], int]:
        """
        Rephrase product descriptions for multiple languages.

        Args:
            description: The original description to rephrase
            languages: List of language codes to rephrase for

        Returns:
            Tuple of (rephrased_descriptions dict, tokens_used)

        Raises:
            TranslationError: If rephrasing fails

        Example:
            >>> service = RephraseService(strategy)
            >>> rephrased, tokens = service.rephrase_description(
            ...     description="A comfortable t-shirt made from cotton.",
            ...     languages=["eng", "ger", "fra"]
            ... )
            >>> rephrased["eng"]
            'A cozy cotton t-shirt for everyday wear.'
        """
        try:
            prompt = load_prompt("rephrase")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{description}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to rephrase descriptions: empty response")

            logger.info(
                f"Rephrased descriptions for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error rephrasing descriptions: {e}")
            raise TranslationError(f"Failed to rephrase descriptions: {e}") from e

    def rephrase_product_name(
        self,
        product_name: str,
        languages: List[str]
    ) -> Tuple[Dict[str, str], int]:
        """
        Rephrase product names for multiple languages.

        Args:
            product_name: The original product name to rephrase
            languages: List of language codes to rephrase for

        Returns:
            Tuple of (rephrased_names dict, tokens_used)

        Raises:
            TranslationError: If rephrasing fails

        Example:
            >>> service = RephraseService(strategy)
            >>> rephrased, tokens = service.rephrase_product_name(
            ...     product_name="Men's Cotton T-Shirt",
            ...     languages=["eng", "ger"]
            ... )
            >>> rephrased["eng"]
            'Men's Cotton Tee'
        """
        try:
            prompt = load_prompt("rephrase")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{product_name}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to rephrase product names: empty response")

            logger.info(
                f"Rephrased product names for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error rephrasing product names: {e}")
            raise TranslationError(f"Failed to rephrase product names: {e}") from e

    def rephrase_meta_title(
        self,
        meta_title: str,
        languages: List[str]
    ) -> Tuple[Dict[str, str], int]:
        """
        Rephrase meta titles for multiple languages.

        Args:
            meta_title: The original meta title to rephrase
            languages: List of language codes to rephrase for

        Returns:
            Tuple of (rephrased_titles dict, tokens_used)

        Raises:
            TranslationError: If rephrasing fails

        Example:
            >>> service = RephraseService(strategy)
            >>> rephrased, tokens = service.rephrase_meta_title(
            ...     meta_title="T-Shirt - Buy Online",
            ...     languages=["eng", "ger"]
            ... )
            >>> rephrased["eng"]
            'Shop T-Shirts Online'
        """
        try:
            prompt = load_prompt("rephrase")

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"[{meta_title}] Langs:[{','.join(languages)}]"
                }
            ]

            response_content, tokens_used = self.translation_strategy.translate(messages)

            if response_content is None:
                raise TranslationError("Failed to rephrase meta titles: empty response")

            logger.info(
                f"Rephrased meta titles for {len(languages)} languages, "
                f"using {tokens_used} tokens"
            )

            return response_content, tokens_used

        except Exception as e:
            logger.error(f"Error rephrasing meta titles: {e}")
            raise TranslationError(f"Failed to rephrase meta titles: {e}") from e
