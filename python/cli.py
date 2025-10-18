"""
CLI mode for Dev Environment Setup.
This is the original command-line interface with improved checkbox UI.
"""

import sys
import os
from typing import Any, Dict, List

import python.config as config
from python.apps import load_apps
from python.shells import configure_shell, load_shells
from python.winget import install_apps, install_winget
from python.check_network import internet_on


def check_internet_on() -> bool:
    """Check if internet is available."""
    return internet_on(url=config.APPS_JSON_URL)


def show_menu(online_mode: bool = False):
    """Display main menu."""
    mode = "🌐 ONLINE" if online_mode else "💾 LOCAL"
    print("\n" + "=" * 70)
    print(f"       DEV ENVIRONMENT SETUP MENU ({mode})")
    print("=" * 70)
    print("1) 🔧 Install winget (if missing)")
    print("2) 📥 Install applications")
    print("3) 🐚 Configure shells")
    print("4) ⚡ Run ALL steps")
    print("0) ❌ Exit")
    print("=" * 70 + "\n")


def get_valid_shells(shells_data: Any) -> List[Dict[str, Any]]:
    """Validate and return shell configurations."""
    if not shells_data:
        print("[WARN] No shell data received")
        return []

    if isinstance(shells_data, str):
        print(f"[ERROR] {shells_data}")
        return []

    if isinstance(shells_data, dict):
        if "shells" in shells_data:
            shells_data = shells_data["shells"]
        else:
            print("[ERROR] Invalid shell format - missing 'shells' key")
            return []

    if not isinstance(shells_data, list):
        print(f"[ERROR] Invalid shells data: {type(shells_data)}")
        return []

    valid_shells = []
    for shell in shells_data:
        if not isinstance(shell, dict):
            continue

        required_fields = ["id", "name", "function"]
        if all(key in shell for key in required_fields):
            shell["_sort_key"] = shell.get("order", 999)
            valid_shells.append(shell)

    return sorted(valid_shells, key=lambda x: x["_sort_key"])


def load_and_filter_shells(
    online_mode: bool = False
) -> List[Dict[str, Any]]:
    """Load, validate and filter shells."""
    try:
        raw_shells = load_shells(online_mode=online_mode)
        valid_shells = get_valid_shells(raw_shells)

        visible_shells = []
        for shell in valid_shells:
            if not shell.get("hidden", False):
                del shell["_sort_key"]
                visible_shells.append(shell)

        return visible_shells

    except Exception as e:
        print(f"[ERROR] Failed to load shells: {str(e)}")
        return []


