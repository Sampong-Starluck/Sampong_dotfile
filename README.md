# Personal Dotfile Repository

This repository is designed to save all my shell configurations, enabling easy restoration after resetting or changing a PC/laptop.

---

## Prerequisites

Before proceeding, ensure you have the following tools installed:

- **Shell Prompt Customization**: [Oh My Posh](https://ohmyposh.dev/)
- **Text Editors**:
   - [Vim](https://www.vim.org/)
   - [Neovim](https://neovim.io/)
   - Notepad
   - [Notepad++](https://notepad-plus-plus.org/)
   - [Visual Studio Code](https://code.visualstudio.com/)
- **Command Prompt Enhancements**: [Clink](https://github.com/chrisant996/clink) (for customizing CMD)
- **Version Management**: [Version-fox (vfox)](https://github.com/version-fox/vfox) (replaces SDKMAN for Java and NVS for Node.js)

---

## Supported Shells

- **PowerShell**: [PowerShell 7](https://learn.microsoft.com/en-us/powershell/scripting/overview?view=powershell-7.4)
- **Command Prompt**: Enhanced with [Clink](https://github.com/chrisant996/clink)
- **Bash**: [Git Bash](https://git-scm.com/), [Cygwin](https://cygwin.com/)
- **Nushell**: [Nushell](https://www.nushell.sh/)

---

## Recommended Terminal Emulators

- [Tabby Terminal](https://tabby.sh/)
- [Windows Terminal](https://github.com/microsoft/terminal)

---

## Installation Guide

### Option 1: Script Installation

Run the provided script to set up your environment.

1. Modify the file paths in `install_app.ps1` to match your system.
2. Execute the script:

    ```shell
    ./install_app.ps1
    ```

⚠ **Warning**: The script may have unintended side effects. Manual installation is recommended for better control.

---

### Option 2: Manual Installation

#### 1. Command Prompt (Clink)

- Install and configure Oh My Posh in Clink as per the [official documentation](https://ohmyposh.dev/docs/installation/prompt).
- Customize using Oh My Posh.

#### 2. PowerShell Configuration

1. Allow execution of scripts:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
   ```

2. Create a PowerShell profile:

   ```powershell
   New-Item $PROFILE.CurrentUserAllHosts -ItemType File -Force
   ```

3. Edit the profile:

   ```powershell
   notepad $PROFILE
   ```

4. Add the following line to the profile file:

   ```powershell
   Import-Module (Resolve-Path '<path-to>/PowerShell/posh_profile.ps1')
   ```

5. Restart the terminal.
---
#### 3. Git Bash Configuration

1. Create a `.bashrc` file:
    ```shell
    vim ~/.bashrc
    ```

2. Add the following:
    ```shell
    export DIR="<path>/bash"
    if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
    . "$DIR/main.sh"
    ```

#### 4. Nushell Configuration

1. Edit the Nu environment file:

   ```nu
   open $nu.env-path | edit
   ```

   Add this line to initialize Oh My Posh on startup:

   ```nu
   oh-my-posh init nu --config "~/AppData/Local/Programs/oh-my-posh/themes/spaceship.omp.json"
   ```

2. Edit the Nu configuration file:

   ```nu
   open $nu.config-path | edit
   ```

   Add the following lines:

   ```nu
   source ~/.oh-my-posh.nu
   let-env EDITOR = "code"
   use ~/Documents/Sampong_dotfile/nu/main_profile.nu
   use main_profile *
   ```

3. Save and restart the shell.

---

## Source

This repository incorporates scripts and ideas from:

- [Chris Titus Tech's GitHub](https://github.com/ChrisTitusTech/powershell-profile)
- [Tim Sneath's GitHub Gist](https://gist.github.com/timsneath/19867b12eee7fd5af2ba)
