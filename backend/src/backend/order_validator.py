from backend.menu.loader import load_menus

menus = load_menus()

name_aliases = {
    "Coke": "Coca-Cola",
    "Sprite Zero": "Sprite",
    "Fries": "French Fries",
}

type_map = {
    "burger": "burgers",
    "drink": "drinks",
    "combo": "combos",
    "fries": "fries",
    "dessert": "desserts"
}

all_items = menus["virtual_items"]["items"] + menus["virtual_items"]["combos"] + menus["upsells"]["items"]
item_names = {item["name"]: item for item in all_items}

types_with_size = {"drink", "fries"}

def validate_order(order: dict) -> dict:
    validated_items = []
    errors = []

    for item in order.get("items", []):
        name = item.get("name")
        type_ = item.get("type")
        size = item.get("size")

        name = name_aliases.get(name, name)
        type_ = type_map.get(type_, type_)

        if name not in item_names:
            errors.append(f"Unknown item: {name}")
            continue

        if item_names[name].get("category") != type_:
            errors.append(f"Incorrect type for item '{name}': expected '{item_names[name].get('category')}', got '{type_}'")

        if type_ in types_with_size:
            if not size:
                errors.append(f"Missing size for {type_} '{name}'")

        validated_items.append(item)

    result = {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "items": validated_items,
        "intents": order.get("intents", [])
    }

    return result
