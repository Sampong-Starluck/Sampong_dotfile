import sys

def _checkbox_menu_simple(items, prompt="Select items"):
    """Simple text-based menu for selecting multiple items (works everywhere)."""
    print("\n" + "=" * 50)
    print(prompt)
    print("=" * 50)

    current_section = None
    item_map = {}
    counter = 1

    for item in items:
        if item["section"] != current_section:
            current_section = item["section"]
            print(f"\n=== {current_section} ===")

        print(f"{counter:2d}. {item['name']}")
        item_map[counter] = item
        counter += 1

    print(f"\n{counter:2d}. ** SELECT ALL **")
    print(f"{counter+1:2d}. ** DONE **")

    selected_items = []

    while True:
        choice = input(f"\nEnter number (1-{counter+1}) or 'done': ").strip().lower()

        if choice in ["done", "d", str(counter+1)]:
            break
        elif choice == str(counter):
            selected_items = [item for item in items if not item.get("is_section_toggle")]
            print(f"Selected all {len(selected_items)} items!")
        else:
            try:
                num = int(choice)
                if 1 <= num <= counter - 1:
                    item = item_map[num]
                    if item in selected_items:
                        selected_items.remove(item)
                        print(f"Removed: {item['name']}")
                    else:
                        selected_items.append(item)
                        print(f"Added: {item['name']}")
                else:
                    print("Invalid number!")
            except ValueError:
                print("Please enter a valid number or 'done'")

    return [item for item in selected_items if not item.get("is_section_toggle")]


def _checkbox_menu_inquirer(items, prompt="Select items"):
    """Fancy interactive checkbox menu using InquirerPy (requires real console)."""
    from InquirerPy import inquirer

    choices = []
    current_section = None
    for item in items:
        if item["section"] != current_section:
            current_section = item["section"]
            choices.append({"name": f"=== {current_section} ===", "value": None, "disabled": ""})
        choices.append({"name": item["name"], "value": item})

    result = inquirer.checkbox(
        message=prompt,
        choices=choices,
        instruction="(Use space to select, enter to confirm)",
    ).execute()

    return [r for r in result if r is not None and not r.get("is_section_toggle")]


def checkbox_menu(items, prompt="Select items"):
    """Auto-detect environment: use InquirerPy if real console, else fallback."""
    try:
        # Detect if running in a real terminal
        if sys.stdin.isatty() and sys.stdout.isatty():
            return _checkbox_menu_inquirer(items, prompt)
        else:
            print("[WARN] No real console detected, using simple menu fallback")
            return _checkbox_menu_simple(items, prompt)
    except Exception as e:
        print(f"[WARN] InquirerPy failed ({e}), using simple menu fallback")
        return _checkbox_menu_simple(items, prompt)