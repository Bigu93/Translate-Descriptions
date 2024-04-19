import json
from flask import jsonify
from utils import internal_server_error, invalid_json_format
from openai import OpenAI
from config import OPENAI_API_KEY, PROMPT_GENERATE

CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def handle_generate_description(request):
    """
    Handler for generating description.
    """
    if request.method != "POST":
        return jsonify({"error": "Unsupported method!"}), 400

    if request.method == "POST":
        data = request.json
        image_links = data.get("imageUrls", [])
        description = generate_description(image_links)

        return jsonify(
            {
                "description": description.choices[0].message.content,
                "prompt_tokens": description.usage.prompt_tokens,
                "total_tokens": description.usage.total_tokens,
            }
        )


def generate_description(image_links):
    """
    Generate description based on provided prompt and images.
    """

    model = "gpt-4-turbo"
    messages = []
    system_prompt = PROMPT_GENERATE

    messages = [
        {
            "type": "text",
            "text": system_prompt,
        }
    ]

    for link in image_links:
        messages.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": link,
                },
            }
        )

    try:
        response = CLIENT.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": messages,
                }
            ],
            max_tokens=4096,
            temperature=0.7,
        )
        return response
    except json.JSONDecodeError as e:
        invalid_json_format(e, response)
    except Exception as e:
        internal_server_error(e)
