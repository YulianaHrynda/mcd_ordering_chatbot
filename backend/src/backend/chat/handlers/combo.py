# backend/chat/handlers/combo.py

from typing import Dict, Optional
from backend.chat.message_gen import generate_system_message
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.menu.loader import load_menus
from backend.menu.pricing import get_price
from backend.logic.order_engine import process_order_logic

async def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handle 'accept_combo' and 'decline_combo' intents with dynamic messaging:
    - accept_combo: upgrade a burger to a combo, seed pending_slots for drink/fries/sauces
    - decline_combo: mark combo_offered and generate the next prompt via OpenAI
    """
    # 1) Parse & validate
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"]:
        return None

    intents = validated["intents"]

    # 2) ACCEPT COMBO
    if "accept_combo" in intents or "request_drink" in intents:
        combo_item = None
        for it in session["order"]:
            if it.type == "burger":
                it.type = "combo"
                it.name += " Meal" if "Meal" not in it.name else ""
                it.price = get_price(it)
                combo_item = it
                break

        if combo_item is None:
            prompt = "It doesn't look like you have a burger to turn into a combo. What else can I get for you?"
            session["history"].append({"role": "system", "content": prompt})
            return {"session_id": session_id, "response": prompt, "finalized": False}

        session["upsell_flags"]["combo_offered"] = True

        # Prepare slots
        menu = load_menus()
        combo_cfg = next(c for c in menu["virtual_items"]["combos"] if c["name"] == combo_item.name)
        slots = combo_cfg["slots"]
        default_side  = slots["fries"][0]
        drink_opts    = slots["drinks"]
        sauce_opts    = slots.get("sauces", {}).get("options", [])

        seq = ["drinks"] + (["sauces"] if sauce_opts else [])
        session["pending_slots"] = {
            "slot": seq[0],
            "options": slots[seq[0]],
            "combo": combo_item,
            "remaining": seq[1:],
            "all": slots
        }

        # Dynamic prompt
        instruction = (
            f"You are McBot, McDonald's assistant. The customer upgraded to a {combo_item.name} combo "
            f"which includes {default_side} by default. Now ask which drink they'd like "
            f"and list the options: {', '.join(drink_opts)}. "
            f"If sauces are next, tell them they can skip by saying 'no'."
        )
        msg = await generate_system_message(session["history"], instruction)
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    # 3) DECLINE COMBO
    if "decline_combo" in intents:
        session["upsell_flags"]["combo_offered"] = True

        result = process_order_logic(
            {"items": session["order"], "intents": [], "errors": [], "is_valid": True},
            session["upsell_flags"]
        )

        order_summary = ", ".join(f"{it.name} for ${it.price:.2f}" for it in session["order"])
        instruction = (
            f"You are McBot. The customer kept their burger as-is. "
            f"Their order now: {order_summary}. "
            f"Next, {result['system_message']}"
        )
        msg = await generate_system_message(session["history"], instruction)
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    return None
