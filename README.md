# Sampong\_dotfile

A **lightweight, interactive dotfile manager and installer for Windows**.  
Quickly set up your favorite apps, configure your shells (PowerShell, Bash, NuShell), and deploy your personal dotfiles — all from one place.

Works with **Windows PowerShell 5.1** and **PowerShell 7+**.

---
## 🚀 Quick Start

### 1\. Clone the repository
```shell
  git clone https://github.com/Sampong-Starluck/Sampong_dotfile.git
  cd Sampong_dotfile
```

### 2\. Run the installer
If you see an execution policy warning, use the **Bypass** flag:

- PowerShell 7+
    ```shell
        pwsh -NoProfile -ExecutionPolicy Bypass -File .\\install.ps1
    ```
- Windows PowerShell 5.1
    ```shell
        powershell -NoProfile -ExecutionPolicy Bypass -File .\\install.ps1
    ```

### 3\. Follow the menu

Choose what to do:

-   Install apps (via winget)
-   Configure your shell
-   Or run the all-in-one setup

---
## 📁 Project Structure
```text
Sampong\_dotfile/  
│  
├─ install.ps1 # Main PowerShell installer  
├─ script/  
│ └─ install\_app.ps1 # Helper script for app installations  
│  
├─ dotfiles/ # Your actual shell configs  
│ ├─ PowerShell/  
│ ├─ bash/  
│ └─ nu/  
│  
├─ json/ # Installer configuration files  
│ ├─ apps.json  
│ └─ shells.json  
│  
├─ python/ # Python helper modules and GUI/CLI tools  
│  
└─ main.py # Python entry point (GUI/CLI)
```

---

## ⚙️ Customization

You can easily make it your own:

-   Add/remove apps → Edit `json/apps.json`
-   Change shell options → Edit `json/shells.json`
-   Update your dotfiles → Modify files under `dotfiles/`

---

## 🧠 NuShell Setup

If you use **NuShell**, make sure your config includes this line:

```shell
    use C:/Users/<your-username>/AppData/Roaming/Sampong\_dotfile/nu/main\_profile.nu  
    main\_profile startup
```
> Replace `<your-username>` with your actual Windows username.

---

## 🛠️ Troubleshooting

-   App install fails?  
    Try running the installer again or use `winget install <app>` manually.
    
-   Profile not applied?  
    Open a new PowerShell window and check `$PROFILE`. Ensure the file path and permissions are correct.
    
-   Execution policy issues?  
    Always launch scripts with:  
    `-ExecutionPolicy Bypass -NoProfile`
    

---

## 🐍 Python Tools (Optional)

The repository includes a **Python-based installer** with a GUI and CLI version.

**Requirements:**

-   Python 3.8+ (3.9 or 3.10 recommended)

**Setup and Run:**  
```shell
    pip install -r requirements.txt
```

**Run the GUI (default):**  
``` shell
    python main.py
```

**Run in CLI mode:**  
```shell
  python main.py --cli
```

**Show CLI help:**  
```shell
    python main.py --help-cli
```

**Notes:**

-   The GUI uses `customtkinter`. If it’s missing, install it via  
    ```shell
        pip install customtkinter
    ```
      or switch to CLI mode.
-   The CLI supports keyboard navigation (arrow keys + space).
-   If input behaves oddly, try running it from `cmd.exe` or a normal PowerShell window.

---

## 🔒 Security Notice

-   Scripts modify your user profile. **Review them before running.**
-   Installer downloads apps from the internet — **use it on trusted networks only.**

---

## Original source



- [PowerShell](https://gist.github.com/timsneath/19867b12eee7fd5af2ba) by Tim Sneath

--- 

## Note

 > At the end of the day, this is just my personal dotfile setup script. <br/>
 > It automates installing and configuring all the apps I need before <br/>
 > I start coding — a convenient (and slightly lazy) way to get my development environment ready fast.