"""
Description rephrasing routes using new architecture.
"""
from flask import Blueprint, request
from app.core.services.rephrase_service import RephraseService
from app.core.strategies.openai_strategy import OpenAIStrategy
from app.config.settings import get_openai_api_key, get_openai_model
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("rephrase")
rephrase_bp = Blueprint("rephrase", __name__)


def get_rephrase_service() -> RephraseService:
    """
    Get RephraseService instance with dependency injection.

    Returns:
        Configured RephraseService instance
    """
    api_key = get_openai_api_key()
    model = get_openai_model()
    strategy = OpenAIStrategy(api_key=api_key, model=model)
    return RephraseService(strategy)


@rephrase_bp.route("/rephrase-description", methods=["POST"])
def rephrase_description():
    """
    Handle description rephrasing request.

    Returns:
        JSON response with rephrased description
    """
    try:
        data = request.get_json()
        if not data:
            return {"error": "Empty payload!"}, 400

        description = data.get("description")
        languages = data.get("languages")

        if not description:
            return {"error": "description is required"}, 400

        if not languages or not isinstance(languages, list):
            return {"error": "languages list is required"}, 400

        rephrase_service = get_rephrase_service()
        rephrased, tokens_used = rephrase_service.rephrase_description(
            description=description,
            languages=languages
        )

        logger.info(
            f"Description rephrasing completed: "
            f"languages={len(languages)}, tokens_used={tokens_used}"
        )

        return {
            "rephrased": rephrased,
            "tokens_used": tokens_used
        }, 200

    except Exception as e:
        logger.error(f"Error rephrasing description: {e}")
        return handle_generic_error(e)
