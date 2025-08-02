# backend/chat/handlers/add_item.py

from typing import Dict, Optional
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.menu.loader import load_menus
from backend.menu.pricing import get_price
from backend.llm.schema import Item

# dessert synonyms for fallback mapping
_DESSERT_SYNONYMS = {
    "oreo mcflurry": "McFlurry with Oreo",
    "mcflurry with oreo": "McFlurry with Oreo",
    "m&m's mcflurry": "McFlurry with M&M's",
    "soft serve cone": "Soft Serve Cone",
    "soft serve": "Soft Serve Cone",
    "apple pie": "Apple Pie",
    "cookie": "Chocolate Chip Cookie",
    "chocolate chip cookie": "Chocolate Chip Cookie",
    "sundae": "Sundae",
}

def _all_menu_items():
    menu = load_menus()
    flat = []
    # flatten every list in your menu dict
    for v in menu.values():
        if isinstance(v, list):
            flat.extend(v)
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list):
                    flat.extend(vv)
    return flat

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    parsed    = parser_order(message, history=session["history"])
    validated = validate_order(parsed)

    # — If validation failed but parser is already asking for a combo‐slot (e.g. request_drink),
    #    bail out so the combo handler can run —
    if not validated["is_valid"] and any(
        intent in ("request_drink","request_size","request_sauce")
        for intent in parsed.intents
    ):
        return None

    # 1) Normal valid‐order flow
    if validated["is_valid"]:
        new_items = validated["items"]
        if "add_item" not in validated["intents"] or not new_items:
            return None

        added_burger = None
        resp_lines   = []
        existing     = {it.name for it in session["order"]}

        for it in new_items:
            if it.name not in existing:
                it.price = get_price(it)
                session["order"].append(it)
                resp_lines.append(f"✅ Added: {it.name} – ${it.price:.2f}")
                if it.type == "burger":
                    added_burger = it

        # burger → combo upsell
        if added_burger and not session["upsell_flags"].get("combo_offered"):
            session["upsell_flags"]["combo_offered"] = True
            msg = (
                "\n".join(resp_lines)
                + f"\nWould you like to make your {added_burger.name} a combo?"
            )
            session["history"].append({"role":"system","content":msg})
            return {"session_id": session_id, "response": msg, "finalized": False}

        # otherwise show summary
        summary = "🧾 Current items:\n" + "\n".join(
            f"- {it.name}: ${it.price:.2f}" for it in session["order"]
        )
        resp_lines.append(summary)
        resp_lines.append("Would you like to add anything else?")
        msg = "\n".join(resp_lines)
        session["history"].append({"role":"system","content":msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    # 2) Validation failed—but maybe they meant a dessert?
    all_items       = _all_menu_items()
    dessert_names   = [i["name"] for i in all_items if i.get("category")=="desserts"]
    parsed_desserts = [it for it in parsed.items if it.type=="dessert"]

    if parsed_desserts:
        added = []
        for pd in parsed_desserts:
            key   = pd.name.lower().strip()
            canon = (
                _DESSERT_SYNONYMS.get(key)
                or next((d for d in dessert_names if key in d.lower()), None)
            )
            if not canon:
                continue
            itm = Item(name=canon, type="dessert", size=None)
            itm.price = get_price(itm)
            session["order"].append(itm)
            added.append(f"{itm.name} – ${itm.price:.2f}")

        if added:
            lines = [
                "✅ Added dessert: " + ", ".join(added),
                "🧾 Current items:\n"
                + "\n".join(f"- {it.name}: ${it.price:.2f}" for it in session["order"]),
                "Would you like to add anything else?"
            ]
            msg = "\n".join(lines)
            session["history"].append({"role":"system","content":msg})
            return {"session_id": session_id, "response": msg, "finalized": False}

    # 3) Still no match → genuine error
    err = (
        "I’m sorry, I couldn’t match that to the menu. "
        "Could you specify exactly what you’d like?"
    )
    session["history"].append({"role":"system","content":err})
    return {"session_id": session_id, "response": err, "finalized": False}
