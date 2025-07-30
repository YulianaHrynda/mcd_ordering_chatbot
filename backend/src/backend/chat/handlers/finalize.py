from typing import Dict, Optional
import uuid
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.logic.order_engine import process_order_logic
from backend.menu.pricing import get_price

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handle finalize_order intent:
    - Validate that there is at least one item
    - Ensure all items have prices
    - Run through process_order_logic → should be complete
    - Return total summary + “order” payload
    """
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"]:
        return None

    intents = validated["intents"]
    if "finalize_order" not in intents:
        return None

    if not session["order"]:
        msg = "You haven't ordered anything yet. Please add items to your order."
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    for it in session["order"]:
        it.price = it.price or get_price(it)

    result = process_order_logic(
        {"items": session["order"], "intents": intents, "errors": [], "is_valid": True},
        session["upsell_flags"]
    )

    if result["state"] != "complete":
        msg = "There are issues with your order:\n" + "\n".join(result.get("errors", []))
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    order_id = str(uuid.uuid4())
    items_data = [i.model_dump() for i in result["items"]]
    total = sum(i.price or 0 for i in result["items"])
    summary_msg = (
        f"Your order total is ${total:.2f}. "
        f"You ordered: {', '.join(item['name'] for item in items_data)}"
    )

    session["history"].append({"role": "system", "content": summary_msg})

    return {
        "session_id": session_id,
        "response": summary_msg,
        "finalized": True,
        "order": {
            "order_id": order_id,
            "items": items_data,
            "total": round(total, 2),
            "finalized": True,
            "session_id": session_id
        }
    }
