from flask import Flask, request, jsonify, make_response, abort
from urllib.parse import unquote
from auth import Auth
from product import ProductApi
from tokens import store_token, is_token_valid
from flask_cors import CORS
from openai import OpenAI
from utils import (
    get_logger,
    extract_request_data,
    validate_request_data,
    process_translation_request,
    internal_server_error,
    invalid_json_format,
    parse_product_data,
)
from config import (
    OPENAI_API_KEY,
    ALLOWED_ORIGINS,
    CLIENT_SECRET,
    CLIENT_USERNAME,
    BASE_URL,
)
import secrets

app_test = Flask(__name__)
app_test.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app_test)

app_test.errorhandler(500)(internal_server_error)
app_test.errorhandler(400)(invalid_json_format)

logger = get_logger("app")

client = OpenAI(api_key=OPENAI_API_KEY)


@app_test.before_request
def restrict_access():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")
        response = make_response()

        if origin in ALLOWED_ORIGINS:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Methods", "POST")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        return response


@app_test.route("/")
def hello_world():
    return "Cześć Butosklep!"


@app_test.route("/generate-token", methods=["GET"])
def generate_token():
    token = secrets.token_hex(16)
    store_token(token)
    return jsonify({"token": token})


@app_test.route("/proxy", methods=["POST"])
def proxy_request():
    token = request.headers.get("Authorization")
    if not token or not is_token_valid(token):
        abort(403)

    if request.method != "POST":
        return f"Unsupported method {request.method}", 405

    request_data = request.get_json()
    user_input, translate_type, langs_list = extract_request_data(request_data)

    if not validate_request_data(user_input, translate_type, langs_list):
        return "Invalid request data", 400

    translations, tokens_used, messages = process_translation_request(
        user_input, translate_type, langs_list, client
    )
    response = make_response(jsonify(translations, tokens_used, messages))
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers.add("Access-Control-Allow-Origin", origin)
    return response


@app_test.route("/product-data/<product_id>", methods=["GET", "POST"])
def get_product_data(product_id):
    token = request.headers.get("Authorization")
    if not token or not is_token_valid(token):
        abort(403)

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


@app_test.route("/translate/<product_id>", methods=["POST"])
def translate(product_id):
    token = request.headers.get("Authorization")
    if not token or not is_token_valid(token):
        abort(403)

    if not product_id:
        return jsonify({"error": "Wymagane ID produktu!"}), 400

    if request.method != "POST":
        return jsonify({"error": "Nie wspierana metoda!"}), 400

    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"error": "Nie podano wysłano payloadu!"}), 400

        if "params" not in data or "products" not in data["params"]:
            return jsonify({"error": "Niepoprawny format danych!"}), 400

        try:
            return jsonify(data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app_test.run(host="0.0.0.0", port=6000)