def get_single_key():
    """
    Get a single key press with proper arrow key support.
    Works on Windows and Unix-like systems.
    """
    if sys.platform == "win32":
        import msvcrt

        key = msvcrt.getch()

        # Handle special keys on Windows
        if key == b'\xe0':  # Windows special key prefix
            special = msvcrt.getch()
            if special == b'H':  # Up arrow
                return 'UP'
            elif special == b'P':  # Down arrow
                return 'DOWN'
            elif special == b'M':  # Right arrow
                return 'RIGHT'
            elif special == b'K':  # Left arrow
                return 'LEFT'

        # Regular keys
        if key == b'\r':  # Enter
            return 'ENTER'
        elif key == b' ':  # Space
            return 'SPACE'
        elif key == b'q' or key == b'Q':  # Q
            return 'QUIT'
        elif key == b'\x1b':  # Escape
            return 'ESC'

        return key.decode('utf-8', errors='ignore')

    else:  # Unix/Linux/macOS
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)

            # Read first byte
            ch = sys.stdin.read(1)

            if ch == '\x1b':  # Escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)

                    if ch3 == 'A':
                        return 'UP'
                    elif ch3 == 'B':
                        return 'DOWN'
                    elif ch3 == 'C':
                        return 'RIGHT'
                    elif ch3 == 'D':
                        return 'LEFT'

            elif ch == '\r' or ch == '\n':
                return 'ENTER'
            elif ch == ' ':
                return 'SPACE'
            elif ch.lower() == 'q':
                return 'QUIT'
            elif ch == '\x1b':
                return 'ESC'

            return ch

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def interactive_checkbox(
    items: List[Dict[str, Any]],
    prompt: str = "Select items"
) -> List[Dict[str, Any]]:
    """
    Interactive checkbox menu with arrow keys and space to select.

    Controls:
    - ↑/↓ : Move cursor up/down
    - SPACE : Select/deselect item
    - ENTER : Confirm selection
    - Q/ESC : Cancel
    """
    if not items:
        print("[WARN] No items to select")
        return []

    # Filter out section toggles
    selectable_items = [
        item for item in items
        if not item.get("is_section_toggle")
    ]

    if not selectable_items:
        print("[WARN] No selectable items")
        return []

    # State
    selected = [False] * len(selectable_items)
    current_pos = 0
    done = False

    # Display first time
    _display_checkbox_menu(
        selectable_items, current_pos, selected, prompt
    )

    # Main loop
    while not done:
        try:
            key = get_single_key()

            if key is None:
                continue

            elif key == 'UP':
                current_pos = (current_pos - 1) % len(selectable_items)
                _display_checkbox_menu(
                    selectable_items, current_pos, selected, prompt
                )

            elif key == 'DOWN':
                current_pos = (current_pos + 1) % len(selectable_items)
                _display_checkbox_menu(
                    selectable_items, current_pos, selected, prompt
                )

            elif key == 'SPACE':
                selected[current_pos] = not selected[current_pos]
                _display_checkbox_menu(
                    selectable_items, current_pos, selected, prompt
                )

            elif key == 'ENTER':
                done = True

            elif key == 'QUIT' or key == 'ESC':
                print("\n[INFO] Cancelled by user")
                return []

        except KeyboardInterrupt:
            print("\n[INFO] Cancelled by user")
            return []
        except Exception as e:
            print(f"[DEBUG] Error: {str(e)}")
            continue

    # Return selected items
    result = [
        item for i, item in enumerate(selectable_items)
        if selected[i]
    ]
    return result


def _display_checkbox_menu(
    items: List[Dict[str, Any]],
    current_pos: int,
    selected: List[bool],
    prompt: str
):
    """Display the interactive checkbox menu."""
    # Clear screen
    os.system('cls' if sys.platform == "win32" else 'clear')

    print("\n" + "=" * 70)
    print(prompt)
    print("=" * 70)
    print("↑ ↓ = Navigate  |  SPACE = Select  |  ENTER = Confirm  |  Q = Cancel")
    print("=" * 70 + "\n")

    current_section = None
    for i, item in enumerate(items):
        # Print section header if new
        if item.get("section") and item["section"] != current_section:
            current_section = item["section"]
            print(f"\n▼ {current_section}")
            print("-" * 70)

        # Determine symbols
        cursor = " → " if i == current_pos else "   "
        checkbox = "[*]" if selected[i] else "[]"

        # Print item
        print(f"{cursor}{checkbox} {item['name']}")

    print("\n" + "=" * 70)
    total_selected = sum(selected)
    print(f"Selected: {total_selected}/{len(items)} items")
    print("=" * 70)


def _checkbox_menu_simple(
    items: List[Dict[str, Any]],
    prompt: str = "Select items"
) -> List[Dict[str, Any]]:
    """
    Simple text-based menu for selecting multiple items.
    Fallback when interactive mode is not available.
    """
    print("\n" + "=" * 70)
    print(prompt)
    print("=" * 70)

    current_section = None
    item_map = {}
    counter = 1

    for item in items:
        if item.get("section") != current_section:
            current_section = item.get("section")
            print(f"\n▼ {current_section}")
            print("-" * 70)

        print(f"{counter:2d}. {item['name']}")
        item_map[counter] = item
        counter += 1

    select_all_num = counter
    done_num = counter + 1
    print(f"\n{select_all_num:2d}. ** SELECT ALL **")
    print(f"{done_num:2d}. ** DONE **")
    print("=" * 70)

    selected_items = []

    while True:
        try:
            num_selected = len(selected_items)
            choice = input(
                f"\n[{num_selected} selected] Enter number (1-{done_num}): "
            ).strip().lower()

            if choice in ["done", "d", str(done_num)]:
                break

            elif choice == str(select_all_num):
                selected_items = list(item_map.values())
                print(f"✓ Selected all {len(selected_items)} items!")

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
                    print("❌ Please enter a valid number")

        except KeyboardInterrupt:
            print("\n[INFO] Cancelled by user")
            return []

    return selected_items


