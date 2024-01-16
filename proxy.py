from flask import jsonify
from openai import OpenAI
from utils import (
    extract_request_data,
    validate_request_data,
    process_translation_request,
)
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def handle_proxy_request(request):
    if request.method != "POST":
        return f"Unsupported method {request.method}", 405

    request_data = request.get_json()
    user_input, translate_type, langs_list = extract_request_data(request_data)

    if not validate_request_data(user_input, translate_type, langs_list):
        return "Invalid request data", 400

    translations, tokens_used, messages = process_translation_request(
        user_input, translate_type, langs_list, client
    )

    return jsonify(translations, tokens_used, messages)
