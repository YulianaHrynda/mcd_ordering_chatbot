import uuid
from typing import Dict, Optional
from backend.chat.message_gen import generate_system_message
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.logic.order_engine import process_order_logic
from backend.menu.pricing import get_price

async def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handle finalize_order intent:
    - Ensure there is at least one item in the session order.
    - Assign prices where missing.
    - Run through process_order_logic → expect 'complete' state.
    - Use OpenAI to craft a dynamic confirmation summary.
    """
    # Parse the message in context and check for finalize_order
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"] or "finalize_order" not in validated["intents"]:
        return None

    # If no items, prompt user to add some
    if not session["order"]:
        msg = "You haven't ordered anything yet. Please add items to your order."
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    # Ensure every item has a price
    for it in session["order"]:
        it.price = it.price or get_price(it)

    # Run the order through logic
    result = process_order_logic(
        {"items": session["order"], "intents": validated["intents"], "errors": [], "is_valid": True},
        session["upsell_flags"]
    )

    # If something’s wrong, let the user know
    if result["state"] != "complete":
        error_msg = "There are issues with your order:\n" + "\n".join(result.get("errors", []))
        session["history"].append({"role": "system", "content": error_msg})
        return {"session_id": session_id, "response": error_msg, "finalized": False}

    # Build a dynamic confirmation using OpenAI
    order_id = str(uuid.uuid4())
    items_list = result["items"]
    total = sum(it.price or 0 for it in items_list)
    names = ", ".join(it.name for it in items_list)

    instruction = (
        "You are McBot, a friendly McDonald's assistant. "
        f"Confirm the completed order with summary: {names} for a total of ${total:.2f}, "
        "include the order ID, and thank the customer."
    )
    confirmation = await generate_system_message(session["history"], instruction)

    session["history"].append({"role": "system", "content": confirmation})

    return {
        "session_id": session_id,
        "response": confirmation,
        "finalized": True,
        "order": {
            "order_id": order_id,
            "items": [it.model_dump() for it in items_list],
            "total": round(total, 2),
            "finalized": True,
            "session_id": session_id
        }
    }
