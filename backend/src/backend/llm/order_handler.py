from openai import OpenAI
from backend.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def process_user_message(message: str) -> str:
    """
    The function which processes user message using gpt-4o-model.
    
    Args:
        message (str): order

    Returns:
        str: message from OpenAI
    """
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful McDonald's order assistant."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()
