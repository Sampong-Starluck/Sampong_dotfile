from .config import (
    SHELLS_JSON_LOCAL,
    SHELLS_JSON_URL,
    fetch_json,
    DOTFILE_ROOT,
    RESET_PROFILES,
)
import os
import platform
import shutil
from datetime import datetime


def ensure_dir(path: str) -> None:
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def load_shells(online_mode=False):
    """Load shells.json from GitHub or local based on mode."""
    if online_mode:
        try:
            return fetch_json(SHELLS_JSON_URL, SHELLS_JSON_LOCAL, online_mode)
        except Exception as e:
            print(f"[WARN] Failed to fetch online config: {e}")
            print("[INFO] Falling back to local config")
            return fetch_json(SHELLS_JSON_LOCAL, SHELLS_JSON_LOCAL)
    return fetch_json(SHELLS_JSON_LOCAL, SHELLS_JSON_LOCAL)


def backup_profile(path: str) -> str | None:
    """Create timestamped backup of profile file."""
    if os.path.exists(path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.{timestamp}.bak"
        shutil.copy2(path, backup_path)
        print(f"[BACKUP] {path} → {backup_path}")
        return backup_path
    return None


def reset_profile(path: str, initial_content: str = "") -> None:
    """Backup existing profile and create new empty one."""
    backup_profile(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(initial_content)
    print(f"[RESET] Created new profile at {path}")


# ---------------- NuShell ---------------- #
def configure_nushell():
    print("[*] Configuring NuShell...")

    # 1) Create and reset main profile
    nu_dir = os.path.join(DOTFILE_ROOT, "nu")
    ensure_dir(nu_dir)
    main_profile = os.path.join(nu_dir, "main_profile.nu")
    with open("./dotfiles/nu/main_profile.nu", "r", encoding="utf-8") as f:
        content = f.read()
    reset_profile(main_profile, content)

    # 2) Reset nushell config files
    nu_cfg = os.path.join(os.getenv("APPDATA"), "nushell")
    ensure_dir(nu_cfg)
    # env_nu = os.path.join(nu_cfg, "env.nu")
    conf_nu = os.path.join(nu_cfg, "config.nu")

    # reset_profile(env_nu, "# NuShell environment config\n")
    reset_profile(conf_nu, "# NuShell main config\n")

    # 3) Apply Oh-My-Posh theme if found
    theme_paths = [
        os.path.join(
            os.getenv("LOCALAPPDATA"),
            "Programs",
            "oh-my-posh",
            "themes",
            "spaceship.omp.json",
        ),
        os.path.join(
            os.getenv("PROGRAMFILES"), "oh-my-posh", "themes", "spaceship.omp.json"
        ),
    ]
    # theme = next((p for p in theme_paths if p and os.path.exists(p)), None)
    entries = [f"use {main_profile.replace('\\', '/')}", 'load_theme "z ash.omp.json"']

    # with open(env_nu, "a", encoding="utf-8") as f:
    #     f.write("$env.config.show_banner = false\n")
    #     for entry in entries:
    #         f.write(f"{entry}\n")
    #
    # print("[OK] Applied Oh-My-Posh to NuShell")

    # 4) Source custom profile
    include = f"use {main_profile.replace('\\', '/')}"

    with open(conf_nu, "a", encoding="utf-8") as f:
        f.write(f"\n{include} * \n")
        # f.write("main_profile startup\n")
        f.write('load_theme "zash.omp.json" \n')
        f.write('$env.config.show_banner = false \n')
        print(f"[OK] Linked NuShell profile in {conf_nu}")


# ---------------- Bash ---------------- #
def configure_bash():
    print("[*] Configuring Bash...")

    # 1) Create and reset main script
    bash_dir = os.path.join(DOTFILE_ROOT, "bash")
    ensure_dir(bash_dir)
    main_sh = os.path.join(bash_dir, "main.sh")
    with open("./dotfiles/bash/main.sh", "r", encoding="utf-8") as f:
        content = f.read()
    reset_profile(main_sh, content)

    # 2) Reset .bashrc
    bashrc = os.path.expanduser("~/.bashrc")
    reset_profile(bashrc, "# Bash configuration\n")

    # 3) Add source line
    source_line = f'source "{main_sh}"'
    with open(bashrc, "a", encoding="utf-8") as f:
        f.write(f"\n# Source Sampong bash customizations\n{source_line}\n")
        print(f"[OK] Updated .bashrc → {bashrc}")


# ---------------- PowerShell ---------------- #
def configure_posh():
    print("[*] Configuring PowerShell...")

    # 1) Create and reset main profile
    posh_dir = os.path.join(DOTFILE_ROOT, "PowerShell")
    ensure_dir(posh_dir)
    profile = os.path.join(posh_dir, "posh_profile.ps1")
    with open("./dotfiles/PowerShell/posh_profile.ps1", "r", encoding="utf-8") as f:
        content = f.read()
    reset_profile(profile, content)

    # 2) Reset PowerShell profile
    if platform.system() == "Windows":
        profile_path = os.path.expandvars(
            r"%USERPROFILE%\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
        )
    else:
        profile_path = os.path.expanduser(
            "~/.config/powershell/Microsoft.PowerShell_profile.ps1"
        )

    ensure_dir(os.path.dirname(profile_path))
    reset_profile(profile_path, "# PowerShell main configuration\n")

    # 3) Add required entries
    entries = [
        f'Import-Module (Resolve-Path "{profile}")',
        "Import-Module -Name Microsoft.WinGet.CommandNotFound",
        'Invoke-Expression "$(vfox activate pwsh)"',
    ]

    with open(profile_path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry}\n")
        print(f"[OK] Added to PowerShell profile → {profile_path}")


# ---------------- Dispatcher ---------------- #
def configure_shell(shell_id: str):
    """Configure shell based on shell_id from shells.json."""
    print(f"[*] Configuring shell: {shell_id}")

    # Skip the "all" meta-entry
    if shell_id == "all":
        print("[SKIP] 'all' is a meta-entry, not a shell")
        return

    # Map shell IDs to configuration functions
    shell_configs = {
        "powershell": configure_posh,
        "nushell": configure_nushell,
        "bash": configure_bash,
        # "fish": configure_fish  # Uncomment when implementing fish shell
    }

    # Get and call the appropriate configuration function
    config_func = shell_configs.get(shell_id.lower())
    if config_func:
        try:
            config_func()
            print(f"[OK] Successfully configured {shell_id}")
        except Exception as e:
            print(f"[ERROR] Failed to configure {shell_id}: {str(e)}")
    else:
        print(f"[WARN] No configuration available for shell: {shell_id}")
