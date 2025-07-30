# backend/main.py

from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from backend.menu.loader import load_menus
from backend.chat.service import ChatService

app = FastAPI()
router = APIRouter()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orders: List[dict] = []

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

@router.post("/")
async def chat(req: ChatRequest, svc: ChatService = Depends()):
    return await svc.handle(req.session_id, req.message)

app.include_router(router, prefix="/chat", tags=["chat"])

@app.get("/")
def root():
    return {"message": "Backend is working!"}

@app.get("/menus")
def get_menus():
    return load_menus()

@app.get("/orders")
def get_orders():
    return orders


# @app.post("/chat")
# async def chat(request: ChatRequest):
#     session_id = request.session_id or str(uuid.uuid4())
#     session = sessions.setdefault(session_id, {
#         "history": [],
#         "order": [],
#         "finalized": False,
#         "upsell_flags": {},
#         "pending_slots": None,
#     })

#     user_message = request.message.strip()

#     # 1) First-time greeting
#     if not session["history"]:
#         greeting = "Welcome to McDonald's! What can I get you started with?"
#         session["history"].append({"role": "system", "content": greeting})
#         return {"session_id": session_id, "response": greeting, "finalized": False}

#     session["history"].append({"role": "user", "content": user_message})

#     # 2) Handle pending combo slots (drink, fries, sauces)
#     slot_info = session.get("pending_slots")
#     if slot_info:
#         selected = user_message.strip()

#         # allow skipping optional sauces
#         if slot_info["slot"] == "sauces" and selected.lower() in ["none", "no", "skip"]:
#             selected_item = None
#         else:
#             valid = slot_info["options"]
#             matched = next((opt for opt in valid if opt.lower() in selected.lower()), None)
#             if not matched:
#                 msg = (
#                     f"Sorry, I didn’t catch that. Please choose one of the following "
#                     f"{slot_info['slot']}: {', '.join(valid)}"
#                 )
#                 return {"session_id": session_id, "response": msg, "finalized": False}
#             selected_item = matched

#         # add selected slot item
#         if selected_item:
#             obj = Item(name=selected_item, type=slot_info["slot"][:-1])
#             obj.price = get_price(obj)
#             session["order"].append(obj)

#         # next slot or finish
#         if slot_info["remaining"]:
#             next_slot = slot_info["remaining"].pop(0)
#             session["pending_slots"]["slot"] = next_slot
#             session["pending_slots"]["options"] = slot_info["all"][next_slot]
#             opts = slot_info["all"][next_slot]
#             msg = f"What would you like for your {next_slot}? Options: {', '.join(opts)}"
#             session["history"].append({"role": "system", "content": msg})
#             return {"session_id": session_id, "response": msg, "finalized": False}

#         # all slots done
#         session["pending_slots"] = None
#         summary = "🧾 Current items:\n" + "\n".join(
#             f"- {i.name}: ${i.price:.2f}" for i in session["order"]
#         )
#         added = selected_item if selected_item else "No sauce"
#         msg = (
#             f"Got it! {added} added to your combo.\n"
#             f"{summary}\n"
#             "Would you like to add anything else?"
#         )
#         session["history"].append({"role": "system", "content": msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}

#     # 3) Normal flow: parse user intent
#     try:
#         parsed = parser_order(user_message, history=session["history"])
#     except Exception:
#         err = "Sorry, I couldn't understand your order. Could you rephrase?"
#         session["history"].append({"role": "system", "content": err})
#         return {"session_id": session_id, "response": err, "finalized": False}

#     validated = validate_order(parsed)

#     if not validated["is_valid"]:
#         err_msg = (
#             "I’m sorry, I couldn’t match that to the menu. "
#             "Could you specify exactly what you’d like?"
#         )
#         session["history"].append({"role": "system", "content": err_msg})
#         return {"session_id": session_id, "response": err_msg, "finalized": False}

#     new_items = validated["items"]
#     intents   = validated["intents"]

