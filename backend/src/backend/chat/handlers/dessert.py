# backend/chat/handlers/dessert.py

from typing import Dict, Optional
from backend.menu.loader import load_menus
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.menu.pricing import get_price

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    2A) Offer a dessert once per order if there's at least one burger/combo.
    2B) Handle user's accept_dessert or decline_dessert intents, listing options correctly.
    """
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"]:
        return None

    new_items = validated["items"]
    intents   = validated["intents"]

    menu = load_menus()
    raw_items = menu.get("items", [])

    if isinstance(raw_items, dict):
        desserts_list = raw_items.get("desserts", [])
    else:
        desserts_list = [itm for itm in raw_items if itm.get("category") == "desserts"]

    dessert_names = [itm["name"] for itm in desserts_list]

    has_eats = any(it.type in ("burger","combo") for it in session["order"])
    if has_eats and not session["upsell_flags"].get("dessert_offered"):
        session["upsell_flags"]["dessert_offered"] = True
        msg = (
            "Would you like to add a dessert? "
            "Here are our options: " + ", ".join(dessert_names)
        )
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    if "accept_dessert" in intents:
        dessert_item = next((i for i in new_items if i.type == "dessert"), None)
        if not dessert_item:
            msg = (
                "Sure! Which dessert would you like? "
                "Options: " + ", ".join(dessert_names)
            )
            session["history"].append({"role": "system", "content": msg})
            return {"session_id": session_id, "response": msg, "finalized": False}

        dessert_item.price = get_price(dessert_item)
        session["order"].append(dessert_item)

        summary = "Current items:\n" + "\n".join(
            f"- {it.name}: ${it.price:.2f}" for it in session["order"]
        )
        msg = (
            f"Great! I've added {dessert_item.name} at ${dessert_item.price:.2f}.\n"
            f"{summary}\n"
            "Is there anything else you'd like?"
        )
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    if "decline_dessert" in intents:
        msg = "No problem—no dessert. Is there anything else you'd like?"
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    return None
