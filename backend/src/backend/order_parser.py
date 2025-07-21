from openai import OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMT = """"
You are a McDonald's ordering assistant AI. Your job is to extract structured order information from the customer's message.

Respond only with a valid JSON object in the following format:

{
  "items": [
    {"name": "<item name>", "type": "burger|drink|combo|fries|dessert", "size": "<small|medium|large>" (if applicable)}
  ],
  "intents": [
    "add_item",
    "finalize_order",
    "ask_for_clarification",
    "ask_for_upsell",
    "cancel_order"
  ]
}

Do not include any explanation. Only output the JSON object.
"""

def parser_order(message: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PROMT},
            {"role": "user", "content": message}
        ],
        # response_format="json"
    )

    content = response.choices[0].message.content.strip()

    return json.loads(content)
