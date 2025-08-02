from typing import Dict, Optional
import re
from backend.llm.schema import Item
from backend.menu.pricing import get_price
from backend.chat.message_gen import generate_system_message

# normalize text for matching
def _normalize(text: str) -> str:
    s = re.sub(r"[^\w\s]", " ", text.lower()).strip()
    return re.sub(r"\s+", " ", s)

# manual synonyms for quick lookup
_MANUAL_SYNONYMS = {
    "coke": "Coca-Cola",
    "coca cola": "Coca-Cola",
    "ff": "French Fries",
    "fries": "French Fries",
    "potato dips": "Potato Dips",
    "dip": "Potato Dips",
}

async def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Slot handler for combo customization (drinks, fries, sauces).
    Uses generate_system_message for dynamic prompts.
    """
    slot_info = session.get("pending_slots")
    if not slot_info:
        return None

    user_choice = message.strip()
    norm_choice = _normalize(user_choice)

    # build lookup table of normalized options
    opts = slot_info["options"]
    lookup: Dict[str, str] = {}
    for opt in opts:
        norm_opt = _normalize(opt)
        lookup[norm_opt] = opt
        lookup[norm_opt.replace("-", " ")] = opt
    # include manual synonyms
    for k, v in _MANUAL_SYNONYMS.items():
        lookup[k] = v

    # determine selection or skip for optional sauces
    if slot_info["slot"] == "sauces" and norm_choice in ("none", "no", "skip"):
        selected = None
    else:
        selected = lookup.get(norm_choice)
        if not selected:
            # dynamic error prompt
            instruction = (
                "You are McBot, a helpful McDonald's assistant. "
                f"The customer was asked to choose a {slot_info['slot']}, but their reply "
                f"was unclear. Please ask again and list the options: {', '.join(opts)}."
            )
            msg = await generate_system_message(session["history"], instruction)
            session["history"].append({"role": "system", "content": msg})
            return {"session_id": session_id, "response": msg, "finalized": False}

    # if an item is selected, add it
    if selected:
        itm = Item(name=selected, type=slot_info["slot"][:-1])
        itm.price = get_price(itm)
        session["order"].append(itm)

    # proceed to next slot if any
    if slot_info["remaining"]:
        next_slot = slot_info["remaining"].pop(0)
        session["pending_slots"]["slot"]    = next_slot
        session["pending_slots"]["options"] = slot_info["all"][next_slot]
        opts_next = slot_info["all"][next_slot]
        instruction = (
            "You are McBot. After adding the previous item, ask the customer "
            f"what they would like for their {next_slot} and list options: {', '.join(opts_next)}."
        )
        msg = await generate_system_message(session["history"], instruction)
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    # all slots completed
    session["pending_slots"] = None
    added_text = selected if selected else "No sauce"
    order_summary = ", ".join(f"{i.name} for ${i.price:.2f}" for i in session["order"])
    instruction = (
        "You are McBot. The customer finished customizing their combo. "
        f"You added '{added_text}'. The current order contains: {order_summary}. "
        "Summarize this to the customer and ask if they’d like anything else."
    )
    msg = await generate_system_message(session["history"], instruction)
    session["history"].append({"role": "system", "content": msg})
    return {"session_id": session_id, "response": msg, "finalized": False}
