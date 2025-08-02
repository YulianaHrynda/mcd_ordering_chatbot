# backend/chat/handlers/dessert.py

from typing import Dict, Optional
import re
from backend.llm.schema import Item
from backend.chat.message_gen import generate_system_message
from backend.menu.loader import load_menus
from backend.menu.pricing import get_price

# normalize helper
def _normalize(text: str) -> str:
    t = re.sub(r"[^\w\s]", " ", text).lower()
    return re.sub(r"\s+", " ", t).strip()

# same dessert synonyms
_MANUAL_DESSERT_SYNONYMS = {
    "apple pie": "Apple Pie",
    "oreomacflurry": "McFlurry with Oreo",
    "m&m's mcflurry": "McFlurry with M&M's",
    "soft serve": "Soft Serve Cone",
    "soft serve cone": "Soft Serve Cone",
    "cookie": "Chocolate Chip Cookie",
    "chocolate chip cookie": "Chocolate Chip Cookie",
    "sundae": "Sundae",
}

def _all_menu_items():
    menu = load_menus()
    flat = []
    for v in menu.values():
        if isinstance(v, list):
            flat.extend(v)
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list):
                    flat.extend(vv)
    return flat

async def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    # 1) First‐time offer
    if not session["upsell_flags"].get("dessert_offered_done"):
        if any(it.type in ("burger","combo") for it in session["order"]):
            session["upsell_flags"]["dessert_offered_done"] = True
            desserts = [i["name"] for i in _all_menu_items() if i.get("category")=="desserts"]
            instruction = (
                "You are McBot. Suggest a dessert upsell, listing each option: "
                + ", ".join(desserts)
            )
            prompt = await generate_system_message(session["history"], instruction)
            session["history"].append({"role":"system","content":prompt})
            return {"session_id": session_id, "response": prompt, "finalized": False}

    # 2) Parse or fallback match
    from backend.llm.order_parser import parser_order
    parsed = None
    try:
        parsed = parser_order(message, history=session["history"])
    except:
        parsed = None

    # 2A) If parser really parsed a dessert, add it
    if parsed:
        new_d = [i for i in parsed.items if i.type=="dessert"]
        if new_d:
            d = new_d[0]
            canon = _MANUAL_DESSERT_SYNONYMS.get(d.name.lower(), d.name)
            itm = Item(name=canon, type="dessert", size=None)
            itm.price = get_price(itm)
            session["order"].append(itm)
            summary = "🧾 Current items:\n" + "\n".join(f"- {it.name}: ${it.price:.2f}" for it in session["order"])
            instruction = (
                f"You added {itm.name} (${itm.price:.2f}). Here’s the order so far: {summary}. "
                "Ask if they’d like anything else."
            )
            prompt = await generate_system_message(session["history"], instruction)
            session["history"].append({"role":"system","content":prompt})
            return {"session_id": session_id, "response": prompt, "finalized": False}

    # 2B) Fuzzy‐match free text
    desserts = [i["name"] for i in _all_menu_items() if i.get("category")=="desserts"]
    norm = _normalize(message)
    lookup = { _normalize(d): d for d in desserts }
    lookup.update(_MANUAL_DESSERT_SYNONYMS)
    chosen = lookup.get(norm)
    if chosen:
        itm = Item(name=chosen, type="dessert", size=None)
        itm.price = get_price(itm)
        session["order"].append(itm)
        summary = "🧾 Current items:\n" + "\n".join(f"- {it.name}: ${it.price:.2f}" for it in session["order"])
        instruction = (
            f"You added {itm.name} (${itm.price:.2f}). Here’s the order so far: {summary}. "
            "Ask if they’d like anything else."
        )
        prompt = await generate_system_message(session["history"], instruction)
        session["history"].append({"role":"system","content":prompt})
        return {"session_id": session_id, "response": prompt, "finalized": False}

    # 3) Didn’t catch it—ask again
    desserts = [i["name"] for i in _all_menu_items() if i.get("category")=="desserts"]
    instruction = (
        "You are McBot. The customer’s dessert choice was unclear. "
        "Please ask which dessert they’d like, listing options: " + ", ".join(desserts)
    )
    prompt = await generate_system_message(session["history"], instruction)
    session["history"].append({"role":"system","content":prompt})
    return {"session_id": session_id, "response": prompt, "finalized": False}
