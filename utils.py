import os
import traceback
import json
from logging_config import get_logger
from flask import jsonify
from config import (
    PROMPT_PRODUCT_NAME,
    PROMPT_PRODUCT_DESC,
    PROMPT_META_TITLE,
    PROMPT_META_DESC,
    PROMPT_KEYWORDS,
    LOG_LEVEL,
    OPENAI_MODEL,
    CLIENT_SECRET,
    CLIENT_USERNAME,
    BASE_URL,
)
from api.auth import Auth
from api.products_info import ProductApi

TRANSLATE_TYPES = {
    "name": PROMPT_PRODUCT_NAME,
    "description": PROMPT_PRODUCT_DESC,
    "meta_title": PROMPT_META_TITLE,
    "meta_description": PROMPT_META_DESC,
    "keywords": PROMPT_KEYWORDS,
}


def get_product_api():
    """Initialize and return a ProductApi instance."""
    auth = Auth(CLIENT_USERNAME, CLIENT_SECRET, BASE_URL)
    token = auth.get_token()
    return ProductApi(BASE_URL, token, "v3")


def extract_request_data(request_data):
    """
    Extracts and returns user input, translate type, and language list from request data.
    """
    text_to_translate = request_data.get("userPrompt")
    translate_type = request_data.get("translateType")
    langs_list = request_data.get("languages")

    return text_to_translate, translate_type, langs_list


def validate_request_data(text_to_translate, translate_type, langs_list):
    """
    Validates request data for translation request.
    """
    if (
        translate_type not in TRANSLATE_TYPES.keys()
        or not text_to_translate
        or not langs_list
    ):
        return False
    return True


def process_translation_request(
    text_to_translate,
    translate_type,
    langs_list,
    client,
):
    """
    OpenAI translation function.
    """
    model = OPENAI_MODEL
    messages = []

    if translate_type in TRANSLATE_TYPES.keys():
        prompt_content = TRANSLATE_TYPES[translate_type]
    else:
        return (
            "Something went wrong",
            400,
        )

    messages.append({"role": "system", "content": prompt_content})
    messages.append(
        {
            "role": "user",
            "content": f"[{text_to_translate}] Langs:[{','.join(langs_list)}]",
        }
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
            max_tokens=4000,
        )
        response_content = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        translations = parse_response_content_openai(response_content)

        return translations, tokens_used, messages
    except json.JSONDecodeError as e:
        invalid_json_format(e, response_content)
    except Exception as e:
        internal_server_error(e)


def escape_single_quotes(value):
    """
    Escape single quotes in a string value, ensuring valid JSON format.
    """
    return value.replace("'", "\\'")


def ensure_quotes_and_escape(json_obj):
    """
    Recursively ensure all keys and values are correctly quoted and single quotes in values are escaped.
    This function operates on the parsed JSON object (dict/list).
    """
    if isinstance(json_obj, dict):
        return {
            ensure_quotes_and_escape(k): ensure_quotes_and_escape(v)
            for k, v in json_obj.items()
        }
    elif isinstance(json_obj, list):
        return [ensure_quotes_and_escape(element) for element in json_obj]
    elif isinstance(json_obj, str):
        return escape_single_quotes(json_obj)
    else:
        return json_obj


def parse_response_content_openai(response_content):
    """
    Validating and parsing the response from OpenAI, ensuring all keys and values are enclosed in double quotes,
    and escaping single quotes in values.
    """
    try:
        parsed_json = json.loads(response_content)
        corrected_json = ensure_quotes_and_escape(parsed_json)
        return corrected_json
    except json.JSONDecodeError:
        try:
            json_start = response_content.index("{")
            json_end = response_content.rindex("}") + 1
            json_str = response_content[json_start:json_end]
            parsed_json = json.loads(json_str)
            corrected_json = ensure_quotes_and_escape(parsed_json)
            return corrected_json
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error in extracting or parsing JSON: {e}")
            return None


