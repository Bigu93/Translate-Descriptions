"""
Product data parsing utilities for IdoSell API responses.
"""
from typing import Any, Dict, List, Optional
from flask import jsonify
from app.infrastructure.logging.structured_logger import get_logger
from app.core.domain.exceptions import ParsingError


logger = get_logger("product_parser")


def format_location(text_id: str) -> str:
    """
    Format a location text ID into a readable format.

    Args:
        text_id: The location text ID (e.g., "Warehouse\\Shelf\\Bin\\Row\\Position")

    Returns:
        Formatted location string

    Example:
        >>> format_location("Warehouse\\A\\Bin\\1\\Top")
        'Warehouse - Bin - Top'
    """
    parts = text_id.split("\\")
    if len(parts) == 5:
        return " - ".join(parts[i] for i in [0, 2, 4])
    elif len(parts) == 2:
        return " - ".join(parts)
    else:
        return text_id


def parse_product_data(
    json_data: Dict[str, Any], lang: Optional[str] = None, fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Parse product data from IdoSell API response.

    Args:
        json_data: The JSON response from the API
        lang: Language filter (None for all languages, 'all' for all, or specific lang code)
        fields: List of fields to include (None for all fields)

    Returns:
        List of parsed product information

    Raises:
        ParsingError: If the JSON data structure is invalid

    Example:
        >>> data = {"results": [{"productIdent": "123", "productDescriptionsLangData": [...]}]}
        >>> result = parse_product_data(data)
        >>> result[0]["productIdent"]
        '123'
    """
    if "results" not in json_data:
        raise ParsingError("Invalid JSON structure: missing 'results' key")

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


def parse_product_images(json_data: Dict[str, Any]):
    """
    Parse product images from IdoSell API response.

    Args:
        json_data: The JSON response from the API

    Returns:
        List of extracted image items.

    Example:
        >>> data = {"results": [{"productImages": [...]}]}
        >>> result = parse_product_images(data)
    """
    results = json_data.get("results", [])
    extracted_data: List[Dict[str, Any]] = []

    for result in results:
        product_images = result.get("productImages", [])
        for image in product_images:
            extracted_data.append(
                {
                    "productImageMediumUrl": image.get("productImageMediumUrl"),
                    "productImageId": image.get("productImageId"),
                }
            )

    return extracted_data


def parse_product_info(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse product info from IdoSell API response.

    Args:
        json_data: The JSON response from the API

    Returns:
        List of parsed product information with stock locations, prices, and descriptions

    Raises:
        ParsingError: If the JSON data structure is invalid

    Example:
        >>> data = {"results": [{"foundByIndex": [...], "productSkuList": [...]}]}
        >>> result = parse_product_info(data)
        >>> len(result)
        1
    """
    if "results" not in json_data:
        raise ParsingError("Invalid JSON structure: missing 'results' key")

    results = json_data.get("results", [])
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


def parse_full_product_info(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse full product info from IdoSell API response.

    Args:
        json_data: The JSON response from the API

    Returns:
        List of parsed full product information

    Raises:
        ParsingError: If the JSON data structure is invalid

    Example:
        >>> data = {"results": [{"productId": "123", "productDisplayedCode": "CODE"}]}
        >>> result = parse_full_product_info(data)
        >>> result[0]["productId"]
        '123'
    """
    if "results" not in json_data:
        raise ParsingError("Invalid JSON structure: missing 'results' key")

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
                    for param in result.get("productParameters", [])
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


def parse_full_products_info(
    json_data: Dict[str, Any], base_url: str
) -> Dict[str, Any]:
    """
    Parse full products info from IdoSell API response with pagination.

    Args:
        json_data: The JSON response from the API
        base_url: The base URL for pagination links

    Returns:
        Dictionary containing extracted data and pagination information

    Raises:
        ParsingError: If the JSON data structure is invalid

    Example:
        >>> data = {
        ...     "results": [{"productId": "123", "productDisplayedCode": "CODE"}],
        ...     "resultsPage": 0,
        ...     "resultsLimit": 10,
        ...     "resultsNumberPage": 2,
        ...     "resultsNumberAll": 20
        ... }
        >>> result = parse_full_products_info(data, "/api/products")
        >>> result["data"][0]["productId"]
        '123'
        >>> result["pagination"]["current_page"]
        0
    """
    if "results" not in json_data:
        raise ParsingError("Invalid JSON structure: missing 'results' key")

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
                        for desc in result.get("productDescriptionsLangData", [])
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
        "next_page": (
            f"{base_url}/{current_page + 1}" if current_page < total_pages - 1 else None
        ),
        "prev_page": f"{base_url}/{current_page - 1}" if current_page > 0 else None,
    }

    return {
        "data": extracted_data,
        "pagination": pagination,
    }
