from typing import Dict, Optional
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.menu.loader import load_menus
from backend.menu.pricing import get_price
from backend.logic.order_engine import process_order_logic
# from backend.llm.schema import Item

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handle accept_combo and decline_combo intents:
    - accept_combo: upgrade a burger to a combo, seed pending_slots for drink/fries/sauces
    - decline_combo: mark combo_offered and proceed with fallback logic
    """
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"]:
        return None

    intents = validated["intents"]

    if "accept_combo" in intents:
        upgraded = False
        combo_item = None
        for it in session["order"]:
            if it.type == "burger":
                it.type = "combo"
                it.name += " Meal" if "Meal" not in it.name else ""
                it.price = get_price(it)
                combo_item = it
                upgraded = True
                break

        if not upgraded:
            msg = "It looks like there’s no burger to upgrade to a combo. What else can I get you?"
            session["history"].append({"role": "system", "content": msg})
            return {"session_id": session_id, "response": msg, "finalized": False}

        session["upsell_flags"]["combo_offered"] = True

        menus = load_menus()
        combo_cfg = next(c for c in menus["virtual_items"]["combos"] if c["name"] == combo_item.name)
        slots = combo_cfg["slots"]

        default_side = slots["fries"][0]
        drink_options = slots["drinks"]
        sauce_options = slots.get("sauces", {}).get("options", [])

        slot_order = ["drinks"]
        if sauce_options:
            slot_order.append("sauces")

        session["pending_slots"] = {
            "slot": slot_order[0],
            "options": slots[slot_order[0]],
            "combo": combo_item,
            "remaining": slot_order[1:],
            "all": slots
        }

        lines = [
            f"Great choice! Your {combo_item.name} combo includes {default_side} by default.",
            f"Which drink would you like? Options: {', '.join(drink_options)}"
        ]
        if sauce_options:
            lines.append(f"After that, you can add a sauce (or say 'no' to skip): {', '.join(sauce_options)}")
        msg = "\n".join(lines)

        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    if "decline_combo" in intents:
        session["upsell_flags"]["combo_offered"] = True

        summary = "🧾 Current items:\n" + "\n".join(
            f"- {it.name}: ${it.price:.2f}" for it in session["order"]
        )
        next_msg = process_order_logic(
            {"items": session["order"], "intents": intents, "errors": [], "is_valid": True},
            session["upsell_flags"]
        )["system_message"]

        msg = f"No problem. Keeping your burger as-is.\n{summary}\n{next_msg}"
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    return None
