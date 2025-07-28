from backend.menu.loader import load_menus
from typing import Dict

menus = load_menus()

PRICE_MAP: Dict[str, float] = {}

for item in menus["virtual_items"]["items"]:
    PRICE_MAP[item["name"]] = item.get("price", 0.0)

for combo in menus["virtual_items"]["combos"]:
    PRICE_MAP[combo["name"]] = combo.get("price", 0.0)

for upsell in menus["upsells"]["items"]:
    PRICE_MAP[upsell["name"]] = upsell.get("price", 0.0)


def get_price(item_or_name) -> float:
    name = item_or_name.name if hasattr(item_or_name, "name") else item_or_name
    return round(PRICE_MAP.get(name, 0.0), 2)
