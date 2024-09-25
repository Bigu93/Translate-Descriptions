import json
from flask import jsonify
from utils import (
    parse_response_content_openai,
    internal_server_error,
    invalid_json_format,
)
from openai import OpenAI
from config import OPENAI_API_KEY
from config import (
    PROMPT_PRODUCT_NAME,
    PROMPT_PRODUCT_DESC,
    PROMPT_META_TITLE,
    PROMPT_META_DESC,
    PROMPT_KEYWORDS,
    OPENAI_MODEL,
)

TRANSLATE_TYPES = {
    "productName": PROMPT_PRODUCT_NAME,
    "productLongDescription": PROMPT_PRODUCT_DESC,
    "productMetaTitle": PROMPT_META_TITLE,
    "productMetaDescription": PROMPT_META_DESC,
    "productMetaKeywords": PROMPT_KEYWORDS,
}

LANGUAGE_MAP = {
    "pol": "Polish",
    "bul": "Bulgarian",
    "cze": "Czech",
    "eng": "English",
    "est": "Estonian",
    "ger": "German",
    "hun": "Hungarian",
    "ita": "Italian",
    "lit": "Lithuanian",
    "rum": "Romanian",
    "scr": "Croatian",
    "slo": "Slovak",
    "slv": "Slovenian",
    "spa": "Spanish",
}

REVERSE_LANGUAGE_MAP = {v: k for k, v in LANGUAGE_MAP.items()}
CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def handle_translate_request(request):
    """
    Handler for translation request.
    """
    if request.method != "POST":
        return jsonify({"error": "Unsupported method!"}), 400

    if request.method == "POST":
        data = request.json

        if not data:
            return jsonify({"error": "Empty payload!"}), 400

        if "params" not in data or "products" not in data["params"]:
            return jsonify({"error": "Unsupported JSON structure!"}), 400

        try:
            target_languages = get_target_languages(data)
            polish_content = extract_polish_content(data)
            category = data["params"]["products"][0]["productInfo"]["category"]
            name = data["params"]["products"][0]["productInfo"]["name"]
            desc = data["params"]["products"][0]["productInfo"]["description"]
            translations = []

            for content in polish_content:
                location_translations = {}
                for field, text in content["texts"].items():
                    if text:
                        polish_text = (
                            desc
                            if field == "productLongDescription"
                            or field == "productMetaDescription"
                            or field == "productMetaKeywords"
                            else name
                        )

                        translated_texts = translate_text(
                            polish_text, target_languages, field, category
                        )
                        for (
                            target_lang_name,
                            translated_text,
                        ) in translated_texts.items():
                            target_lang_code = REVERSE_LANGUAGE_MAP.get(
                                target_lang_name, target_lang_name
                            )
                            if target_lang_code not in location_translations:
                                location_translations[target_lang_code] = {}
                            location_translations[target_lang_code][field] = (
                                translated_text
                            )

                translations.append(
                    {
                        "location": content["location"],
                        "translated_texts": location_translations,
                    }
                )

            updated_data = update_json(data, translations)
            return jsonify(updated_data), 200

        except Exception as e:
            print("error: ", str(e))
            return jsonify({"error": str(e)}), 500


def extract_polish_content(data):
    """
    Extract Polish content and its location within the JSON.
    """
    polish_content = []
    for product in data["params"]["products"]:
        for description in product["productDescriptionsLangData"]:
            if description["langId"] == "pol":
                content_to_translate = {}
                for key, value in description.items():
                    if key not in ["langId", "shopId"]:
                        content_to_translate[key] = value
                if content_to_translate:
                    polish_content.append(
                        {
                            "location": (product, description),
                            "texts": content_to_translate,
                        }
                    )
    return polish_content


def get_target_languages(data):
    """
    Extract a unique set of languages to translate to, excluding 'pol', and map them to full language names.
    """
    languages = set()
    for product in data["params"]["products"]:
        for description in product["productDescriptionsLangData"]:
            lang_id = description.get("langId")
            if lang_id and lang_id != "pol":
                languages.add(LANGUAGE_MAP.get(lang_id, lang_id))
    return languages


def translate_text(text, target_languages, content_type, category):
    """
    Translate text to the target language using an API.
    """
    model = OPENAI_MODEL
    messages = []
    system_prompt = TRANSLATE_TYPES.get(content_type, "Invalid content_type")
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"[{text}] Langs:[{','.join(target_languages)}] Category:[{category}]",
        },
    ]

    try:
        response = CLIENT.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
            max_tokens=4096,
        )
        response_content = response.choices[0].message.content.strip()
        translation = parse_response_content_openai(response_content)
        return translation
    except json.JSONDecodeError as e:
        invalid_json_format(e, response_content)
    except Exception as e:
        internal_server_error(e)


def update_json(data, translations):
    """
    Update the original JSON structure with the translations.
    """
    for translation in translations:
        product, original_description = translation["location"]
        for target_lang, translated_texts in translation["translated_texts"].items():
            found = False
            for description in product["productDescriptionsLangData"]:
                if (
                    description["langId"] == target_lang
                    and description["shopId"] == original_description["shopId"]
                ):
                    description.update(translated_texts)
                    found = True
                    break
            if not found:
                new_translation = {
                    "langId": target_lang,
                    "shopId": original_description["shopId"],
                    **translated_texts,
                }
                product["productDescriptionsLangData"].append(new_translation)
    return data