#     response_lines = []
#     added_burger = None

#     # 4) Handle add_item
#     if "add_item" in intents and new_items:
#         existing = {it.name for it in session["order"]}
#         for it in new_items:
#             if it.name not in existing:
#                 it.price = get_price(it)
#                 session["order"].append(it)
#                 response_lines.append(f"✅ Added: {it.name} - ${it.price:.2f}")
#                 if it.type == "burger":
#                     added_burger = it

#         # after adding a burger, offer combo
#         if added_burger and not session["upsell_flags"].get("combo_offered"):
#             session["upsell_flags"]["combo_offered"] = True
#             msg = (
#                 "\n".join(response_lines)
#                 + f"\nWould you like to make your {added_burger.name} a combo?"
#             )
#             session["history"].append({"role": "system", "content": msg})
#             return {"session_id": session_id, "response": msg, "finalized": False}

#         # otherwise show current items
#         summary = "🧾 Current items:\n" + "\n".join(
#             f"- {it.name}: ${it.price:.2f}" for it in session["order"]
#         )
#         response_lines.append(summary)
#         response_lines.append("Would you like to add anything else?")
#         msg = "\n".join(response_lines)
#         session["history"].append({"role": "system", "content": msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}

#     # 5) Handle accept_combo with specific prompts
#     if "accept_combo" in intents:
#         upgraded = False
#         combo_item = None
#         for it in session["order"]:
#             if it.type == "burger":
#                 it.type = "combo"
#                 it.name += " Meal" if "Meal" not in it.name else ""
#                 it.price = get_price(it)
#                 combo_item = it
#                 upgraded = True
#                 break

#         if not upgraded:
#             msg = "It looks like there’s no burger to upgrade to a combo. What else can I get you?"
#             session["history"].append({"role": "system", "content": msg})
#             return {"session_id": session_id, "response": msg, "finalized": False}

#         session["upsell_flags"]["combo_offered"] = True

#         # fetch combo slots from menu
#         menu = load_menus()
#         combo_cfg = next(c for c in menu["virtual_items"]["combos"] if c["name"] == combo_item.name)
#         slots = combo_cfg["slots"]
#         default_side = slots["fries"][0]
#         drinks = slots["drinks"]
#         sauces = slots.get("sauces", {}).get("options", [])

#         # set up pending_slots order
#         slot_order = ["drinks"]
#         if sauces:
#             slot_order.append("sauces")
#         session["pending_slots"] = {
#             "slot": slot_order[0],
#             "options": slots[slot_order[0]],
#             "combo": combo_item,
#             "remaining": slot_order[1:],
#             "all": slots
#         }

#         # build prompt
#         lines = [
#             f"Great choice! Your {combo_item.name} combo includes {default_side} by default.",
#             f"Which drink would you like? Options: {', '.join(drinks)}"
#         ]
#         if sauces:
#             lines.append(f"After that, you can add a sauce (or say 'no' to skip): {', '.join(sauces)}")
#         msg = "\n".join(lines)

#         session["history"].append({"role": "system", "content": msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}

#     # 6) Handle decline_combo
#     if "decline_combo" in intents:
#         session["upsell_flags"]["combo_offered"] = True
#         summary = "🧾 Current items:\n" + "\n".join(
#             f"- {it.name}: ${it.price:.2f}" for it in session["order"]
#         )
#         next_msg = process_order_logic(
#             {"items": session["order"], "intents": intents, "errors": [], "is_valid": True},
#             session["upsell_flags"]
#         )["system_message"]
#         msg = f"No problem. Keeping your burger as-is.\n{summary}\n{next_msg}"
#         session["history"].append({"role": "system", "content": msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}


#     # — after your accept_combo / decline_combo blocks but before finalize —

#     #  — 2A) OFFER DESSERT if user has any burger/combo and we haven't yet —
#     has_eat = any(it.type in ("burger","combo") for it in session["order"])
#     if has_eat and not session["upsell_flags"].get("dessert_offered"):
#         session["upsell_flags"]["dessert_offered"] = True

