# backend/chat/handlers/ask_upsell.py

from typing import Dict, Optional
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.logic.order_engine import process_order_logic

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    Handle the 'ask_for_upsell' intent by rerunning process_order_logic
    on the current order to surface any outstanding upsells (sauce, dessert, etc).
    """
    parsed = parser_order(message, history=session["history"])
    validated = validate_order(parsed)
    if not validated["is_valid"]:
        return None

    if "ask_for_upsell" in validated["intents"]:
        result = process_order_logic(
            {"items": session["order"], "intents": [], "errors": [], "is_valid": True},
            session["upsell_flags"]
        )
        msg = result["system_message"]

        for flag in result["actions"]:
            session["upsell_flags"][flag] = True
        session["history"].append({"role": "system", "content": msg})
        return {"session_id": session_id, "response": msg, "finalized": False}

    return None
