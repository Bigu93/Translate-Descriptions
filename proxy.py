"""
Proxy routes using new architecture.
"""
from flask import Blueprint, request
from app.core.services.translation_service import TranslationService
from app.core.strategies.openai_strategy import OpenAIStrategy
from app.config.settings import get_openai_api_key, get_openai_model
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("proxy")
proxy_bp = Blueprint("proxy", __name__)


def get_translation_service() -> TranslationService:
    """
    Get TranslationService instance with dependency injection.

    Returns:
        Configured TranslationService instance
    """
    api_key = get_openai_api_key()
    model = get_openai_model()
    strategy = OpenAIStrategy(api_key=api_key, model=model)
    return TranslationService(strategy)


@proxy_bp.route("/translate", methods=["POST"])
def proxy_translate():
    """
    Handle translation proxy request.

    Returns:
        JSON response with translations
    """
    try:
        if request.method != "POST":
            return {"error": f"Unsupported method {request.method}"}, 405

        request_data = request.get_json()
        if not request_data:
            return {"error": "Empty payload!"}, 400

        text_to_translate = request_data.get("userPrompt")
        translate_type = request_data.get("translateType")
        langs_list = request_data.get("languages")

        if not text_to_translate:
            return {"error": "userPrompt is required"}, 400

        if not translate_type:
            return {"error": "translateType is required"}, 400

        if not langs_list or not isinstance(langs_list, list):
            return {"error": "languages list is required"}, 400

        valid_types = ["name", "description", "meta_title", "meta_description", "keywords"]
        if translate_type not in valid_types:
            return {"error": f"Invalid translateType. Must be one of: {', '.join(valid_types)}"}, 400

        translation_service = get_translation_service()
        translations, tokens_used = translation_service.translate(
            text=text_to_translate,
            translate_type=translate_type,
            languages=langs_list
        )

        logger.info(
            f"Proxy translation completed: type={translate_type}, "
            f"languages={len(langs_list)}, tokens_used={tokens_used}"
        )

        return {
            "translations": translations,
            "tokens_used": tokens_used
        }, 200

    except Exception as e:
        logger.error(f"Error in proxy translation: {e}")
        return handle_generic_error(e)
