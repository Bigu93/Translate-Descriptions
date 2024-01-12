from logging.handlers import RotatingFileHandler
from flask import jsonify
from config import TRANSLATE_PRODUCT_DESC, TRANSLATE_PRODUCT_NAME, LOG_LEVEL
import logging
import os
import traceback
import hashlib
import json


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name="__default__"):
    """
    Returns a logger with rotating file handler. Default name is '__default__'.
    """
    handler = RotatingFileHandler(
        os.path.join("logs", "app.log"), maxBytes=10000, backupCount=3, encoding="utf-8"
    )
    handler.setLevel(getattr(logging, LOG_LEVEL))
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    if not logger.handlers:
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
            print(f"Error in extracting or parsing JSON: {e}")
            return None


def parse_product_data(json_data, lang=None, fields=None):
    parsed_data = []

    for product in json_data["results"]:
        product_info = {
            "productIdent": product["productIdent"],
            "productDescriptionsLangData": {},
        }

        for lang_data in product["productDescriptionsLangData"]:
            current_lang = lang_data["langId"]

            if lang is None or lang == "all" or current_lang == lang:
                if fields is None:
                    filtered_lang_data = lang_data
                else:
                    filtered_lang_data = {
                        field: lang_data.get(field, None) for field in fields
                    }

                # Group by language
                if current_lang not in product_info["productDescriptionsLangData"]:
                    product_info["productDescriptionsLangData"][current_lang] = []

                product_info["productDescriptionsLangData"][current_lang].append(
                    filtered_lang_data
                )

        parsed_data.append(product_info)

    return parsed_data


def internal_server_error(e):
    logger_server_error = get_logger("server_error")
    logger_server_error.error(f"Error in /proxy route: {str(e)}")
    logger_server_error.error("Traceback: " + traceback.format_exc())
    return jsonify(error="Internal Server Error"), 500


def invalid_json_format(e):
    logger_invalid_json = get_logger("logger_invalid_json")
    logger_invalid_json.error(f"JSON parsing error: {str(e)}")
    response = "Invalid JSON content"
    logger_invalid_json.error(response)
    return jsonify(error=response), 400
