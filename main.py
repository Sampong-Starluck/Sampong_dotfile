import sys
from typing import Any, Dict, List
from python.apps import load_apps
from python.shells import load_shells, configure_shell
from python.winget import install_winget, install_apps
from python.ui import checkbox_menu


def show_help():
    print("Usage: python main.py [--online]")
    print("")
    print("Options:")
    print("  --online    Fetch configs from GitHub instead of local json/ folder")
    print("  --help      Show this help message")
    print("")
    print("Default: Uses local json/apps.json and json/shells.json")


def show_menu():
    mode = "ONLINE" if "--online" in sys.argv else "LOCAL"
    print("="*50)
    print(f"    DEV ENVIRONMENT SETUP MENU ({mode})")
    print("="*50)
    print("1) Install winget (if missing)")
    print("2) Install applications")
    print("3) Configure shells")
    print("4) Run ALL steps")
    print("0) Exit")


def get_valid_shells(shells_data: Any) -> List[Dict[str, Any]]:
    """Validate and return shell configurations."""
    if not shells_data:
        print("No shell data received")
        return []
        
    # Handle string error messages
    if isinstance(shells_data, str):
        print(f"Error loading shells: {shells_data}")
        return []
        
    # Convert dictionary to list if needed
    if isinstance(shells_data, dict):
        if "shells" in shells_data:
            shells_data = shells_data["shells"]
            # Add version info if available
            if "version" in shells_data:
                print(f"Shell configurations version: {shells_data['version']}")
        else:
            print("Invalid shell configuration format - missing 'shells' key")
            return []
            
    # Handle non-list data
    if not isinstance(shells_data, list):
        print(f"Invalid shells data format: {type(shells_data)}")
        return []
        
    # Validate each shell entry
    valid_shells = []
    for shell in shells_data:
        if not isinstance(shell, dict):
            print(f"Invalid shell entry format: {shell}")
            continue
            
        # Check required fields
        required_fields = ['id', 'name', 'function']
        if all(key in shell for key in required_fields):
            # Sort by order if available, otherwise append
            if 'order' in shell:
                shell['_sort_key'] = shell['order']
            else:
                shell['_sort_key'] = 999
            valid_shells.append(shell)
        else:
            missing = [f for f in required_fields if f not in shell]
            print(f"Missing required fields in shell: {missing}")
            
    # Sort shells by order
    return sorted(valid_shells, key=lambda x: x['_sort_key'])


def load_and_filter_shells(online_mode: bool = False) -> List[Dict[str, Any]]:
    """Load, validate and filter shells."""
    try:
        # Load shells with online/offline mode
        raw_shells = load_shells(online_mode=online_mode)
        
        # Validate shell configurations
        valid_shells = get_valid_shells(raw_shells)
        
        # Filter visible shells and remove sort key
        visible_shells = []
        for shell in valid_shells:
            if not shell.get("hidden", False):
                del shell['_sort_key']
                visible_shells.append(shell)
        
        return visible_shells
        
    except Exception as e:
        print(f"Error loading shells: {str(e)}")
        return []


def display_shell_info(shell: Dict[str, Any]) -> None:
    """Display detailed shell information."""
    print(f"\n{shell['name']} ({shell['id']})")
    if 'description' in shell:
        print(f"Description: {shell['description']}")
    if 'requires' in shell:
        print(f"Requirements: {', '.join(shell['requires'])}")


def main():
    # Get online mode flag once
    online_mode = "--online" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        return

    done = False
    while not done:
        try:
            show_menu()
            opt = input("Select an option: ").strip()

            if opt == "1":
                install_winget()

            elif opt == "2":
                # apps = load_apps(online_mode=online_mode)
                apps = load_apps()
                selected = checkbox_menu(apps, "Select apps to install")
                if selected:
                    install_apps(selected)
                else:
                    print("No apps selected.")

            elif opt == "3":
                visible_shells = load_and_filter_shells(online_mode=online_mode)
                if not visible_shells:
                    print("No valid shell configurations found!")
                    continue
                
                print("\nAvailable shells:")
                for shell in visible_shells:
                    display_shell_info(shell)
                
                sel = input("\nEnter shell id to configure (or 'all'/'back'): ").strip().lower()
                if sel == "all":
                    for shell in visible_shells:
                        if shell['id'] != "all":  # Skip the "all" meta-entry
                            configure_shell(shell["id"])
                elif sel != "back":
                    if any(s["id"] == sel for s in visible_shells):
                        configure_shell(sel)
                    else:
                        print(f"Invalid shell ID: {sel}")

            elif opt == "4":
                print("\n=== Running all steps ===")
                
                print("\n1. Installing winget...")
                if install_winget():
                    print("\n2. Installing apps...")
#                     apps = load_apps(online_mode=online_mode)
                    apps = load_apps()
                    if apps:
                        install_apps([a for a in apps if not a.get("is_section_toggle")])
                
                print("\n3. Configuring shells...")
                visible_shells = load_and_filter_shells(online_mode=online_mode)
                if visible_shells:
                    for shell in visible_shells:
                        if shell['id'] != "all":  # Skip the "all" meta-entry
                            configure_shell(shell["id"])
                print("\n=== All steps completed ===")

            elif opt == "0":
                print("Goodbye!")
                done = True

            else:
                print("Invalid choice. Try again!")

            if not done:
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            continue
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or check the logs")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)