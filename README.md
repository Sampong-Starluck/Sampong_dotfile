# Personal Dotfiles Repository

Easily restore your preferred shell environments and configurations after resetting or changing your PC or laptop.

---

## Prerequisites

Before using these dotfiles, please install:

### Shell Prompt & Enhancements
- [Oh My Posh](https://ohmyposh.dev) — beautiful, customizable shell prompts
- [Clink](https://github.com/chrisant996/clink) — enhances Windows CMD

### Text Editors
- [Vim](https://www.vim.org/)
- [Neovim](https://neovim.io/)
- Notepad (basic editing for installation scripts)
- [Notepad++](https://notepad-plus-plus.org/)
- [Visual Studio Code](https://code.visualstudio.com/)

### Command Prompt Enhancements
- [Clink](https://github.com/chrisant996/clink) (for customizing CMD)

### Version Management
- [Version-fox (vfox)](https://github.com/version-fox/vfox)  
  *(A unified tool for managing SDKs (Java, Node.js, etc.)*

---

## Supported Shells

- **PowerShell**: [PowerShell 7](https://learn.microsoft.com/en-us/powershell/scripting/overview?view=powershell-7.4)
- **Command Prompt**: Enhanced with [Clink](https://github.com/chrisant996/clink)
- **Bash**: [Git Bash](https://git-scm.com/), [Cygwin](https://cygwin.com/)
- **NuShell**: [NuShell](https://www.nushell.sh/)

---

## Recommended Terminal Emulators

- [Tabby Terminal](https://tabby.sh/)
- [Windows Terminal](https://github.com/microsoft/terminal)

---

## Installation

### Option 1: Invoke web request:

```powershell
irm https://raw.githubusercontent.com/Sampong-Starluck/Sampong_dotfile/master/install_app.ps1 | invoke-expression 
```
**Note**: This method is not working currently. Recommence Method 2 & 3

---

### Option 2: Automated Script
Clone this repo:
   ```powershell
   git clone https://github.com/Sampong-Starluck/Sampong_dotfile.git
   ```

Run the main installer:
   ```powershell
    ./install.ps1
   ```

   If you encounter issues, try:
   ```powershell
   ./install_app.ps1
   ```

   Note: You may need to adjust file paths in install_app.ps1 for your system.

WARNING: The script may have side effects. For full control, use manual installation.

---

### Option 3: Manual Setup

#### PowerShell

1. Allow script execution:
   ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
   ```

2. Create your profile if it doesn't exist:
   ```powershell
    New-Item $PROFILE.CurrentUserAllHosts -ItemType File -Force
   ```

3. Edit your profile:
   ```powershell
   notepad $PROFILE
   ```

4. Add this line (adjust the path as needed):
   ```powershell
   Import-Module (Resolve-Path '<path-to>/PowerShell/posh_profile.ps1')
   ```
5. Restart your terminal.

---

#### CMD (Clink)

1. Install Oh My Posh: https://ohmyposh.dev/docs/installation/prompt
2. Follow the Oh My Posh Clink guide: https://ohmyposh.dev/docs/installation/clink
3. Customize your prompt as desired.

---

#### Bash (Git Bash, Cygwin)

1. Edit or create your .bashrc:
   ```shell
   vim ~/.bashrc
   ```

2. Add:
   ```shell
   export DIR="<path>/bash"
      if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
      . "$DIR/main.sh"
   ```
---

#### NuShell

1. Edit your Nu environment file:
   ```shell
   open $nu.env-path | edit
   ```
   Add:
      ```shell
      oh-my-posh init nu --config "~/AppData/Local/Programs/oh-my-posh/themes/spaceship.omp.json"
      ```

2. Edit your Nu config file:
   ```shell
   open $nu.config-path | edit
   ```

   Add:
   ```shell
   source ~/.oh-my-posh.nu
   let-env EDITOR = "code"
   use ~/Documents/Sampong_dotfile/nu/main_profile.nu
   use main_profile *
   ```

3. Save and restart NuShell.

---

## Credits

Inspired by and adapted from:
- [Chris Titus Tech's PowerShell Profile](https://github.com/ChrisTitusTech/powershell-profile)
- [Tim Sneath's PowerShell Gist](https://gist.github.com/timsneath/19867b12eee7fd5af2ba)