def display_shell_info(shell: Dict[str, Any]) -> None:
    """Display detailed shell information."""
    print(f"\n  {shell['name']} ({shell['id']})")
    if "description" in shell:
        print(f"    Description: {shell['description']}")
    if "requires" in shell:
        print(f"    Requires: {', '.join(shell['requires'])}")


def main():
    """Main CLI loop."""
    print("\n" + "=" * 70)
    print("   🚀 DEV ENVIRONMENT SETUP - CLI MODE")
    print("=" * 70)

    online_mode = check_internet_on()

    done = False
    while not done:
        try:
            show_menu(online_mode)
            opt = input("Select an option (0-4): ").strip()

            if opt == "1":
                print("\n" + "=" * 70)
                print("   🔧 Installing winget")
                print("=" * 70 + "\n")
                install_winget()

            elif opt == "2":
                mode = "ONLINE" if online_mode else "LOCAL"
                print("\n" + "=" * 70)
                print(f"   📦 Select Applications to Install ({mode}))")
                print("=" * 70 + "\n")
                apps = load_apps(online_mode)
                selected = interactive_checkbox(
                    apps,
                    "Select applications to install"
                )
                if selected:
                    print("\n" + "=" * 70)
                    print("   📥 Installing Applications")
                    print("=" * 70 + "\n")
                    install_apps(selected)
                    print("\n✅ Installation complete!")
                else:
                    print("\n[INFO] No apps selected.")

            elif opt == "3":
                mode = "ONLINE" if online_mode else "LOCAL"
                print("\n" + "=" * 70)
                print(f"   🐚 Configure Shells ({mode}))")
                print("=" * 70 + "\n")
                visible_shells = load_and_filter_shells(
                    online_mode=online_mode
                )
                if not visible_shells:
                    print("[ERROR] No shell configurations found!")
                    continue

                selected = interactive_checkbox(
                    visible_shells,
                    "Select shells to configure"
                )

                if selected:
                    print("\n" + "=" * 70)
                    print("   ⚙️ Configuring Shells")
                    print("=" * 70 + "\n")
                    for shell in selected:
                        if shell["id"] != "all":
                            print(f"Configuring {shell['name']}...")
                            configure_shell(shell["id"])
                    print("\n✅ Shell configuration complete!")
                else:
                    print("\n[INFO] No shells selected.")

            elif opt == "4":
                print("\n" + "=" * 70)
                print("   ⚡ Running All Setup Steps")
                print("=" * 70 + "\n")

                print("[1/3] Installing winget...")
                if install_winget():
                    print("\n[2/3] Installing applications...")
                    apps = load_apps()
                    install_apps(
                        [a for a in apps
                         if not a.get("is_section_toggle")]
                    )

                print("\n[3/3] Configuring shells...")
                visible_shells = load_and_filter_shells(
                    online_mode=online_mode
                )
                if visible_shells:
                    for shell in visible_shells:
                        if shell["id"] != "all":
                            configure_shell(shell["id"])

                print("\n" + "=" * 70)
                print("   ✅ All steps completed!")
                print("=" * 70 + "\n")

            elif opt == "0":
                print("Goodbye! 👋\n")
                done = True

            else:
                print("❌ Invalid choice. Try again!")

            if not done:
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n[INFO] Operation cancelled by user")
            continue
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            print("[INFO] Please try again")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] {str(e)}")
        sys.exit(1)