from typing import Dict
from backend.logic.order_engine import process_order_logic

def handle(session: Dict, message: str, session_id: str) -> Dict:
    """
    Fallback handler when no other handler has processed the message:
    - Calls process_order_logic with current order + no new intents
    - Appends the system_message, ensures it ends with a question
    """
    result = process_order_logic(
        {"items": session["order"], "intents": [], "errors": [], "is_valid": True},
        session["upsell_flags"]
    )

    msg = result["system_message"]
    if not msg.endswith("?"):
        msg += " Would you like to add anything else?"

    session["history"].append({"role": "system", "content": msg})
    for flag in result["actions"]:
        session["upsell_flags"][flag] = True

    return {"session_id": session_id, "response": msg, "finalized": False}
