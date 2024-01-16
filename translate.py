from flask import jsonify


def handle_translate_request(request, product_id):
    if request.method != "POST":
        return jsonify({"error": "Nie wspierana metoda!"}), 400

    if not product_id:
        return jsonify({"error": "Wymagane ID produktu!"}), 400

    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"error": "Nie podano wysłano payloadu!"}), 400

        if "params" not in data or "products" not in data["params"]:
            return jsonify({"error": "Niepoprawny format danych!"}), 400

        try:
            return jsonify(data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
