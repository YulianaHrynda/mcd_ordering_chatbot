"""
Main module
"""

from fastapi import FastAPI
from pydantic import BaseModel
from backend.menu.loader import load_menus
from backend.order_handler import process_user_message
from backend.order_parser import parser_order
from backend.order_validator import validate_order

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

@app.post("/parse")
async def parse(request: MessageRequest):
    parsed = parser_order(request.message)
    return {"parsed": parsed}

@app.post("/order/validate")
async def validate(request: MessageRequest):
    parsed = parser_order(request.message)
    validated = validate_order(parsed)
    return validated
