from flask import jsonify
from urllib.parse import unquote
from config import (
    CLIENT_SECRET,
    CLIENT_USERNAME,
    BASE_URL,
)
from api.auth import Auth
from api.products_info import ProductApi
from utils import (
    parse_product_data,
)


def handle_product_data_request(request, product_id):
    if not product_id:
        return jsonify({"error": "Wymagane ID produktu!"}), 400

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
            return jsonify({"error": "Nie podano wysłano payloadu!"}), 400

        if "params" not in data or "products" not in data["params"]:
            return jsonify({"error": "Niepoprawny format danych!"}), 400

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
