from typing import Optional, Dict
import uuid
from backend.chat.handlers import (
    greeting,
    slot,
    add_item,
    combo,
    dessert,
    finalize,
    fallback,
    ask_upsell
)

sessions: Dict[str, dict] = {}


class ChatService:
    async def handle(self, session_id: Optional[str], message: str) -> Dict:
        sid = session_id or str(uuid.uuid4())
        session = sessions.setdefault(
            sid,
            {
                "history": [],
                "order": [],
                "upsell_flags": {},
                "pending_slots": None,
            },
        )

        for handler in (
            greeting,
            slot,
            add_item,
            combo,
            ask_upsell,
            dessert,
            finalize,
        ):
            resp = handler.handle(session, message, sid)
            if resp is not None:
                return resp

        return fallback.handle(session, message, sid)
