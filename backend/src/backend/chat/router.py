from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from .service import ChatService

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

@router.post("/chat")
async def chat(req: ChatRequest, svc: ChatService = Depends()):
    return await svc.handle(req.session_id, req.message)
