"""
Token management routes using new architecture.
"""
from flask import Blueprint
from app.core.services.token_service import TokenService
from app.infrastructure.database.token_repository import TokenRepository
from app.infrastructure.database.connection_pool import get_connection_pool
from app.presentation.web.middleware.auth_middleware import require_auth
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("tokens")
token_bp = Blueprint("token", __name__)


def get_token_service() -> TokenService:
    """
    Get TokenService instance with dependency injection.

    Returns:
        Configured TokenService instance
    """
    connection_pool = get_connection_pool()
    token_repository = TokenRepository(connection_pool)
    return TokenService(token_repository)


@token_bp.route("/generate-token", methods=["GET"])
def generate_token():
    """
    Generate a new API token.

    Returns:
        JSON response with generated token
    """
    try:
        token_service = get_token_service()
        token = token_service.generate_token()

        logger.info(f"Generated new token: {token[:10]}...")
        return {"token": token}, 200

    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return handle_generic_error(e)


@token_bp.route("/cleanup", methods=["POST"])
@require_auth(lambda token: get_token_service().validate_token(token))
def cleanup_tokens():
    """
    Remove expired tokens from database.

    Returns:
        JSON response with cleanup results
    """
    try:
        token_service = get_token_service()
        removed_count = token_service.cleanup_expired_tokens()

        logger.info(f"Removed {removed_count} expired tokens")
        return {"message": f"Removed {removed_count} expired tokens"}, 200

    except Exception as e:
        logger.error(f"Error cleaning up tokens: {e}")
        return handle_generic_error(e)


@token_bp.route("/check", methods=["GET"])
@require_auth(lambda token: get_token_service().validate_token(token))
def check_all_tokens():
    """
    Check all tokens in the database.

    Returns:
        JSON response with list of tokens
    """
    try:
        token_service = get_token_service()
        tokens = token_service.get_all_tokens()

        logger.info(f"Found {len(tokens)} tokens in database")
        return {"tokens": tokens}, 200

    except Exception as e:
        logger.error(f"Error checking tokens: {e}")
        return handle_generic_error(e)


@token_bp.route("/check_setup", methods=["GET"])
@require_auth(lambda token: get_token_service().validate_token(token))
def check_database_setup():
    """
    Check if database setup is correct.

    Returns:
        JSON response with setup status
    """
    try:
        token_service = get_token_service()
        is_valid = token_service.check_database_setup()

        if is_valid:
            logger.info("Database setup appears to be correct")
            return {"message": "Database setup appears to be correct"}, 200
        else:
            logger.error("Database setup is incorrect")
            return {"error": "Database setup is incorrect"}, 500

    except Exception as e:
        logger.error(f"Error checking database setup: {e}")
        return handle_generic_error(e)
