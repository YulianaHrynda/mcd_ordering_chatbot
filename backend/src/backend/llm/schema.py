from pydantic import BaseModel, Field
from typing import Optional, Literal, List

class Item(BaseModel):
    name: str
    type: str  # 👈 тимчасово
    size: Optional[str] = None
    price: Optional[float] = None


class OrderResponse(BaseModel):
    items: List[Item] = Field(default_factory=list)
    intents: List[Literal[
        "add_item",
        "finalize_order",
        "ask_for_clarification",
        "ask_for_upsell",
        "cancel_order",
        "accept_combo",
        "decline_combo",
        "accept_dessert",
        "decline_dessert"
    ]] = Field(default_factory=list)

