from flask import Flask, request, abort
from flask_cors import CORS
from config import ALLOWED_ORIGINS
from utils import get_logger, internal_server_error, invalid_json_format
from tokens import is_token_valid, generate_token
from proxy import handle_proxy_request
from product import handle_product_data_request
from translate import handle_translate_request

app_test = Flask(__name__)
CORS(app_test, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

logger = get_logger("app")

app_test.errorhandler(500)(internal_server_error)
app_test.errorhandler(400)(invalid_json_format)


@app_test.route("/")
def hello_world():
    return "Cześć Butosklep!"


@app_test.route("/generate-token", methods=["GET"])
def get_token():
    return generate_token(request)


@app_test.route("/proxy", methods=["POST"])
def proxy_request():
    token = request.headers.get("Authorization")
    if not token or not is_token_valid(token):
        abort(403)
    return handle_proxy_request(request)


@app_test.route("/product-data/<product_id>", methods=["GET", "POST"])
def product_data(product_id):
    token = request.headers.get("Authorization")
    if not token or not is_token_valid(token):
        abort(403)
    return handle_product_data_request(request, product_id)


@app_test.route("/translate/<product_id>", methods=["POST"])
def translate(product_id):
    token = request.headers.get("Authorization")
    if not token or not is_token_valid(token):
        abort(403)
    return handle_translate_request(request, product_id)


if __name__ == "__main__":
    app_test.run(host="0.0.0.0", port=6000)
