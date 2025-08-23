# config.py
import os
import sys
import requests
import json

# -------------------------------------------------------------------
# Base directory = project root (where main.py is located)
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Local JSON paths
APPS_JSON_LOCAL = os.path.join(BASE_DIR, "json", "apps.json")
SHELLS_JSON_LOCAL = os.path.join(BASE_DIR, "json", "shells.json")

# GitHub username and repo
USERNAME = "Sampong-Starluck"
REPOSITORY = "Sampong_dotfile"

# Remote GitHub URLs
GITHUB_BASE = f"https://raw.githubusercontent.com/{USERNAME}/{REPOSITORY}/master/json"
APPS_JSON_URL = f"{GITHUB_BASE}/apps.json"
SHELLS_JSON_URL = f"{GITHUB_BASE}/shells.json"

# Remote shell profile URLs
NU_PROFILE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPOSITORY}/master/dotfiles/nu/main_profile.nu"
BASH_PROFILE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPOSITORY}/master/dotfiles/bash/main.sh"
POSH_PROFILE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPOSITORY}/master/dotfiles/PowerShell/posh_profile.ps1"

# Dotfile root in AppData
DOTFILE_ROOT = os.path.join(os.getenv("APPDATA"), "Sampong_dotfile")

# Flags
ONLINE_MODE = "--online" in sys.argv
FORCE_LOCAL = "--force-local" in sys.argv
RESET_PROFILES = "--reset-profiles" in sys.argv


def fetch_text(url, local_fallback=None):
    """Fetch text from GitHub if --online, else fallback to local file."""
    if ONLINE_MODE and not FORCE_LOCAL:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            print(f"[DEBUG] Loaded text from GitHub: {url}")
            return resp.text
        except Exception as e:
            print(f"[WARN] GitHub fetch failed ({e}), falling back to local")

    if local_fallback and os.path.exists(local_fallback):
        with open(local_fallback, "r", encoding="utf-8") as f:
            print(f"[DEBUG] Loaded text from local: {local_fallback}")
            return f.read()
    return None


def fetch_json(url, local_path):
    """Fetch JSON from GitHub if --online, else fallback to local file."""
    if ONLINE_MODE and not FORCE_LOCAL:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            print(f"[DEBUG] Loaded JSON from GitHub: {url}")
            return resp.json()
        except Exception as e:
            print(f"[WARN] GitHub fetch failed ({e}), falling back to local")

    # Always fallback to local
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            print(f"[DEBUG] Loaded JSON from local: {local_path}")
            return json.load(f)
    else:
        raise FileNotFoundError(f"Local file not found: {local_path}")