# Sampong_dotfile: Windows Dev Environment Setup

This repository provides an **interactive PowerShell script** to help you quickly set up a Windows development environment. It works with standard Windows PowerShell and PowerShell 7+, and lets you install essential applications, configure popular shells, and manage your dotfiles—all from a single menu.

## Features

- **Install winget** (if missing)
- **Select and install apps** from a customizable `apps.json` catalog
- **Configure shells** (PowerShell, Bash, NuShell) with your custom dotfiles
- **All-in-one option** to run every step automatically
- **Interactive menus** for easy selection

## Prerequisites

- **Windows PowerShell** (works with both Windows PowerShell 5.1 and PowerShell 7+)
- Internet connection for downloads

## Usage

1. **Clone this repository**  
   ```powershell
   git clone https://github.com/yourusername/Sampong_dotfile.git
   cd Sampong_dotfile
   ```

2. **Run the installer**  
   ```powershell
   .\install.ps1
   ```

3. **Follow the interactive prompts**  
   - Install winget if needed  
   - Select apps to install  
   - Choose which shells to configure

## Customization

- **apps.json**: Edit `json/apps.json` to add or remove applications.
- **shells.json**: Edit `json/shells.json` to control which shells are available for configuration.
- **Dotfiles**: Place your custom shell configs in the `Sampong_dotfile` subfolders (e.g., `PowerShell/`, `bash/`, `nu/`).

## What Gets Configured

- **PowerShell**: Adds imports and customizations to your `$PROFILE`
- **Bash**: Sources your custom `main.sh` from `.bashrc`
- **NuShell**: Sets up config and env files, applies Oh-My-Posh theme if available

## Notes

- The script does **not** install PowerShell modules by default, but you can enable this in the code.
- All changes are made to your user profile directories (safe for multi-user systems).
- You can always re-run the script to update or reconfigure.

---

**Questions or issues?**  
Open an issue or

