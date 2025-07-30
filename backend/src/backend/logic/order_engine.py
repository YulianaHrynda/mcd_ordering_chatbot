from backend.llm.schema import Item, OrderResponse
from typing import List, Literal, Dict

def process_order_logic(order: dict, upsell_flags: Dict[str, bool]) -> dict:
    """
    Accepts the result of validate_order() and returns a system message + actions.
    """
    system_lines: List[str] = []
    actions: List[str] = []
    state: Literal["complete", "incomplete", "error"] = "incomplete"

    if not order["is_valid"]:
        return {
            "system_message": "There are issues with your order:\n" + "\n".join(order["errors"]),
            "actions": ["request_clarification"],
            "state": "error",
            "items": order["items"],
            "intents": order.get("intents", [])
        }

    items = order["items"]
    intents = order.get("intents", [])

    if "finalize_order" in intents:
        total = len(items)
        return {
            "system_message": f"Your order is complete. Total items: {total}. Would you like to confirm?",
            "actions": ["finalize"],
            "state": "complete",
            "items": items,
            "intents": intents
        }

    # Count items
    burger_count = sum(1 for item in items if item.type == "burger")
    combo_count = sum(1 for item in items if item.type == "combo")
    dessert_included = any(item.type == "dessert" for item in items)
    has_drink = any(item.type == "drink" for item in items)

    # === Combo upsell ===
    if burger_count > 0 and not upsell_flags.get("combo_offered", False):
        actions.append("offer_combo")
        system_lines.append("Would you like to make it a combo?")

    # === Post-combo upsells ===
    if combo_count > 0:
        if not upsell_flags.get("sauce_offered", False):
            actions.append("offer_sauce")
            # Optional: system_lines.append("Would you like any sauce?")

        if not dessert_included and not upsell_flags.get("dessert_offered", False):
            actions.append("offer_dessert")
            system_lines.append("Would you like to add a dessert?")

        if not has_drink and not upsell_flags.get("drink_requested", False):
            actions.append("request_drink_for_combo")
            system_lines.append("Which drink would you like with your combo?")

    # === Double Deal ===
    if burger_count >= 2 and not upsell_flags.get("double_deal_applied", False):
        actions.append("apply_double_deal")
        system_lines.append("We applied a double deal discount!")

    # === Fallback ===
    if not system_lines:
        system_lines.append("Is there anything else you'd like to add?")

    return {
        "system_message": "\n".join(system_lines).strip(),
        "actions": actions,
        "state": state,
        "items": items,
        "intents": intents
    }
