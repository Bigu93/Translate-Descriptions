"""
Request handlers for translation-related operations.
"""
from typing import Any, Dict, List, Tuple
from flask import request, jsonify
from app.infrastructure.logging.structured_logger import get_logger
from app.core.services.translation_service import TranslationService
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("translation_handlers")


class TranslationHandlers:
    """
    Handlers for translation-related API requests.
    """

    def __init__(self, translation_service: TranslationService):
        """
        Initialize translation handlers.

        Args:
            translation_service: Translation service instance
        """
        self.translation_service = translation_service
        logger.info("TranslationHandlers initialized")

    def translate(self) -> Tuple[Any, int]:
        """
        Handle translation request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = TranslationHandlers(service)
            >>> response, status = handlers.translate()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            text_to_translate = data.get("userPrompt")
            translate_type = data.get("translateType")
            langs_list = data.get("languages")

            if not text_to_translate:
                return jsonify(error="userPrompt is required"), 400

            if not translate_type:
                return jsonify(error="translateType is required"), 400

            if not langs_list or not isinstance(langs_list, list):
                return jsonify(error="languages list is required"), 400

            # Validate translate type
            valid_types = ["name", "description", "meta_title", "meta_description", "keywords"]
            if translate_type not in valid_types:
                return jsonify(
                    error=f"Invalid translateType. Must be one of: {', '.join(valid_types)}"
                ), 400

            # Perform translation
            translations, tokens_used = self.translation_service.translate(
                text=text_to_translate,
                translate_type=translate_type,
                languages=langs_list
            )

            logger.info(
                f"Translation completed: type={translate_type}, "
                f"languages={len(langs_list)}, tokens_used={tokens_used}"
            )

            return jsonify({
                "translations": translations,
                "tokens_used": tokens_used
            }), 200

        except Exception as e:
            logger.error(f"Error in translation: {e}")
            return handle_generic_error(e)

    def generate_description(self) -> Tuple[Any, int]:
        """
        Handle description generation request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = TranslationHandlers(service)
            >>> response, status = handlers.generate_description()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            product_name = data.get("productName")
            languages = data.get("languages")

            if not product_name:
                return jsonify(error="productName is required"), 400

            if not languages or not isinstance(languages, list):
                return jsonify(error="languages list is required"), 400

            # Generate descriptions
            descriptions, tokens_used = self.translation_service.generate_description(
                product_name=product_name,
                languages=languages
            )

            logger.info(
                f"Description generation completed: "
                f"product={product_name}, languages={len(languages)}, tokens_used={tokens_used}"
            )

            return jsonify({
                "descriptions": descriptions,
                "tokens_used": tokens_used
            }), 200

        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return handle_generic_error(e)

    def rephrase_description(self) -> Tuple[Any, int]:
        """
        Handle description rephrasing request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = TranslationHandlers(service)
            >>> response, status = handlers.rephrase_description()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            description = data.get("description")
            languages = data.get("languages")

            if not description:
                return jsonify(error="description is required"), 400

            if not languages or not isinstance(languages, list):
                return jsonify(error="languages list is required"), 400

            # Rephrase descriptions
            rephrased, tokens_used = self.translation_service.rephrase_description(
                description=description,
                languages=languages
            )

            logger.info(
                f"Description rephrasing completed: "
                f"languages={len(languages)}, tokens_used={tokens_used}"
            )

            return jsonify({
                "rephrased": rephrased,
                "tokens_used": tokens_used
            }), 200

        except Exception as e:
            logger.error(f"Error rephrasing description: {e}")
            return handle_generic_error(e)

    def translate_product_name(self) -> Tuple[Any, int]:
        """
        Handle product name translation request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = TranslationHandlers(service)
            >>> response, status = handlers.translate_product_name()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            product_name = data.get("productName")
            languages = data.get("languages")

            if not product_name:
                return jsonify(error="productName is required"), 400

            if not languages or not isinstance(languages, list):
                return jsonify(error="languages list is required"), 400

            # Translate product name
            translations, tokens_used = self.translation_service.translate(
                text=product_name,
                translate_type="name",
                languages=languages
            )

            logger.info(
                f"Product name translation completed: "
                f"product={product_name}, languages={len(languages)}, tokens_used={tokens_used}"
            )

            return jsonify({
                "translations": translations,
                "tokens_used": tokens_used
            }), 200

        except Exception as e:
            logger.error(f"Error translating product name: {e}")
            return handle_generic_error(e)
