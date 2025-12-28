"""
VAT validation routes using new architecture.
"""
from flask import Blueprint, request
from app.core.services.vies_service import ViesService
from app.config.settings import get_vies_wsdl
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("vies")
vies_bp = Blueprint("vies", __name__)


def get_vies_service() -> ViesService:
    """
    Get ViesService instance with dependency injection.

    Returns:
        Configured ViesService instance
    """
    wsdl = get_vies_wsdl()
    return ViesService(wsdl)


@vies_bp.route("/validate", methods=["POST"])
def validate_vat():
    """
    Validate VAT number using VIES service.

    Returns:
        JSON response with validation result
    """
    try:
        request_data = request.get_json()
        if (
            not request_data
            or "country_code" not in request_data
            or "vat_number" not in request_data
        ):
            return {"error": "Invalid request data"}, 400

        country_code = request_data["country_code"]
        vat_number = request_data["vat_number"]

        vies_service = get_vies_service()
        result = vies_service.validate_vat(country_code, vat_number)

        if "valid" in result and result["valid"]:
            logger.info(f"Validated VAT: {country_code}{vat_number}")
            return result, 200
        elif "error" in result:
            logger.error(f"VAT validation error: {result['error']}")
            return {"error": result["error"]}, 500
        else:
            logger.warning(f"Invalid VAT: {country_code}{vat_number}")
            return {"error": "VAT Number is not valid"}, 400

    except Exception as e:
        logger.error(f"Error validating VAT: {e}")
        return handle_generic_error(e)
