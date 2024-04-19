from flask import jsonify
from urllib.parse import unquote
from config import (
    CLIENT_SECRET,
    CLIENT_USERNAME,
    BASE_URL,
)
from api.auth import Auth
from api.products_info import ProductApi
from utils import parse_product_data, parse_product_info, parse_full_product_info


def handle_product_data_request(request, product_id):
    """
    Handler for getting name and description data about product.
    """
    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400

    if request.method == "GET":
        shopid = request.args.get("shopid", default=0, type=int)
        langid = request.args.get("langid", default="pol", type=str)
        langid = None if langid.lower() == "all" else langid

        fields_query = request.args.get("fields", default="productName", type=str)
        fields_list = (
            None if fields_query.lower() == "all" else unquote(fields_query).split(",")
        )

        auth = Auth(CLIENT_USERNAME, CLIENT_SECRET, BASE_URL)
        token = auth.get_token()
        product_api = ProductApi(BASE_URL, token, "v3")

        try:
            status_code, reason, product_data = product_api.get_product_description(
                params=[product_id, shopid]
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if status_code == 200:
            data = parse_product_data(product_data, lang=langid, fields=fields_list)
            return jsonify(data)
        else:
            return jsonify({"error": reason}), status_code

    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"error": "Ęmpty payload!"}), 400

        if "params" not in data or "products" not in data["params"]:
            return jsonify({"error": "Unsupported JSON structure!"}), 400

        auth = Auth(CLIENT_USERNAME, CLIENT_SECRET, BASE_URL)
        token = auth.get_token()
        product_api = ProductApi(BASE_URL, token, "v3")

        try:
            status_code, reason, product_data = product_api.set_product_description(
                data=data
            )
            return jsonify({"message": "Zapisano!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


def handle_product_full_info_request(request, product_id):
    """
    Handler for getting full information about specific product.
    """
    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400

    if request.method == "GET":
        parts = product_id.split("-")

        if len(parts) == 2:
            product_id, size_id = parts
            return handle_full_product_with_size(request, product_id, size_id)
        else:
            return jsonify(
                {"error": "Product ID with size code needs to be provided!"}
            ), 400


def handle_product_info_request(request, product_id):
    """
    Handler for getting neccessary information about specific product.
    """
    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400

    if request.method == "GET":
        parts = product_id.split("-")

        if len(parts) == 2:
            product_id, size_id = parts
            return handle_product_with_size(request, product_id, size_id)
        else:
            return handle_product_without_size(request, product_id)


def handle_product_with_size(request, product_id, size_id):
    """
    Handler for getting information about specific product with size code.
    """
    auth = Auth(CLIENT_USERNAME, CLIENT_SECRET, BASE_URL)
    token = auth.get_token()
    product_api = ProductApi(BASE_URL, token, "v3")

    try:
        status_code, reason, product_data = product_api.get_product_info_with_sizecode(
            params=[product_id, size_id]
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if status_code == 200:
        data = parse_product_info(product_data)
        return jsonify(status_code, reason, data)
    else:
        return jsonify({"error": reason}), status_code


def handle_full_product_with_size(request, product_id, size_id):
    """
    Handler for getting full information about product with size code.
    """
    auth = Auth(CLIENT_USERNAME, CLIENT_SECRET, BASE_URL)
    token = auth.get_token()
    product_api = ProductApi(BASE_URL, token, "v3")

    try:
        status_code, reason, product_data = (
            product_api.get_product_full_info_with_sizecode(
                params=[product_id, size_id]
            )
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if status_code == 200:
        data = parse_full_product_info(product_data)
        return jsonify(status_code, reason, data)
    else:
        return jsonify({"error": reason}), status_code


def handle_product_without_size(request, product_id):
    """
    Handler for getting neccessary information about product.
    """
    return f"Product ID: {product_id}, Size ID not provided"
