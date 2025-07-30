from typing import Dict, Optional
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.menu.pricing import get_price

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handles 'add_item' intents:
    1) Parse the message via LLM.
    2) Validate against menu and reject invalid orders immediately.
    3) Add each new, non-duplicate item to session['order'] with price.
    4) If a burger was added and combo not yet offered, offer combo.
    5) Otherwise, show the updated summary and ask if user wants anything else.
    Returns a response dict or None to pass to next handler.
    """
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    
    if not validated["is_valid"]:
        err = (
            "I’m sorry, I couldn’t match that to the menu. "
            "Could you specify exactly what you’d like?"
        )
        session["history"].append({"role": "system", "content": err})
        return {"session_id": session_id, "response": err, "finalized": False}
    
    new_items = validated["items"]
    intents   = validated["intents"]
    
    if "add_item" not in intents or not new_items:
        return None
    
    response_lines = []
    added_burger = None
    existing = {item.name for item in session["order"]}
    
    for item in new_items:
        if item.name not in existing:
            item.price = get_price(item)
            session["order"].append(item)
            response_lines.append(f"Added: {item.name} - ${item.price:.2f}")
            if item.type == "burger":
                added_burger = item
    
    if added_burger and not session["upsell_flags"].get("combo_offered"):
        session["upsell_flags"]["combo_offered"] = True
        msg = (
            "\n".join(response_lines)
            + f"\nWould you like to make your {added_burger.name} a combo?"
        )
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}
    
    summary_lines = [f"- {itm.name}: ${itm.price:.2f}" for itm in session["order"]]
    summary = "Current items:\n" + "\n".join(summary_lines)
    
    response_lines.append(summary)
    response_lines.append("Would you like to add anything else?")
    msg = "\n".join(response_lines)
    
    session["history"].append({"role": "system", "content": msg})
    return {"session_id": session_id, "response": msg, "finalized": False}
