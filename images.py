from flask import jsonify
from config import (
    CLIENT_SECRET,
    CLIENT_USERNAME,
    BASE_URL,
)
from api.auth import Auth
from api.products_info import ProductApi
from utils import (
    parse_product_images,
)


def handle_images_request(request, product_id):
    """
    Handler for getting product images.
    """
    if request.method != "GET":
        return jsonify({"error": "Unsupported method!"}), 400

    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400
    elif product_id and request.method == "GET":
        auth = Auth(CLIENT_USERNAME, CLIENT_SECRET, BASE_URL)
        token = auth.get_token()
        product_api = ProductApi(BASE_URL, token, "v3")

        payload = {
            "params": {
                "returnElements": ["pictures"],
                "productParams": [{"productId": product_id}],
            }
        }

        try:
            status_code, reason, product_data = product_api.get_product_images(
                data=payload
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if status_code == 200:
            images = parse_product_images(product_data)
            return images
        else:
            return jsonify({"error": reason}), status_code
