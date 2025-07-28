from backend.llm.schema import Item, OrderResponse
from typing import List, Literal, Dict

def process_order_logic(order: dict, upsell_flags: Dict[str, bool]) -> dict:
    """
    Приймає результат validate_order() і повертає system message + дії.
    """
    system_message: str = ""
    actions: List[str] = []
    state: Literal["complete", "incomplete", "error"] = "incomplete"

    if not order["is_valid"]:
        system_message = "There are issues with your order:\n" + "\n".join(order["errors"])
        state = "error"
        return {
            "system_message": system_message,
            "actions": ["request_clarification"],
            "state": state,
            "items": order["items"],
            "intents": order.get("intents", [])
        }

    items = order["items"]
    intents = order.get("intents", [])

    if "finalize_order" in intents:
        total = len(items)
        system_message = f"Your order is complete. Total items: {total}. Would you like to confirm?"
        return {
            "system_message": system_message,
            "actions": ["finalize"],
            "state": "complete",
            "items": items,
            "intents": intents
        }

    burger_count = 0
    combo_count = 0
    dessert_offered = any(item.type == "dessert" for item in items)
    has_drink = any(item.type == "drink" for item in items)

    for item in items:
        if item.type == "burger":
            burger_count += 1
        elif item.type == "combo":
            combo_count += 1

    if burger_count > 0 and not upsell_flags.get("combo_offered"):
        actions.append("offer_combo")
        system_message += "Would you like to make it a combo?\n"

    if combo_count > 0:
        if not upsell_flags.get("sauce_offered"):
            actions.append("offer_sauce")
        if not dessert_offered and not upsell_flags.get("dessert_offered"):
            actions.append("offer_dessert")
            system_message += "Would you like to add a dessert?\n"
        if not has_drink and not upsell_flags.get("drink_requested"):
            actions.append("request_drink_for_combo")
            system_message += "Which drink would you like with your combo?\n"

    if burger_count >= 2:
        actions.append("apply_double_deal")
        system_message += "We applied a double deal discount!\n"

    if not system_message.strip():
        system_message = "Is there anything else you'd like to add?"

    return {
        "system_message": system_message.strip(),
        "actions": actions,
        "state": state,
        "items": items,
        "intents": intents
    }
