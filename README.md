# Personal Dotfile Repository

This repository is created to save all my shell configurations, allowing for easy restoration after resetting or changing my PC.

## Prerequisites

- [Oh My Posh](https://ohmyposh.dev/)
- [Vim](https://www.vim.org/)
- [Neovim](https://neovim.io/)
- [Node Version Manager (NVM)](https://github.com/nvm-sh/nvm)
- [Clink (for customizing CMD)](https://github.com/chrisant996/clink)

### Replacing NVM
I have replaced SDKMAN and NVS (Node Version Switcher) with [Version-fox (vfox)](https://github.com/version-fox/vfox) for both Java and NodeJS.

## Shells Supported

- PowerShell 7
- Command Prompt
- Bash (Git Bash, Cygwin)
- Nushell

## Terminal Emulators

- [Tabby Terminal](https://tabby.sh/)
- [Windows Terminal](https://github.com/microsoft/terminal)

## Command Line-based Text Editors

- Vim
- Neovim

## Installation

### Using Script

To install the configuration using a script, run the following command:

```shell
./install_app.ps1
```

**Warning:** This script has not been tested extensively and might not work as intended or could cause unwanted effects. Manual configuration is recommended.

### Manual Installation

#### Command Prompt (Clink)

I use Clink to modernize the Command Prompt shell and Oh My Posh for customization. Follow the Clink and Oh My Posh manuals for setup instructions.

#### PowerShell

1. Run this command from an elevated PowerShell prompt:

    ```shell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
    ```

2. Create a PowerShell profile:

    ```shell
    New-Item $PROFILE.CurrentUserAllHosts -ItemType File -Force
    ```

3. Edit the profile by running:

    ```shell
    notepad $PROFILE
    ```

4. Add the following code to `$PROFILE`:

    ```shell
    Import-Module (Resolve-Path '$PATH\PowerShell\posh_profile.ps1')
    ```

5. Restart the terminal.

#### Git Bash

1. Create a `.bashrc` file:

    ```shell
    vim ~/.bashrc
    ```

2. Paste the following into the `.bashrc` file:

    ```shell
    export DIR="<path>/bash"
    if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
    . "$DIR/main.sh"
    ```

## Source

The original scripts are from [Chris Titus Tech's GitHub](https://github.com/ChrisTitusTech/powershell-profile) and [Tim Sneath's GitHub Gist](https://gist.github.com/timsneath/19867b12eee7fd5af2ba).

