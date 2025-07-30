from openai import OpenAI
from backend.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_system_message(history: list[dict], instruction: str) -> str:
    """
    Given the existing conversation history and a short instruction
    (e.g. "Summarize the current items and ask if they want anything else"),
    call the OpenAI Chat API to produce a natural‐language response.
    """
    messages = []

    for turn in history:
        messages.append(turn)

    messages.append({"role": "system", "content": instruction})
    messages.append({"role": "user", "content": ""})

    resp = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=150,
    )
    return resp.choices[0].message.content.strip()
