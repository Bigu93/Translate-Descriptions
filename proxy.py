from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import traceback
from utils import (
    calc_hash,
    setup_logger,
    parse_request_data,
    validate_request_data,
    process_translation_request,
)
from config import (
    OPENAI_API_KEY,
    ALLOWED_IPs,
    VALID_API_KEY,
    ALLOWED_ORIGINS,
    ROUTES_WITHOUT_API_KEY,
)

# Initialize Flask App
app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app)

# Load Environment Variables
load_dotenv()

# Setup Logging
logger = setup_logger()

# OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)


def is_ip_allowed(client_ip_str):
    return client_ip_str in ALLOWED_IPs


@app.before_request
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


@app.route("/proxy", methods=["GET", "POST"])
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


@app.route("/")
def hello_world():
    return "Cześć Butosklep!"


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Error in /proxy route: {str(e)}")
    logger.error("Traceback: " + traceback.format_exc())
    return jsonify(error="Internal Server Error"), 500


@app.errorhandler(400)
def invalid_json_format(e, response):
    logger.error(f"JSON parsing error: {str(e)}")
    logger.error("Invalid JSON content: " + response)
    return jsonify(error="Invalid JSON content"), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
