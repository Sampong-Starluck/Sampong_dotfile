import sys
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dev Environment Setup Tool",
        epilog="Default: Runs GUI. Use --cli for command-line mode."
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode instead of GUI"
    )
    parser.add_argument(
        "--help-cli",
        action="store_true",
        help="Show CLI-specific help"
    )

    args = parser.parse_args()

    # Show CLI help if requested
    if args.help_cli:
        show_cli_help()
        return

    # Run in CLI mode
    if args.cli:
        run_cli()
    else:
        # Try to run GUI, fallback to CLI if it fails
        try:
            run_gui()
        except Exception as err:
            print(f"[WARN] GUI failed: {str(err)}")
            print("[INFO] Falling back to CLI mode...")
            run_cli()


def run_gui():
    """Launch CustomTkinter GUI."""
    try:
        from python.gui import SetupApp
        import customtkinter as ctk

        app = SetupApp()
        app.mainloop()
    except ImportError as err:
        print(f"[ERROR] CustomTkinter not installed: {str(err)}")
        print("Install with: pip install customtkinter")
        raise


def run_cli():
    """Launch CLI mode (original implementation)."""
    from python.cli import main as cli_main
    cli_main()


def show_cli_help():
    """Show CLI-specific help."""
    print("=" * 60)
    print("    DEV ENVIRONMENT SETUP - CLI MODE")
    print("=" * 60)
    print("\nUsage: python main.py [--cli] [--help-cli]")
    print("\nOptions:")
    print("  --cli           Force CLI mode (no GUI)")
    print("  --help-cli      Show this help message")
    print("  -h, --help      Show general help")
    print("\nDefault Behavior:")
    print("  - Runs GUI if available")
    print("  - Falls back to CLI if GUI fails")
    print("\nExamples:")
    print("  python main.py              # Run GUI (default)")
    print("  python main.py --cli        # Force CLI mode")
    print("\nFeatures:")
    print("  ✓ Interactive menu system")
    print("  ✓ App selection with checkboxes")
    print("  ✓ Shell configuration")
    print("  ✓ One-click setup for all steps")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] {str(e)}")
        sys.exit(1)