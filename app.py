from flask import Flask, request, abort
from flask_cors import CORS
from config import ALLOWED_ORIGINS
from utils import get_logger, internal_server_error, invalid_json_format
from tokens import is_token_valid, generate_token, check_all_tokens, token_bp
from proxy import handle_proxy_request
from product import (
    handle_product_data_request,
    handle_product_info_request,
    handle_product_full_info_request,
    handle_full_products,
)
from rephrase import handle_rephrase_description
from translate import handle_translate_request
from images import handle_images_request
from generate import handle_generate_description
from vies import handle_vies_request
from functools import wraps

app_test = Flask(__name__)
app_test.register_blueprint(token_bp, url_prefix="/token")
CORS(app_test, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

logger = get_logger("app")

app_test.errorhandler(500)(internal_server_error)
app_test.errorhandler(400)(invalid_json_format)


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not is_token_valid(token):
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app_test.route("/")
def hello_world():
    return "Hello Butosklep!"


@app_test.route("/generate-token", methods=["GET"])
def get_token():
    return generate_token(request)


@app_test.route("/check_tokens")
def check_tokens():
    check_all_tokens()
    return "Check complete. See logs for details"


@app_test.route("/proxy", methods=["POST"])
def proxy_request():
    return handle_proxy_request(request)


@app_test.route("/vies", methods=["POST"])
def vies_validation():
    return handle_vies_request(request)


@app_test.route("/product-data/<product_id>", methods=["GET", "POST"])
# @token_required
def product_data(product_id):
    return handle_product_data_request(request, product_id)


@app_test.route("/product-info/<product_ids>", methods=["GET"])
def product_info(product_ids):
    return handle_product_info_request(request, product_ids)


@app_test.route("/product-full-info/<product_id>", methods=["GET"])
def product_full_info(product_id):
    return handle_product_full_info_request(request, product_id)


@app_test.route("/products-info/<int:page_number>", methods=["GET"])
def products_info(page_number):
    return handle_full_products(request, page_number)


@app_test.route("/translate", methods=["POST"])
def translate():
    return handle_translate_request(request)


@app_test.route("/images/<product_id>", methods=["GET"])
def get_images(product_id):
    return handle_images_request(request, product_id)


@app_test.route("/generate-description", methods=["POST"])
# @token_required
def generate_description():
    return handle_generate_description(request)


@app_test.route("/rephrase-description", methods=["POST"])
# @token_required
def rephrase_description():
    return handle_rephrase_description(request)


if __name__ == "__main__":
    app_test.run(host="0.0.0.0", port=5000)
