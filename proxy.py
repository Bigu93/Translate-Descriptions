from flask import Flask, request, jsonify, make_response
from auth import Auth
from product import ProductApi
from flask_cors import CORS
from openai import OpenAI
from utils import (
    calc_hash,
    get_logger,
    parse_request_data,
    validate_request_data,
    process_translation_request,
    internal_server_error,
    invalid_json_format,
    parse_product_data,
)
from config import (
    OPENAI_API_KEY,
    ALLOWED_IPs,
    VALID_API_KEY,
    ALLOWED_ORIGINS,
    ROUTES_WITHOUT_API_KEY,
    CLIENT_SECRET,
    CLIENT_USERNAME,
    BASE_URL,
)

app_test = Flask(__name__)
app_test.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app_test)

app_test.errorhandler(500)(internal_server_error)
app_test.errorhandler(400)(invalid_json_format)

logger = get_logger("app")

client = OpenAI(api_key=OPENAI_API_KEY)


def is_ip_allowed(client_ip_str):
    return client_ip_str in ALLOWED_IPs


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

    client_ip = request.remote_addr
    api_key = request.headers.get("Authorization")
    hashed_key = calc_hash(VALID_API_KEY)

    if request.path in ROUTES_WITHOUT_API_KEY:
        if not is_ip_allowed(client_ip):
            return "Access denied!", 403
        return
    if api_key != hashed_key:
        return "Acces denied!", 403


@app_test.route("/proxy", methods=["GET", "POST"])
def proxy_request():
    if request.method != "POST":
        return f"Unsupported method {request.method}", 405

    request_data = request.get_json()
    user_input, translate_type, langs_list = parse_request_data(request_data)

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


@app_test.route("/")
def hello_world():
    return "Cześć Butosklep!"


@app_test.route("/product-data/<product_id>", methods=["GET"])
def get_product_data(product_id):
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    shopid = request.args.get("shopid", default=0, type=int)
    langid = request.args.get("langid", default="pol", type=str)

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
        data = parse_product_data(product_data, lang=langid)
        return jsonify(data)
    else:
        return jsonify({"error": reason}), status_code


if __name__ == "__main__":
    app_test.run(host="0.0.0.0", port=6000)