#         # pull all dessert names from your menu
#         desserts = [
#             itm["name"]
#             for itm in load_menus()["items"]
#             if itm["category"] == "desserts"
#         ]
#         msg = (
#             "Would you like to add a dessert? "
#             "Here are our options: " + ", ".join(desserts)
#         )
#         session["history"].append({"role":"system","content":msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}

#     # — 2B) USER SAYS “YES” TO DESSERT —
#     if "accept_dessert" in intents:
#         # If parser already pulled a dessert item, use that; otherwise ask “which one?”
#         dessert_item = next((i for i in new_items if i.type == "dessert"), None)
#         if not dessert_item:
#             # clarification slot
#             desserts = [
#                 itm["name"]
#                 for itm in load_menus()["items"]
#                 if itm["category"] == "desserts"
#             ]
#             msg = (
#                 "Sure! Which dessert would you like? "
#                 "Options: " + ", ".join(desserts)
#             )
#             session["history"].append({"role":"system","content":msg})
#             return {"session_id": session_id, "response": msg, "finalized": False}
#         # actually add it
#         dessert_item.price = get_price(dessert_item)
#         session["order"].append(dessert_item)
#         summary = "🧾 Current items:\n" + "\n".join(
#             f"- {it.name}: ${it.price:.2f}" for it in session["order"]
#         )
#         msg = (
#             f"Great! I've added {dessert_item.name} to your order.\n"
#             f"{summary}\n"
#             "Is there anything else you'd like?"
#         )
#         session["history"].append({"role":"system","content":msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}

#     # — 2C) USER SAYS “NO” TO DESSERT —
#     if "decline_dessert" in intents:
#         msg = "No problem—no dessert. Is there anything else you'd like?"
#         session["history"].append({"role":"system","content":msg})
#         return {"session_id": session_id, "response": msg, "finalized": False}


#     # 7) Handle finalize_order
#     if "finalize_order" in intents:
#         if not session["order"]:
#             msg = "You haven't ordered anything yet. Please add items to your order."
#             session["history"].append({"role": "system", "content": msg})
#             return {"session_id": session_id, "response": msg, "finalized": False}

#         for it in session["order"]:
#             it.price = it.price or get_price(it)

#         result = process_order_logic(
#             {"items": session["order"], "intents": intents, "errors": [], "is_valid": True},
#             session["upsell_flags"]
#         )
#         if result["state"] == "complete":
#             order_id = str(uuid.uuid4())
#             total = sum(i.price or 0 for i in result["items"])
#             summary = {
#                 "order_id": order_id,
#                 "items": [i.model_dump() for i in result["items"]],
#                 "total": round(total, 2),
#                 "finalized": True,
#                 "session_id": session_id,
#             }
#             orders.append(summary)
#             session["finalized"] = True
#             session["order"] = []
#             msg = (
#                 f"Your order total is ${summary['total']:.2f}. You ordered: "
#                 + ", ".join(i["name"] for i in summary["items"])
#             )
#             session["history"].append({"role": "system", "content": msg})
#             return {"session_id": session_id, "response": msg, "finalized": True, "order": summary}
#         else:
#             msg = "There are issues with your order:\n" + "\n".join(result.get("errors", []))
#             session["history"].append({"role": "system", "content": msg})
#             return {"session_id": session_id, "response": msg, "finalized": False}

#     # 8) Fallback: continue conversation
#     fallback = process_order_logic(
#         {"items": session["order"], "intents": intents, "errors": [], "is_valid": True},
#         session["upsell_flags"]
#     )
#     msg = fallback["system_message"]
#     if not msg.endswith("?"):
#         msg += " Would you like to add anything else?"
#     session["history"].append({"role": "system", "content": msg})
#     session["upsell_flags"].update({flag: True for flag in fallback["actions"]})

#     return {"session_id": session_id, "response": msg, "finalized": False}
