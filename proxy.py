from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from logging.handlers import RotatingFileHandler
import traceback
import hashlib
import os
import json
import logging

load_dotenv()

######################
#   Logging setup    #
######################
handler = RotatingFileHandler(
    "record_debug.log", maxBytes=10000, backupCount=3, encoding="utf-8"
)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s"
)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.addHandler(handler)

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app)

######################
#   Config setup     #
######################
OPENAI_API_KEY = os.getenv("O_SECRET")
ALLOWED_IPs = os.getenv("IPs")
VALID_API_KEY = os.getenv("API_KEY")
ALLOWED_ORIGINS = ["https://butosklep.pl", "https://butosklep.iai-shop.com"]
ROUTES_WITHOUT_API_KEY = ["/"]
PROMPT_NAME = """Act like a language translator. I will give you product name and desired lang for translating. Keep the word seqeuence in place. Don't add any special signs like commas, hyphens or similar to the response. I will give you some examples in Polish. In given examples, the "Suzy", "Carrie", "KK174215", "LL274A177", "MR870-49" are special names. If the sentence has special name, keep it at the end of sentence, but if it's from Big Star company or different, put it before the last one. Examples in Polish:
###
Klapki Z Kokardą I Ozdobnym Misiem Fuksja Suzy, Damskie Lakierowane Sandały Na Słupku Maciejka Czarne Carrie,Męskie Buty Trekkingowe Big Star KK174215 Czarne, Damskie Tenisówki Na Platformie Big Star LL274A177 Białe, Lakierowane Botki Na Obcasie S.Barski MR870-49 Jasnoszare
###
Return just the translated text in JSON following format:{"Czech":"Sample text"}"""
PROMPT_DESCRIPTION = """Act like a language translator. I will give you product descriptions for translating. Important thing is to remove all HTML tags. You will get langs list for all translations. Return just the translated text in following JSON format: {"Sample lang":"Sample text","Sample lang":"Sample text",}"""

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

    # if request.path in ROUTES_WITHOUT_API_KEY:
    #     if not is_ip_allowed(client_ip):
    #         return "Access denied!", 403
    #     return
    # if not is_ip_allowed(client_ip) or api_key != hashed_key:
    #     return "Access denied asshole!", 403
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
        user_input, translate_type, langs_list
    )
    response = make_response(jsonify(translations, tokens_used, messages))
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers.add("Access-Control-Allow-Origin", origin)
    return response


@app.route("/")
def hello_world():
    return "Cześć Butosklep!"


def calc_hash(input):
    value_to_hash = input
    hash_method = hashlib.sha256()
    hash_method.update(value_to_hash.encode("utf-8"))
    hash_result = hash_method.hexdigest()
    return hash_result


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


def parse_request_data(request_data):
    user_input = request_data.get("userPrompt")
    translate_type = request_data.get("translateType")
    langs_list = request_data.get("languages")
    return user_input, translate_type, langs_list


def validate_request_data(user_input, translate_type, langs_list):
    if (
        translate_type not in ["name", "description"]
        or not user_input
        or not langs_list
    ):
        return False
    return True


def process_translation_request(user_input, translate_type, langs_list):
    model = "gpt-3.5-turbo-1106"
    messages = []

    if translate_type == "description":
        prompt_content = PROMPT_DESCRIPTION
    elif translate_type == "name":
        prompt_content = PROMPT_NAME
    else:
        return (
            "Coś poszło nie tak :(",
            400,
        )

    messages.append({"role": "system", "content": prompt_content})
    messages.append(
        {
            "role": "user",
            "content": f"[{user_input}] Langs:[{','.join(langs_list)}]",
        }
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
        )
        response_content = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        translations = parse_response_content(response_content)

        return translations, tokens_used, messages
    except json.JSONDecodeError as e:
        invalid_json_format(e, response_content)
    except Exception as e:
        internal_server_error(e)


def parse_response_content(response_content):
    try:
        # First, try to directly parse the response content as JSON
        return json.loads(response_content)
    except json.JSONDecodeError:
        # If direct parsing fails, try extracting JSON from formatted content
        try:
            json_start = response_content.index("{")
            json_end = response_content.rindex("}") + 1
            json_str = response_content[json_start:json_end]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            # Handle cases where extraction or parsing fails
            print(f"Error in extracting or parsing JSON: {e}")
            return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
