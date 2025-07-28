"""
Main module
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from backend.menu.loader import load_menus
from backend.llm.order_parser import parser_order
from backend.logic.order_validator import validate_order
from backend.logic.order_engine import process_order_logic
from backend.menu.pricing import get_price
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, dict] = {}
orders: List[dict] = []


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class OrderSummary(BaseModel):
    order_id: str
    items: List[dict]
    total: float
    finalized: bool
    session_id: str


@app.get("/")
def root():
    return {"message": "Backend is working!"}


@app.get("/menus")
def get_menus():
    return load_menus()


@app.post("/chat")
async def chat(request: ChatRequest):
    # Session management
    session_id = request.session_id or str(uuid.uuid4())
    session = sessions.setdefault(session_id, {
        "history": [],
        "order": [],  # Accumulated items
        "finalized": False,
        "upsell_flags": {},
    })

    user_message = request.message.strip()
    session["history"].append({"role": "user", "content": user_message})

    # Greeting if first message
    if len(session["history"]) == 1:
        system_message = "Welcome to McDonald's! What can I get you started with?"
        session["history"].append({"role": "system", "content": system_message})
        return {"session_id": session_id, "response": system_message, "finalized": False}

    # LLM order parsing
    try:
        parsed = parser_order(user_message)
    except Exception:
        system_message = "Sorry, I couldn't understand your order. Could you rephrase?"
        session["history"].append({"role": "system", "content": system_message})
        return {"session_id": session_id, "response": system_message, "finalized": False}

    # Validate new items
    validated = validate_order(parsed)
    new_items = validated["items"]
    intents = validated["intents"]

    # Append new items with price if user is adding
    if "add_item" in intents and new_items:
        existing_item_names = {item.name for item in session["order"]}
        for item in new_items:
            if item.name not in existing_item_names:
                item.price = get_price(item)  # ✅ Variant A: pass item object
                session["order"].append(item)

    # If user wants to finalize, process full accumulated order
    if "finalize_order" in intents:
        if not session["order"]:
            system_message = "You haven't ordered anything yet. Please add items to your order."
            session["history"].append({"role": "system", "content": system_message})
            return {"session_id": session_id, "response": system_message, "finalized": False}

        # Ensure all items have price
        for item in session["order"]:
            if item.price is None:
                item.price = get_price(item)

        accumulated_order = {
            "items": session["order"],
            "intents": intents,
            "errors": [],
            "is_valid": True,
        }

        logic_result = process_order_logic(accumulated_order, session["upsell_flags"])
        if logic_result["state"] == "complete":
            order_id = str(uuid.uuid4())
            total = sum(item.price or 0 for item in logic_result["items"])
            order_summary = {
                "order_id": order_id,
                "items": [item.model_dump() for item in logic_result["items"]],
                "total": round(total, 2),
                "finalized": True,
                "session_id": session_id,
            }
            orders.append(order_summary)
            session["finalized"] = True
            session["order"] = []  # Clear after finalization
            system_message = f"Your order total is ${order_summary['total']:.2f}. " + \
                             "You ordered: " + ", ".join([item["name"] for item in order_summary["items"]])
            session["history"].append({"role": "system", "content": system_message})
            return {"session_id": session_id, "response": system_message, "finalized": True, "order": order_summary}
        else:
            system_message = "There are issues with your order:\n" + "\n".join(accumulated_order["errors"])
            session["history"].append({"role": "system", "content": system_message})
            return {"session_id": session_id, "response": system_message, "finalized": False}

    # Otherwise continue building the order
    logic_result = process_order_logic({"items": session["order"], "intents": intents, "errors": [], "is_valid": True}, session["upsell_flags"])
    system_message = logic_result["system_message"]
    session["history"].append({"role": "system", "content": system_message})
    session["upsell_flags"] = {flag: True for flag in logic_result["actions"]}
    return {"session_id": session_id, "response": system_message, "finalized": False}


@app.get("/orders")
def get_orders():
    return orders