def parse_product_data(json_data, lang=None, fields=None):
    """
    Parsing JSON from IdoSell API response.
    """
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

                if current_lang not in product_info["productDescriptionsLangData"]:
                    product_info["productDescriptionsLangData"][current_lang] = []

                product_info["productDescriptionsLangData"][current_lang].append(
                    filtered_lang_data
                )
        parsed_data.append(product_info)
    return parsed_data


def parse_product_images(json_data):
    """
    Parsing JSON from IdoSell API response.
    """
    results = json_data.get("results", [])
    extracted_data = []

    for result in results:
        product_images = result.get("productImages", [])
        for image in product_images:
            extracted_data.append(
                {
                    "productImageMediumUrl": image.get("productImageMediumUrl"),
                    "productImageId": image.get("productImageId"),
                }
            )
    return jsonify(extracted_data)


def parse_product_info(json_data):
    """
    Parsing JSON about product info from IdoSell API response.
    """
    results = json_data.get("results", [])

    def format_location(text_id):
        parts = text_id.split("\\")
        if len(parts) == 5:
            return " - ".join(parts[i] for i in [0, 2, 4])
        elif len(parts) == 2:
            return " - ".join(parts)
        else:
            return text_id

    extracted_data = []

    for result in results:
        found_by = result.get("foundByIndex", [])
        product_info_list = result.get("productSkuList", [])
        for info in product_info_list:
            quantities_dict = {
                q["stockId"]: q["disposition"] for q in info.get("quantities", [])
            }
            stock_locations = [
                {
                    "stockId": stock["stockId"],
                    "location": format_location(stock["stockLocationTextId"]),
                    "quantity": quantities_dict.get(stock["stockId"], 0),
                }
                for stock in info.get("stockLocations", [])
            ]
            extracted_data.append(
                {
                    "foundBy": found_by,
                    "productId": info.get("productId"),
                    "productName": info.get("productName"),
                    "sizeId": info.get("sizeId"),
                    "sizeName": info.get("sizeName"),
                    "codeProducer": info.get("codeProducer"),
                    "weight": info.get("weight"),
                    "quantity": sum(q["quantity"] for q in info.get("quantities", [])),
                    "producerName": info.get("producerName"),
                    "delivererName": info.get("delivererName"),
                    "productNote": info.get("productNote"),
                    "stockLocations": stock_locations if stock_locations else None,
                    "germanProductName": next(
                        (
                            desc["name"]
                            for desc in info.get("productDescriptionsLangData", [])
                            if desc["langId"] == "ger"
                        ),
                        None,
                    ),
                    "productRetailPrice": next(
                        (
                            price["productRetailPrice"]
                            for price in info.get("productPrices", [])
                            if price["shopName"] == "butosklep.pl"
                        ),
                        None,
                    ),
                    "productWholesalePrice": next(
                        (
                            price["productWholesalePrice"]
                            for price in info.get("productPrices", [])
                            if price["shopName"] == "butosklep.pl"
                        ),
                        None,
                    ),
                    "productIconSmallUrl": info.get("productIcon", {}).get(
                        "productIconSmallUrl"
                    ),
                    "productIconLargeUrl": info.get("productIcon", {}).get(
                        "productIconLargeUrl"
                    ),
                    "langProductNames": {
                        desc["langId"]: desc["name"]
                        for desc in info.get("productDescriptionsLangData", [])
                    },
                }
            )
    return extracted_data


