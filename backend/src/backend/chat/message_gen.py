from openai import OpenAI
from backend.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_system_message(history: list[dict], instruction: str) -> str:
    """
    Given conversation history and an instruction, produce
    a dynamic system message via the Chat API.
    """
    messages = []
    messages.extend(history)
    messages.append({"role": "system", "content": instruction})
    messages.append({"role": "user", "content": ""})

    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=150,
    )
    return resp.choices[0].message.content.strip()
