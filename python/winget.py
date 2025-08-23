import subprocess
import shutil


def is_winget_installed():
    return shutil.which("winget") is not None


def install_winget():
    if is_winget_installed():
        print("[OK] winget already installed.")
        return True

    print("[*] Installing winget...")
    url = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    print(f"Please download and install manually: {url}")
    return False


def install_apps(apps):
    total = len(apps)
    if total == 0:
        return

    print(f"[*] Installing {total} application(s)...")
    for i, app in enumerate(apps, start=1):
        percent = int((i / total) * 100)
        print(f"-> [{app['section']}] {app['name']} ({percent}%)")

        if app.get("is_section_toggle"):
            continue  # skip section toggles

        try:
            subprocess.run(
                [
                    "winget",
                    "install",
                    "-e",
                    "--id",
                    app["id"],
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ],
                check=True,
            )
            print("   [OK]")
        except subprocess.CalledProcessError:
            print("   [FAILED]")