def parse_full_product_info(json_data):
    """
    Parsing JSON about full product info from IdoSell API response.
    """
    results = json_data.get("results", [])
    extracted_data = []
    for result in results:
        extracted_data.append(
            {
                "productId": result.get("productId"),
                "productDisplayedCode": result.get("productDisplayedCode"),
                "producerName": result.get("producerName"),
                "sizeChartId": result.get("sizeChartId"),
                "sizeChartName": result.get("sizeChartName"),
                "categoryName": result.get("categoryName"),
                "categoryIdoSellPath": result.get("categoryIdoSellPath"),
                "productIconLargeUrl": result.get("productIcon", {}).get(
                    "productIconLargeUrl"
                ),
                "productAuctionIconLargeUrl": f"""https://butosklep.pl/{result.get("productAuctionIcon", {}).get(

                    "productAuctionIconLargeUrl"

                )}""",
                "productSmallImages": {
                    index + 1: image["productImageSmallUrl"]
                    for index, image in enumerate(result.get("productImages", []))
                },
                "productMediumImages": {
                    index + 1: image["productImageMediumUrl"]
                    for index, image in enumerate(result.get("productImages", []))
                },
                "productLargeImages": {
                    index + 1: image["productImageLargeUrl"]
                    for index, image in enumerate(result.get("productImages", []))
                },
                "productAddingTime": result.get("productAddingTime"),
                "productPriceChangedTime": result.get("productPriceChangedTime"),
                "productInNew": result.get("productInNew"),
                "productRetailPrice": result.get("productRetailPrice"),
                "productWholesalePrice": result.get("productWholesalePrice"),
                "productMinimalPrice": result.get("productMinimalPrice"),
                "productParameters": {
                    next(
                        (
                            desc["parameterName"]
                            for desc in param["parameterDescriptionsLangData"]
                            if desc["langId"] == "pol"
                        ),
                        None,
                    ): next(
                        (
                            val_desc["parameterValueName"]
                            for value in param["parameterValues"]
                            for val_desc in value["parameterValueDescriptionsLangData"]
                            if val_desc["langId"] == "pol"
                        ),
                        None,
                    )
                    for param in result.get("productParameters")
                    if next(
                        (
                            desc["parameterName"]
                            for desc in param["parameterDescriptionsLangData"]
                            if desc["langId"] == "pol"
                        ),
                        None,
                    )
                },
                "productSizes": [
                    size["sizeId"] for size in result.get("productSizes", [])
                ],
            }
        )
    return extracted_data


def parse_full_products_info(json_data, base_url):
    """
    Parsing JSON about full products info from IdoSell API response.
    """
    results = json_data.get("results", [])
    extracted_data = []
    for result in results:
        extracted_data.append(
            {
                "productId": result.get("productId"),
                "productDisplayedCode": result.get("productDisplayedCode"),
                "polishProductName": next(
                    (
                        desc["productName"]
                        for desc in result.get("productDescriptionsLangData")
                        if desc["langId"] == "pol"
                    ),
                    None,
                ),
            }
        )
    current_page = json_data.get("resultsPage", 0)
    results_limit = json_data.get("resultsLimit", 10)
    total_pages = json_data.get("resultsNumberPage", 0)
    total_results = json_data.get("resultsNumberAll", 0)
    pagination = {
        "current_page": current_page,
        "results_limit": results_limit,
        "total_pages": total_pages - 1,
        "total_results": total_results,
        "has_next_page": current_page < total_pages - 1,
        "has_prev_page": current_page > 0,
        "next_page": f"{base_url}/{current_page + 1}"
        if current_page < total_pages - 1
        else None,
        "prev_page": f"{base_url}/{current_page - 1}" if current_page > 0 else None,
    }
    return {
        "data": extracted_data,
        "pagination": pagination,
    }


def internal_server_error(e):
    """
    Handling server 500 response.
    """
    logger_server_error = get_logger("server_error")
    logger_server_error.error(f"Error: {str(e)}")
    logger_server_error.error("Traceback: " + traceback.format_exc())
    return jsonify(error="Internal Server Error"), 500


def invalid_json_format(e):
    """
    Handling server 400 response.
    """
    logger_invalid_json = get_logger("logger_invalid_json")
    logger_invalid_json.error(f"JSON parsing error: {str(e)}")
    response = "Invalid JSON content"
    logger_invalid_json.error(response)
    return jsonify(error=response), 400
