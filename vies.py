from flask import jsonify
from zeep import Client, exceptions
from config import VIES_WSDL


def handle_vies_request(request):
    if request.method != "POST":
        return jsonify({"error": f"Unsupported method {request.method}"}), 405

    request_data = request.get_json()
    if (
        not request_data
        or "country_code" not in request_data
        or "vat_number" not in request_data
    ):
        return jsonify({"error": "Invalid request data"}), 400

    country_code = request_data["country_code"]
    vat_number = request_data["vat_number"]

    result = validate_vat(country_code, vat_number)
    if "valid" in result and result["valid"]:
        return jsonify(result), 200
    elif "error" in result:
        return jsonify({"error": result["error"]}), 500
    else:
        return jsonify({"error": "VAT Number is not valid"}), 400


def validate_vat(country_code, vat_number):
    client = Client(VIES_WSDL)
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            result = client.service.checkVat(
                countryCode=country_code, vatNumber=vat_number
            )
            return {
                "valid": result.valid,
                "name": result.name,
                "address": result.address,
            }
        except exceptions.Fault as fault:
            return {"error": str(fault)}
        except Exception as e:
            attempts += 1
            if attempts == max_attempts:
                return {"error": str(e)}
