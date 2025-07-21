"""
Main module
"""

from fastapi import FastAPI
from pydantic import BaseModel
from backend.menu.loader import load_menus
from backend.order_handler import process_user_message

app = FastAPI()


class MessageRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Backend is working!"}


@app.get("/menus")
def get_menus():
    return load_menus()


@app.post("/order")
async def order(request: MessageRequest):
    reply = process_user_message(request.message)
    return {"response": reply}
