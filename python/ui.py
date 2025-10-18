import sys
from typing import List, Dict, Any


def _checkbox_menu_simple(
    items: List[Dict[str, Any]],
    prompt: str = "Select items"
) -> List[Dict[str, Any]]:
    """
    Simple text-based menu for selecting multiple items.
    Works in any terminal environment.
    """
    print("\n" + "=" * 60)
    print(prompt)
    print("=" * 60)

    current_section = None
    item_map = {}
    counter = 1

    # Display items with numbering
    for item in items:
        if item["section"] != current_section:
            current_section = item["section"]
            print(f"\n=== {current_section} ===")

        print(f"{counter:2d}. {item['name']}")
        item_map[counter] = item
        counter += 1

    # Display special options
    select_all_num = counter
    done_num = counter + 1
    print(f"\n{select_all_num:2d}. ** SELECT ALL **")
    print(f"{done_num:2d}. ** DONE **")
    print("=" * 60)

    selected_items = []
    selection_display = {}

    while True:
        # Show current selections
        if selected_items:
            print(f"\n[Current selections: {len(selected_items)} items]")

        try:
            choice = input(
                f"\nEnter number (1-{done_num}) or 'done': "
            ).strip().lower()

            # Handle done/exit
            if choice in ["done", "d", str(done_num)]:
                break

            # Handle select all
            elif choice == str(select_all_num):
                selected_items = [
                    item for item in items
                    if not item.get("is_section_toggle")
                ]
                print(f"✓ Selected all {len(selected_items)} items!")

            # Handle individual selections
            else:
                try:
                    num = int(choice)
                    if 1 <= num < select_all_num:
                        item = item_map[num]
                        if item in selected_items:
                            selected_items.remove(item)
                            print(f"✗ Removed: {item['name']}")
                        else:
                            selected_items.append(item)
                            print(f"✓ Added: {item['name']}")
                    else:
                        print("❌ Invalid number!")
                except ValueError:
                    print("❌ Please enter a valid number or 'done'")

        except KeyboardInterrupt:
            print("\n[CANCELLED]")
            return []

    # Return selections, filter out section toggles
    return [
        item for item in selected_items
        if not item.get("is_section_toggle")
    ]


def _checkbox_menu_inquirer(
    items: List[Dict[str, Any]],
    prompt: str = "Select items"
) -> List[Dict[str, Any]]:
    """
    Fancy interactive checkbox menu using InquirerPy.
    Requires a real terminal with rich support.
    """
    try:
        from InquirerPy import inquirer
    except ImportError:
        print(
            "[WARN] InquirerPy not installed. "
            "Using simple menu instead."
        )
        return _checkbox_menu_simple(items, prompt)

    # Build choices with sections
    choices = []
    current_section = None

    for item in items:
        if item["section"] != current_section:
            current_section = item["section"]
            choices.append({
                "name": f"▼ {current_section}",
                "value": None,
                "disabled": True
            })

        if not item.get("is_section_toggle"):
            choices.append({
                "name": item["name"],
                "value": item
            })

    try:
        result = inquirer.checkbox(
            message=prompt,
            choices=choices,
            instruction="(Use ↑↓ to move, Space to select, Enter to confirm)",
            border=True,
            show_instruction=True,
        ).execute()

        return [r for r in result if r is not None]

    except Exception as e:
        print(f"[WARN] InquirerPy failed: {str(e)}")
        print("[INFO] Falling back to simple menu")
        return _checkbox_menu_simple(items, prompt)


def checkbox_menu(
    items: List[Dict[str, Any]],
    prompt: str = "Select items"
) -> List[Dict[str, Any]]:
    """
    Auto-detect environment and show appropriate menu.

    - Uses InquirerPy if in real terminal
    - Falls back to simple menu for non-interactive environments
    """
    if not items:
        print("[WARN] No items to select")
        return []

    try:
        # Detect if running in a real terminal
        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                return _checkbox_menu_inquirer(items, prompt)
            except Exception:
                print("[INFO] Falling back to simple menu")
                return _checkbox_menu_simple(items, prompt)
        else:
            print("[INFO] No real console detected, using simple menu")
            return _checkbox_menu_simple(items, prompt)

    except Exception as e:
        print(f"[WARN] Menu error: {str(e)}")
        return _checkbox_menu_simple(items, prompt)


def show_banner(mode: str = "GUI"):
    """Display startup banner."""
    print("\n" + "=" * 60)
    print("   🚀 DEV ENVIRONMENT SETUP - " + mode.upper())
    print("=" * 60 + "\n")


def show_section(title: str, fg_color: str = "cyan"):
    """Print section header."""
    print(fg_color)
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def warning(message: str):
    """Print warning message."""
    print(f"⚠️  {message}")


def info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")