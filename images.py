from flask import jsonify
from utils import parse_product_images, get_product_api


def handle_images_request(request, product_id):
    """
    Handler for getting product images.
    """
    product_api = get_product_api()

    if request.method != "GET":
        return jsonify({"error": "Unsupported method!"}), 400

    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400
    elif product_id and request.method == "GET":
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
        elif status_code == 207:
            return jsonify({"error": "Brak towaru"}), status_code
        else:
            return jsonify({"error": reason}), status_code
