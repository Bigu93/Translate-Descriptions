from flask import jsonify
from urllib.parse import unquote
from utils import (
    parse_product_data,
    parse_product_info,
    parse_full_product_info,
    parse_full_products_info,
    get_product_api,
)


def is_ean_code(product_id):
    return product_id.isdigit() and len(product_id) in {8, 12, 13, 14}


def handle_api_response(status_code, reason, product_data, parse_func=None, **kwargs):
    """Standardize API responses."""
    if status_code == 200:
        if parse_func:
            try:
                data = parse_func(product_data, **kwargs)
            except Exception as e:
                return jsonify({"error": f"Parsing error: {str(e)}"}), 500
            return jsonify(data), 200
        return jsonify({"message": "Success"}), 200
    else:
        return jsonify({"error": reason}), status_code


def handle_product_data_request(request):
    """
    Handler for getting and setting product name and description data.
    Supports GET for retrieval and POST for updating.
    """
    product_id = request.view_args.get("product_id")

    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400

    product_api = get_product_api()

    if request.method == "GET":
        shopid = request.args.get("shopid", default=0, type=int)
        langid = request.args.get("langid", default="pol", type=str).lower()
        langid = None if langid == "all" else langid

        fields_query = request.args.get("fields", default="productName", type=str)
        fields_list = (
            None if fields_query.lower() == "all" else unquote(fields_query).split(",")
        )

        try:
            (status_code, reason, product_data) = product_api.get_product_description(
                params=[product_id, shopid]
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return handle_api_response(
            status_code,
            reason,
            product_data,
            parse_func=parse_product_data,
            lang=langid,
            fields=fields_list,
        )

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty payload!"}), 400

        if "params" not in data or "products" not in data["params"]:
            return jsonify({"error": "Unsupported JSON structure!"}), 400

        try:
            status_code, reason, _ = product_api.set_product_description(data=data)
            if status_code == 200:
                return jsonify({"message": "Saved successfully!"}), 200
            else:
                return jsonify({"error": reason}), status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": "Method not allowed"}), 405


def handle_product_full_info_request(request):
    """
    Handler for getting full information about a specific product.
    Determines whether the product_id is an EAN or contains a size code.
    """
    product_id = request.view_args.get("product_id")

    if not product_id:
        return jsonify({"error": "Product ID needs to be provided!"}), 400

    if request.method != "GET":
        return jsonify({"error": "Method not allowed"}), 405

    if is_ean_code(product_id):
        return handle_full_product_with_ean(product_id)
    else:
        parts = product_id.split("-")
        if len(parts) == 2:
            base_product_id, size_id = parts
            return handle_full_product_with_size(base_product_id, size_id)
        else:
            return (
                jsonify({"error": "Product ID with size code needs to be provided!"}),
                400,
            )


def handle_products_full_info_request(request):
    """
    Handler for getting full information about all products.
    """
    if request.method != "GET":
        return jsonify({"error": "Invalid method!"}), 400

    return handle_full_products()


def handle_product_info_request(request, product_ids):
    """
    Handler for getting necessary information about specific products.
    Expects a comma-separated list of product_ids.
    """

    if not product_ids:
        return jsonify({"error": "Product IDs need to be provided!"}), 400

    product_ids_list = product_ids.split(",")

    return handle_products_with_size(request, product_ids_list)


def handle_products_with_size(request, product_ids):
    """
    Handler for getting information about specific products with embedded size codes.
    """
    if not isinstance(product_ids, (list, tuple)) or not product_ids:
        return (
            jsonify(
                {"error": "Invalid product_ids: expected a non-empty list or tuple"}
            ),
            400,
        )

    product_api = get_product_api()

    try:
        status_code, reason, product_data = product_api.get_product_info_with_sizecode(
            params=product_ids
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return handle_api_response(
        status_code, reason, product_data, parse_func=parse_product_info
    )


def handle_full_product_with_size(product_id, size_id):
    """
    Handler for getting full information about a product with a specific size code.
    """
    product_api = get_product_api()

    try:
        status_code, reason, product_data = (
            product_api.get_product_full_info_with_sizecode(
                params=[product_id, size_id]
            )
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return handle_api_response(
        status_code, reason, product_data, parse_func=parse_full_product_info
    )


def handle_full_product_with_ean(ean):
    """
    Handler for getting full information about a product using its EAN code.
    """
    product_api = get_product_api()

    try:
        status_code, reason, product_data = product_api.get_product_full_info_with_ean(
            params=ean
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return handle_api_response(
        status_code, reason, product_data, parse_func=parse_full_product_info
    )


def handle_full_products(request, results_page=0, results_limit=50):
    """
    Handler for getting information about all products with pagination and a dynamic results limit,
    with a constraint of results_limit between 1 and 100.
    """
    product_api = get_product_api()

    payload = {"params": {"resultsPage": results_page, "resultsLimit": results_limit}}
    try:
        status_code, reason, product_data = product_api.get_products_info(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if status_code == 200:
        base_url = request.base_url.rsplit("/", 1)[0]
        try:
            data = parse_full_products_info(product_data, base_url)
        except Exception as e:
            return jsonify({"error": f"Parsing error: {str(e)}"}), 500
        return jsonify(data), 200
    else:
        return jsonify({"error": reason}), status_code
