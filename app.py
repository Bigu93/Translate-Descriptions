from flask import Flask, request, abort, send_from_directory, make_response
from flask_cors import CORS
from config import ALLOWED_ORIGINS
from utils import (
    internal_server_error,
    invalid_json_format,
)
from logging_config import get_logger
from tokens import is_token_valid, generate_token, token_bp
from proxy import handle_proxy_request
from product import (
    handle_product_data_request,
    handle_product_info_request,
    handle_product_full_info_request,
    handle_full_products,
)
from auth_bearer import auth_bp
from rephrase import handle_rephrase_description
from translate import handle_translate_request
from images import handle_images_request
from generate import handle_generate_description
from vies import handle_vies_request
from functools import wraps

logger = get_logger("app")

app_test = Flask(__name__)
app_test.register_blueprint(token_bp, url_prefix="/token")
app_test.register_blueprint(auth_bp, url_prefix="/auth")

app_test.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400

CORS(app_test, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

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


@app_test.before_request
def log_request():
    if request.path.startswith("/static/"):
        logger_files.info(f"Static file request: {request.path}")


@app_test.after_request
def log_response(response):
    if request.path.startswith("/static"):
        logger_files.info(
            f"Static file request completed: {request.path}, Status: {response.status_code}"
        )
    return response


@app_test.route("/")
def hello_world():
    return "Hello Butosklep!"


@app_test.route("/generate-token", methods=["GET"])
def get_token():
    return generate_token()


@app_test.route("/proxy", methods=["POST"])
def proxy_request():
    return handle_proxy_request(request)


@app_test.route("/vies", methods=["POST"])
def vies_validation():
    return handle_vies_request(request)


@app_test.route("/product-data/<product_id>", methods=["GET", "POST"])
@token_required
def product_data(product_id):
    request.view_args["product_id"] = product_id
    return handle_product_data_request(request)


@app_test.route("/product-info/<product_ids>", methods=["GET"])
def product_info(product_ids):
    return handle_product_info_request(request, product_ids)


@app_test.route("/product-full-info/<product_id>", methods=["GET"])
def product_full_info(product_id):
    request.view_args["product_id"] = product_id
    return handle_product_full_info_request(request)


@app_test.route("/products-info/<int:results_page>", methods=["GET"])
def products_info(results_page):
    results_limit = request.args.get("results_limit", default=50, type=int)
    if not (1 <= results_limit <= 100):
        results_limit = 50

    return handle_full_products(request, results_page, results_limit)


@app_test.route("/translate", methods=["POST"])
def translate():
    return handle_translate_request(request)


@app_test.route("/images/<product_id>", methods=["GET"])
def get_images(product_id):
    request.view_args["product_id"] = product_id
    return handle_images_request(request)


@app_test.route("/generate-description", methods=["POST"])
@token_required
def generate_description():
    return handle_generate_description(request)


@app_test.route("/rephrase-description", methods=["POST"])
@token_required
def rephrase_description():
    return handle_rephrase_description(request)


if __name__ == "__main__":
    app_test.run(host="0.0.0.0", port=5000)
