from openai import OpenAI
from backend.settings import settings
from backend.llm.schema import OrderResponse
from pathlib import Path
import json


client = OpenAI(api_key=settings.OPENAI_API_KEY)

PROMPT_PATH = Path(__file__).parent / "prompts" / "order_parsing.txt"
PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


def parser_order(message: str) -> OrderResponse:
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": message}
        ],
        # response_format={"type": "json"}
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed_json = json.loads(content)

        for item in parsed_json.get("items", []):
            if item.get("size") == "":
                item["size"] = None

        return OrderResponse(**parsed_json)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse model response: {e}\nRaw content: {content}")
