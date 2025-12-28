"""
Description generation routes using new architecture.
"""
from flask import Blueprint, request
from app.core.services.generation_service import GenerationService
from app.core.strategies.openai_strategy import OpenAIStrategy
from app.config.settings import get_openai_api_key, get_openai_model
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("generate")
generate_bp = Blueprint("generate", __name__)


def get_generation_service() -> GenerationService:
    """
    Get GenerationService instance with dependency injection.

    Returns:
        Configured GenerationService instance
    """
    api_key = get_openai_api_key()
    model = get_openai_model()
    strategy = OpenAIStrategy(api_key=api_key, model=model)
    return GenerationService(strategy)


@generate_bp.route("/generate-description", methods=["POST"])
def generate_description():
    """
    Handle description generation request.

    Returns:
        JSON response with generated description
    """
    try:
        data = request.get_json()
        if not data:
            return {"error": "Empty payload!"}, 400

        product_name = data.get("productName")
        languages = data.get("languages")

        if not product_name:
            return {"error": "productName is required"}, 400

        if not languages or not isinstance(languages, list):
            return {"error": "languages list is required"}, 400

        generation_service = get_generation_service()
        descriptions, tokens_used = generation_service.generate_description(
            product_name=product_name,
            languages=languages
        )

        logger.info(
            f"Description generation completed: "
            f"product={product_name}, languages={len(languages)}, tokens_used={tokens_used}"
        )

        return {
            "descriptions": descriptions,
            "tokens_used": tokens_used
        }, 200

    except Exception as e:
        logger.error(f"Error generating description: {e}")
        return handle_generic_error(e)
