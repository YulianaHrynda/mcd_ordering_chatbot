# backend/chat/handlers/fallback.py

from typing import Dict
from backend.chat.message_gen import generate_system_message
from backend.logic.order_engine import process_order_logic

async def handle(session: Dict, message: str, session_id: str) -> Dict:
    """
    Fallback handler when no other handler has processed the message:
    - Calls process_order_logic with current order + no new intents
    - Uses OpenAI to craft a dynamic follow-up based on the system_message
    """
    # Determine the next upsell/fallback suggestion
    result = process_order_logic(
        {"items": session["order"], "intents": [], "errors": [], "is_valid": True},
        session["upsell_flags"],
    )

    # Summarize current order for context
    order_summary = ", ".join(f"{it.name} for ${it.price:.2f}" for it in session["order"]) or "nothing yet"

    # Build instruction for the LLM
    instruction = (
        "You are McBot, a helpful McDonald's assistant. "
        f"The customer's current order: {order_summary}. "
        f"Now {result['system_message']} "
        "Please phrase this as a friendly question."
    )

    # Generate a dynamic follow-up prompt
    msg = await generate_system_message(session["history"], instruction)

    # Append to history and mark flags
    session["history"].append({"role": "system", "content": msg})
    for flag in result["actions"]:
        session["upsell_flags"][flag] = True

    return {"session_id": session_id, "response": msg, "finalized": False}
