import sys
from pathlib import Path
from src.backend.llm.order_parser import parser_order
from src.backend.logic.order_validator import validate_order
from src.backend.logic.order_engine import process_order_logic

SRC = Path(__file__).parent / "src"
sys.path.append(str(SRC))

def main():
    print("\U0001F354 Welcome to McDonald's! What can I get you started with?")
    full_order = {
        "items": [],
        "intents": [],
        "errors": [],
        "is_valid": True,
    }

    upsell_flags = {
        "combo_offered": False,
        "sauce_offered": False,
        "dessert_offered": False,
        "drink_requested": False,
    }

    while True:
        user_input = input("\U0001F9D1 You: ").strip()
        if not user_input:
            continue

        try:
            parsed = parser_order(user_input)
        except Exception as e:
            print(f"⚠️ Failed to parse message: {e}")
            continue

        validated = validate_order(parsed)
        logic = process_order_logic(validated, upsell_flags)

        if logic["state"] == "error":
            print(f"\U0001F916 System: {logic['system_message']}")
            continue

        full_order["items"].extend(logic["items"])
        full_order["intents"].extend(logic.get("intents", []))

        # Оновити прапори після дій
        for action in logic.get("actions", []):
            if action == "offer_combo":
                upsell_flags["combo_offered"] = True
            elif action == "offer_sauce":
                upsell_flags["sauce_offered"] = True
            elif action == "offer_dessert":
                upsell_flags["dessert_offered"] = True
            elif action == "request_drink_for_combo":
                upsell_flags["drink_requested"] = True

        print(f"\U0001F916 System: {logic['system_message']}")

        if logic["state"] == "complete":
            print("\n\U0001F9FE Your order summary:")
            for item in full_order["items"]:
                size = f" ({item.size})" if getattr(item, "size", None) else ""
                print(f" - {item.name}{size}")

            total_price = sum(item.price or 0.0 for item in full_order["items"])
            print(f"\n\U0001F4B0 Total price: ${total_price:.2f}")
            print("✅ Thank you for your order!\n")
            break

if __name__ == "__main__":
    main()
