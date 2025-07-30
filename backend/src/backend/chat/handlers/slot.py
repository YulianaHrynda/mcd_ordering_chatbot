from typing import Dict, Optional
import re
from backend.llm.schema import Item
from backend.menu.pricing import get_price

def _normalize(text: str) -> str:
    s = re.sub(r"[^\w\s]", " ", text.lower()).strip()
    return re.sub(r"\s+", " ", s)

_MANUAL_SYNONYMS = {
    "coke": "Coca-Cola",
    "coca cola": "Coca-Cola",
    "ff": "French Fries",
    "fries": "French Fries",
    "potato dips": "Potato Dips",
    "dip": "Potato Dips",
}

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    slot_info = session.get("pending_slots")
    if not slot_info:
        return None

    user_choice = message.strip()
    norm_choice = _normalize(user_choice)

    opts = slot_info["options"]
    lookup = {}
    for opt in opts:
        norm_opt = _normalize(opt)
        lookup[norm_opt] = opt
        lookup[norm_opt.replace("-", " ")] = opt
    for k, v in _MANUAL_SYNONYMS.items():
        lookup[k] = v

    if slot_info["slot"] == "sauces" and norm_choice in ("none", "no", "skip"):
        selected = None
    else:
        selected = lookup.get(norm_choice)
        if not selected:
            msg = (
                f"Sorry, I didn’t catch that. Please choose one of the following "
                f"{slot_info['slot']}: {', '.join(opts)}"
            )
            return {"session_id": session_id, "response": msg, "finalized": False}

    if selected:
        itm = Item(name=selected, type=slot_info["slot"][:-1])
        itm.price = get_price(itm)
        session["order"].append(itm)

    if slot_info["remaining"]:
        nxt = slot_info["remaining"].pop(0)
        session["pending_slots"]["slot"]    = nxt
        session["pending_slots"]["options"] = slot_info["all"][nxt]
        opts_next = slot_info["all"][nxt]
        prompt = f"What would you like for your {nxt}? Options: {', '.join(opts_next)}"
        session["history"].append({"role":"system","content":prompt})
        return {"session_id": session_id, "response": prompt, "finalized": False}

    session["pending_slots"] = None
    summary = "Current items:\n" + "\n".join(
        f"- {i.name}: ${i.price:.2f}" for i in session["order"]
    )
    added = selected if selected else "No sauce"
    msg = (
        f"Got it! {added} added to your combo.\n"
        f"{summary}\n"
        "Would you like to add anything else?"
    )
    session["history"].append({"role":"system","content":msg})
    return {"session_id": session_id, "response": msg, "finalized": False}
