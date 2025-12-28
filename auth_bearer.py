"""
Bearer token authentication routes using new architecture.
"""
from flask import Blueprint
from app.core.services.auth_service import AuthService
from app.infrastructure.database.bearer_repository import BearerRepository
from app.infrastructure.database.connection_pool import get_connection_pool
from app.presentation.web.middleware.auth_middleware import require_auth
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("auth_bearer")
auth_bp = Blueprint("auth", __name__)


def get_auth_service() -> AuthService:
    """
    Get AuthService instance with dependency injection.

    Returns:
        Configured AuthService instance
    """
    connection_pool = get_connection_pool()
    bearer_repository = BearerRepository(connection_pool)
    return AuthService(bearer_repository)


@auth_bp.route("/generate_auth_token", methods=["POST"])
def generate_auth_token():
    """
    Generate a new bearer authentication token.

    Returns:
        JSON response with generated token
    """
    try:
        auth_service = get_auth_service()
        token = auth_service.generate_bearer_token()

        logger.info(f"Generated new bearer token: {token[:10]}...")
        return {"token": token["token"], "expires_at": token["expires_at"]}, 201

    except Exception as e:
        logger.error(f"Error generating bearer token: {e}")
        return handle_generic_error(e)


@auth_bp.route("/revoke_auth_token", methods=["POST"])
@require_auth(lambda token: get_auth_service().validate_token(token))
def revoke_auth_token():
    """
    Revoke a bearer authentication token.

    Returns:
        JSON response with revocation status
    """
    try:
        auth_service = get_auth_service()
        success = auth_service.revoke_token()

        if success:
            logger.info("Bearer token revoked successfully")
            return {"message": "Token revoked successfully"}, 200
        else:
            logger.warning("Bearer token not found")
            return {"error": "Token not found"}, 404

    except Exception as e:
        logger.error(f"Error revoking bearer token: {e}")
        return handle_generic_error(e)


@auth_bp.route("/protected", methods=["GET"])
@require_auth(lambda token: get_auth_service().validate_token(token))
def protected_route():
    """
    Protected route that requires authentication.

    Returns:
        JSON response confirming access
    """
    return {"message": "You have access to this protected route"}, 200
