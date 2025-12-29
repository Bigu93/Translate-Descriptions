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

    def translate_product(self) -> Tuple[Any, int]:
        """
        Handle product translation request with complex payload structure.

        Expected payload:
        {
            "params": {
                "products": [
                    {
                        "productIdent": {"productIdentType": "id", "identValue": "52"},
                        "productInfo": {"description": "...", "name": "...", "category": "..."},
                        "productDescriptionsLangData": [...]
                    }
                ]
            }
        }

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            params = data.get("params")
            if not params:
                return jsonify(error="params is required"), 400

            products = params.get("products")
            if not products or not isinstance(products, list):
                return jsonify(error="params.products list is required"), 400

            if len(products) == 0:
                return jsonify(error="params.products list cannot be empty"), 400

            # Process first product (as per client expectation)
            product = products[0]
            product_info = product.get("productInfo", {})
            existing_lang_data = product.get("productDescriptionsLangData", [])

            # Extract source data for translation
            source_name = product_info.get("name", "")
            source_description = product_info.get("description", "")
            category = product_info.get("category", "")

            if not source_name and not source_description:
                return jsonify(error="At least one of name or description is required in productInfo"), 400

            # Get languages from existing productDescriptionsLangData
            languages = []
            for lang_data in existing_lang_data:
                lang_id = lang_data.get("langId")
                if lang_id and lang_id not in languages:
                    languages.append(lang_id)

            if not languages:
                return jsonify(error="No languages found in productDescriptionsLangData"), 400

            # Translate name if present
            translated_names = {}
            if source_name:
                name_translations, name_tokens = self.translation_service.translate(
                    text=source_name,
                    translate_type="name",
                    languages=languages
                )
                translated_names = name_translations

            # Translate description if present
            translated_descriptions = {}
            if source_description:
                desc_translations, desc_tokens = self.translation_service.translate(
                    text=source_description,
                    translate_type="description",
                    languages=languages
                )
                translated_descriptions = desc_translations

            # Build response in the expected format
            result = {
                "params": {
                    "products": [
                        {
                            "productIdent": product.get("productIdent"),
                            "productInfo": product_info,
                            "productDescriptionsLangData": []
                        }
                    ]
                }
            }

            # Populate translated data for each language
            for lang_data in existing_lang_data:
                lang_id = lang_data.get("langId")
                shop_id = lang_data.get("shopId", 0)

                translated_lang_data = {
                    "langId": lang_id,
                    "shopId": shop_id
                }

                # Add translated name
                if lang_id in translated_names:
                    translated_lang_data["productName"] = translated_names[lang_id]

                # Add translated description
                if lang_id in translated_descriptions:
                    translated_lang_data["productLongDescription"] = translated_descriptions[lang_id]

                # Copy any other fields from original lang_data
                for key, value in lang_data.items():
                    if key not in ["langId", "shopId", "productName", "productLongDescription"]:
                        translated_lang_data[key] = value

                result["params"]["products"][0]["productDescriptionsLangData"].append(translated_lang_data)

            logger.info(
                f"Product translation completed: "
                f"product_id={product.get('productIdent', {}).get('identValue')}, "
                f"languages={len(languages)}"
            )

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error translating product: {e}")
            return handle_generic_error(e)
