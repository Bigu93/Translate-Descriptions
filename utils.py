from logging.handlers import RotatingFileHandler
from flask import jsonify
from config import TRANSLATE_PRODUCT_DESC, TRANSLATE_PRODUCT_NAME
import logging
import traceback
import hashlib
import json


def setup_logger():
    """
    Sets up and returns a logger with rotating file handler.
    """
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
    return logger


def parse_request_data(request_data):
    """
    Extracts and returns user input, translate type, and language list from request data.
    """
    user_input = request_data.get("userPrompt")
    translate_type = request_data.get("translateType")
    langs_list = request_data.get("languages")
    return user_input, translate_type, langs_list


def validate_request_data(user_input, translate_type, langs_list):
    """
    Validates request data for translation request.
    """
    if (
        translate_type not in ["name", "description"]
        or not user_input
        or not langs_list
    ):
        return False
    return True


def process_translation_request(
    user_input,
    translate_type,
    langs_list,
    client,
    first_dec,
):
    model = "gpt-3.5-turbo-1106"
    messages = []

    if translate_type == "description":
        prompt_content = TRANSLATE_PRODUCT_DESC
    elif translate_type == "name":
        prompt_content = TRANSLATE_PRODUCT_NAME
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


def calc_hash(input):
    """
    Calculates and returns SHA256 hash of the input.
    """
    hash_method = hashlib.sha256()
    hash_method.update(input.encode("utf-8"))
    return hash_method.hexdigest()


def parse_response_content(response_content):
    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        try:
            json_start = response_content.index("{")
            json_end = response_content.rindex("}") + 1
            json_str = response_content[json_start:json_end]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            # Handle cases where extraction or parsing fails
            print(f"Error in extracting or parsing JSON: {e}")
            return None


# Error handling decorators
def internal_server_error(e):
    logger = setup_logger()
    logger.error(f"Error in /proxy route: {str(e)}")
    logger.error("Traceback: " + traceback.format_exc())
    return jsonify(error="Internal Server Error"), 500


def invalid_json_format(e):
    logger = setup_logger()
    logger.error(f"JSON parsing error: {str(e)}")
    # Assuming `response` is a string describing the error context
    response = "Invalid JSON content"  # Update this as needed
    logger.error(response)
    return jsonify(error=response), 400
