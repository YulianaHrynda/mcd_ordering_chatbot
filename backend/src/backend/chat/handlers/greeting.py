from typing import Optional, Dict
from backend.chat.message_gen import generate_system_message

async def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    If this is the first turn (empty history), dynamically generate
    a friendly greeting and question for the user.
    """
    if not session["history"]:
        instruction = (
            "You are McBot, a friendly virtual assistant for McDonald’s. "
            "Greet the customer warmly and ask what they would like to order."
        )
        greeting = await generate_system_message(session["history"], instruction)

        session["history"].append({"role": "system", "content": greeting})
        return {
            "session_id": session_id,
            "response": greeting,
            "finalized": False
        }

    return None
