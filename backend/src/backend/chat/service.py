# backend/chat/service.py

import uuid
import inspect
from typing import Optional, Dict
from backend.chat.handlers import (
    greeting,
    slot,
    add_item,
    combo,
    ask_upsell,
    dessert,
    finalize,
    fallback,
)

sessions: Dict[str, dict] = {}


class ChatService:
    async def handle(self, session_id: Optional[str], message: str) -> Dict:
        sid = session_id or str(uuid.uuid4())
        session = sessions.setdefault(sid, {
            "history": [],
            "order": [],
            "upsell_flags": {},
            "pending_slots": None,
        })

        # Try each handler in turn
        for handler in (
            greeting,
            slot,
            add_item,
            combo,
            ask_upsell,
            dessert,
            finalize,
        ):
            result = handler.handle(session, message, sid)
            # if it's a coroutine, await it
            if inspect.isawaitable(result):
                result = await result

            if result is not None:
                return result

        # Always await fallback (it's async)
        return await fallback.handle(session, message, sid)
