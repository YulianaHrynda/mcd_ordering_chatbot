from backend.menu.loader import load_menus
from backend.llm.schema import OrderResponse, Item
from backend.menu.pricing import get_price
from typing import List, Dict

menus = load_menus()

name_aliases: Dict[str, str] = {
    "Coke": "Coca-Cola",
    "Sprite Zero": "Sprite",
    "Fries": "French Fries",
    "big drink": "Coca-Cola"
}

type_map: Dict[str, str] = {
    "burger": "burgers",
    "drink": "drinks",
    "combo": "combos",
    "fries": "fries",
    "dessert": "desserts"
}

all_items = (
    menus["virtual_items"]["items"]
    + menus["virtual_items"]["combos"]
    + menus["upsells"]["items"]
)
item_names = {item["name"]: item for item in all_items}
types_with_size = {"drinks", "fries"}

def validate_order(order: OrderResponse) -> dict:
    validated_items: List[Item] = []
    errors: List[str] = []

    for item in order.items:
        name = name_aliases.get(item.name.strip().lower().capitalize(), item.name)
        raw_type = item.type
        type_ = type_map.get(raw_type, raw_type)
        size = item.size

        if name not in item_names:
            errors.append(f"Unknown item: {name}")
            continue

        expected_type = item_names[name].get("category")
        if expected_type != type_:
            errors.append(f"Incorrect type for item '{name}': expected '{expected_type}', got '{type_}'")

        if expected_type in types_with_size:
            if not size:
                errors.append(f"Missing size for {type_} '{name}'")

        price = get_price(name)
        validated_items.append(Item(name=name, type=item.type, size=size, price=price))

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "items": validated_items,
        "intents": order.intents
    }
