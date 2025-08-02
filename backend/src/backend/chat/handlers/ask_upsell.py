# backend/chat/handlers/ask_upsell.py

from typing import Dict, Optional
from backend.chat.message_gen import generate_system_message
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.logic.order_engine import process_order_logic

async def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handle the 'ask_for_upsell' intent by:
    1) Re-running process_order_logic on the current order to find outstanding upsells.
    2) Generating a dynamic upsell prompt via OpenAI.
    """
    # 1) Parse & validate for intents
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"]:
        return None

    if "ask_for_upsell" not in validated["intents"]:
        return None

    # 2) Determine what upsells are available
    result = process_order_logic(
        {"items": session["order"], "intents": [], "errors": [], "is_valid": True},
        session["upsell_flags"]
    )
    # Mark offered flags so they won't repeat
    for flag in result["actions"]:
        session["upsell_flags"][flag] = True

    # 3) Build a concise instruction describing the needed upsell
    #    Include current items + what the system_message suggests.
    order_summary = ", ".join(f"{it.name} for ${it.price:.2f}" for it in session["order"])
    instruction = (
        "You are McBot, a friendly McDonald's assistant. "
        f"The customer currently has: {order_summary}. "
        "Based on this, suggest the next upsell helping them complete their order, "
        "using the guidelines in the system message: "
        f"\"{result['system_message']}\""
    )

    # 4) Generate a dynamic prompt via OpenAI
    msg = await generate_system_message(session["history"], instruction)

    # 5) Record and return
    session["history"].append({"role": "system", "content": msg})
    return {"session_id": session_id, "response": msg, "finalized": False}
