import json
from flask import jsonify
from utils import internal_server_error, invalid_json_format
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, PROMPT_REPHRASE

CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def handle_rephrase_description(request):
    """
    Handler for rephrasing description.
    """
    if request.method != "POST":
        return jsonify({"error": "Unsupported method!"}), 400

    if request.method == "POST":
        data = request.json
        product_description = data.get("description", "")
        rephrased_description = rephrase_description(product_description)

        return jsonify(
            {
                "description": rephrased_description.choices[0].message.content,
                "prompt_tokens": rephrased_description.usage.prompt_tokens,
                "total_tokens": rephrased_description.usage.total_tokens,
            }
        )


def rephrase_description(product_description):
    """
    Rephrase description based on provided prompt.
    """

    model = OPENAI_MODEL
    system_prompt = PROMPT_REPHRASE

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"{product_description}",
        },
    ]

    try:
        response = CLIENT.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4096,
            temperature=0.6,
        )
        return response
    except json.JSONDecodeError as e:
        invalid_json_format(e, response)
    except Exception as e:
        internal_server_error(e)
