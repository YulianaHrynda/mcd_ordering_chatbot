from pydantic import BaseModel
from typing import Optional, Literal, List

class Item(BaseModel):
    name: str
    type: Literal["burger", "drink", "combo", "fries", "dessert"]
    size: Optional[Literal["small", "medium", "large"]] = None
    price: Optional[float] = None

class OrderResponse(BaseModel):
    items: List[Item]
    intents: List[Literal[
        "add_item",
        "finalize_order",
        "ask_for_clarification",
        "ask_for_upsell",
        "cancel_order"
    ]]
