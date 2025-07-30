from typing import Optional, Dict

def handle(session: Dict, message: str, session_id: str) -> Optional[Dict]:
    """
    If this is the first turn (empty history), send the greeting and return a response dict.
    Otherwise return None so next handler can run.
    """
    if not session["history"]:
        greeting = "Welcome to McDonald's! What can I get you started with?"
        session["history"].append({"role": "system", "content": greeting})
        return {"session_id": session_id, "response": greeting, "finalized": False}

    return None
