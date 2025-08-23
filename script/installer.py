#!/usr/bin/env python3
"""
install_env_gui.py
------------------
Modern GUI for development environment setup with comprehensive logging and download progress.
Requires Python 3.7+ and tkinter.
"""

import json
import os
import subprocess
import sys
import threading
import tkinter as tk
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Optional, Callable

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    import requests


class ModernStyle:
    """Modern color scheme and styling constants."""

    # Color palette
    BG_PRIMARY = "#1e1e1e"  # Dark background
    BG_SECONDARY = "#2d2d2d"  # Slightly lighter
    BG_TERTIARY = "#3c3c3c"  # Card backgrounds

    FG_PRIMARY = "#ffffff"  # Primary text
    FG_SECONDARY = "#b3b3b3"  # Secondary text
    FG_ACCENT = "#0078d4"  # Accent blue
    FG_SUCCESS = "#16c60c"  # Success green
    FG_WARNING = "#ffb900"  # Warning orange
    FG_ERROR = "#d13438"  # Error red

    # Fonts
    FONT_MAIN = ("Segoe UI", 10)
    FONT_HEADING = ("Segoe UI", 12, "bold")
    FONT_SMALL = ("Segoe UI", 9)
    FONT_MONO = ("Consolas", 9)


class Logger:
    """Custom logger for GUI applications."""

    def __init__(self, log_widget: scrolledtext.ScrolledText = None):
        self.file_logger = None
        self.log_widget = log_widget
        self.setup_file_logger()

    def setup_file_logger(self):
        """Setup file logging."""
        log_dir = Path.home() / "Documents" / "Sampong_dotfile" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"env_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.file_logger = logging.getLogger(__name__)
        self.file_logger.info("Environment setup session started")

    def log(self, level: str, message: str, show_in_gui: bool = True):
        """Log message to both file and GUI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Log to file
        if level.upper() == "INFO":
            self.file_logger.info(message)
        elif level.upper() == "WARNING":
            self.file_logger.warning(message)
        elif level.upper() == "ERROR":
            self.file_logger.error(message)
        elif level.upper() == "SUCCESS":
            self.file_logger.info(f"SUCCESS: {message}")

        # Log to GUI if widget is available and requested
        if self.log_widget and show_in_gui:
            color_map = {
                "INFO": "#b3b3b3",
                "WARNING": ModernStyle.FG_WARNING,
                "ERROR": ModernStyle.FG_ERROR,
                "SUCCESS": ModernStyle.FG_SUCCESS
            }

            self.log_widget.configure(state='normal')
            self.log_widget.insert(tk.END, formatted_message + "\n")

            # Color the last line
            line_start = self.log_widget.index("end-2c linestart")
            line_end = self.log_widget.index("end-2c lineend")

            tag_name = f"{level.lower()}_{timestamp}"
            self.log_widget.tag_add(tag_name, line_start, line_end)
            self.log_widget.tag_config(tag_name, foreground=color_map.get(level.upper(), "#b3b3b3"))

            self.log_widget.configure(state='disabled')
            self.log_widget.see(tk.END)

    def info(self, message: str, show_in_gui: bool = True):
        """Log info message."""
        self.log(level="INFO", message=message, show_in_gui=show_in_gui)

    def warning(self, message: str, show_in_gui: bool = True):
        """Log warning message."""
        self.log(level="WARNING", message=message, show_in_gui=show_in_gui)

    def error(self, message: str, show_in_gui: bool = True):
        """Log error message."""
        self.log(level="ERROR", message=message, show_in_gui=show_in_gui)

    def success(self, message: str, show_in_gui: bool = True):
        """Log success message."""
        self.log(level="SUCCESS", message=message, show_in_gui=show_in_gui)


class WingetProgressParser:
    """Parser for winget output to extract download progress."""

    @staticmethod
    def parse_progress(output_line: str) -> Optional[Dict]:
        """Parse winget output line for progress information."""
        # Common winget progress patterns
        patterns = [
            # Download progress: "  ██████████████████████████████  100%"
            r'^\s*[█▓▒░\-\s]*\s*(\d+(?:\.\d+)?)%',
            # Download progress with speed: "Downloading... 45.2 MB / 100.0 MB (45%)"
            r'(\d+(?:\.\d+)?)\s*MB\s*/\s*(\d+(?:\.\d+)?)\s*MB\s*\((\d+)%\)',
            # Simple percentage: "Progress: 75%"
            r'Progress:\s*(\d+)%',
            # Downloading indicator
            r'Downloading\s+.*?(\d+)%',
        ]

        for pattern in patterns:
            match = re.search(pattern, output_line, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 3:  # MB/MB pattern
                    current_mb = float(match.group(1))
                    total_mb = float(match.group(2))
                    percentage = int(match.group(3))
                    return {
                        'percentage': percentage,
                        'current_mb': current_mb,
                        'total_mb': total_mb,
                        'status': 'downloading'
                    }
                else:  # Simple percentage pattern
                    percentage = int(match.group(1))
                    return {
                        'percentage': percentage,
                        'status': 'downloading'
                    }

        # Check for other status indicators
        if 'installing' in output_line.lower():
            return {'status': 'installing', 'percentage': None}
        elif 'verifying' in output_line.lower():
            return {'status': 'verifying', 'percentage': None}
        elif 'extracting' in output_line.lower():
            return {'status': 'extracting', 'percentage': None}
        elif 'completed' in output_line.lower() or 'successfully installed' in output_line.lower():
            return {'status': 'completed', 'percentage': 100}

        return None


class ModernCheckbox(tk.Frame):
    """Custom modern checkbox widget."""

    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(parent, bg=ModernStyle.BG_TERTIARY, **kwargs)

        self.checked = tk.BooleanVar()
        self.command = command

        # Create checkbox canvas
        self.canvas = tk.Canvas(
            self, width=20, height=20,
            bg=ModernStyle.BG_TERTIARY,
            highlightthickness=0
        )
        self.canvas.pack(side="left", padx=(0, 8))

        # Create label
        self.label = tk.Label(
            self, text=text,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.FG_PRIMARY,
            font=ModernStyle.FONT_MAIN,
            anchor="w"
        )
        self.label.pack(side="left", fill="x", expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        self.bind("<Button-1>", self.toggle)

        # Initial draw
        self.draw_checkbox()

    def toggle(self, event=None):
        """Toggle checkbox state."""
        self.checked.set(not self.checked.get())
        self.draw_checkbox()
        if self.command:
            self.command()

    def draw_checkbox(self):
        """Draw the checkbox based on current state."""
        self.canvas.delete("all")

        # Draw border
        self.canvas.create_rectangle(
            2, 2, 18, 18,
            outline=ModernStyle.FG_ACCENT if self.checked.get() else ModernStyle.FG_SECONDARY,
            fill=ModernStyle.FG_ACCENT if self.checked.get() else ModernStyle.BG_SECONDARY,
            width=2
        )

        # Draw checkmark
        if self.checked.get():
            self.canvas.create_line(6, 10, 9, 13, fill="white", width=2)
            self.canvas.create_line(9, 13, 14, 8, fill="white", width=2)

    def get(self):
        """Get checkbox state."""
        return self.checked.get()

    def set(self, value):
        """Set checkbox state."""
        self.checked.set(value)
        self.draw_checkbox()


class ScrollableFrame(tk.Frame):
    """Scrollable frame with mouse wheel support."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self, bg=ModernStyle.BG_SECONDARY,
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(
            self.canvas, bg=ModernStyle.BG_SECONDARY
        )

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda er1: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self.bind_mousewheel()

    def bind_mousewheel(self):
        """Bind mouse wheel events to canvas."""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)


class ModernButton(tk.Button):
    """Modern styled button."""

    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        # Define button styles
        styles = {
            "primary": {
                "bg": ModernStyle.FG_ACCENT,
                "fg": "white",
                "activebackground": "#106ebe",
                "activeforeground": "white"
            },
            "secondary": {
                "bg": ModernStyle.BG_TERTIARY,
                "fg": ModernStyle.FG_PRIMARY,
                "activebackground": "#4a4a4a",
                "activeforeground": ModernStyle.FG_PRIMARY
            },
            "success": {
                "bg": ModernStyle.FG_SUCCESS,
                "fg": "white",
                "activebackground": "#13a10e",
                "activeforeground": "white"
            },
            "danger": {
                "bg": ModernStyle.FG_ERROR,
                "fg": "white",
                "activebackground": "#b02a2e",
                "activeforeground": "white"
            }
        }

        style_config = styles.get(style, styles["primary"])

        super().__init__(
            parent,
            text=text,
            command=command,
            font=ModernStyle.FONT_MAIN,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            **style_config,
            **kwargs
        )


def open_log_folder():
    """Open the log folder in file explorer."""
    log_dir = Path.home() / "Documents" / "Sampong_dotfile" / "logs"
    if log_dir.exists():
        os.startfile(log_dir)
    else:
        messagebox.showwarning("Warning", "Log folder not found!")


class ProgressDialog(tk.Toplevel):
    """Modern progress dialog with enhanced logging and download progress."""

    def __init__(self, parent, title="Progress"):
        super().__init__(parent)

        self.view_logs_btn = None
        self.close_btn = None
        self.log_text = None
        self.status_label = tk.Label(
            self, text="Preparing...",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_SECONDARY,
            font=ModernStyle.FONT_MAIN
        )
        self.current_status = None
        self.progress = None
        self.current_progress = None
        self.title(title)
        self.geometry("700x500")
        self.configure(bg=ModernStyle.BG_PRIMARY)
        self.resizable(True, True)

        # Center on parent
        self.transient(parent)
        self.grab_set()

        # Create logger
        self.logger = None

        # Create widgets
        self.setup_ui()

    def setup_ui(self):
        """Setup progress dialog UI."""
        # Title
        title_label = tk.Label(
            self, text="Operation Progress",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_PRIMARY,
            font=ModernStyle.FONT_HEADING
        )
        title_label.pack(pady=(20, 10))

        # Progress section
        progress_frame = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        progress_frame.pack(pady=10, padx=20, fill="x")

        # Overall progress
        overall_label = tk.Label(
            progress_frame, text="Overall Progress:",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_SECONDARY,
            font=ModernStyle.FONT_SMALL,
            anchor="w"
        )
        overall_label.pack(fill="x")

        self.progress = ttk.Progressbar(
            progress_frame, mode='determinate',
            length=500
        )
        self.progress.pack(pady=(2, 10), fill="x")

        # Current item progress
        current_label = tk.Label(
            progress_frame, text="Current Item:",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_SECONDARY,
            font=ModernStyle.FONT_SMALL,
            anchor="w"
        )
        current_label.pack(fill="x")

        self.current_progress = ttk.Progressbar(
            progress_frame, mode='determinate',
            length=500
        )
        self.current_progress.pack(pady=(2, 5), fill="x")

        # Current item status
        self.current_status = tk.Label(
            progress_frame, text="Ready...",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_SECONDARY,
            font=ModernStyle.FONT_SMALL,
            anchor="w"
        )
        self.current_status.pack(fill="x", pady=(0, 5))

        # Status label
        self.status_label.pack(pady=5)

        # Log area with enhanced styling
        log_frame = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)

        log_label = tk.Label(
            log_frame, text="📋 Operation Log:",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_PRIMARY,
            font=ModernStyle.FONT_MAIN,
            anchor="w"
        )
        log_label.pack(fill="x", pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, width=80,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.FG_PRIMARY,
            font=ModernStyle.FONT_MONO,
            insertbackground=ModernStyle.FG_PRIMARY,
            state='disabled',
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True)

        # Initialize logger with the text widget
        self.logger = Logger(self.log_text)

        # Button frame
        btn_frame = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        btn_frame.pack(pady=10)

        # Close button (initially disabled)
        self.close_btn = ModernButton(
            btn_frame, text="Close",
            command=self.destroy,
            state="disabled"
        )
        self.close_btn.pack(side="left", padx=(0, 10))

        # View logs button
        self.view_logs_btn = ModernButton(
            btn_frame, text="📁 Open Log Folder",
            command=open_log_folder,
            style="secondary"
        )
        self.view_logs_btn.pack(side="left")

    def update_progress(self, overall_value, current_value=None, status="", current_status="", log_message="",
                        log_level="INFO"):
        """Update progress dialog with enhanced logging and current item progress."""
        self.progress['value'] = overall_value

        if current_value is not None:
            self.current_progress['value'] = current_value

        if status:
            self.status_label.config(text=status)

        if current_status:
            self.current_status.config(text=current_status)

        if log_message and self.logger:
            if log_level.upper() == "SUCCESS":
                self.logger.success(log_message)
            elif log_level.upper() == "WARNING":
                self.logger.warning(log_message)
            elif log_level.upper() == "ERROR":
                self.logger.error(log_message)
            else:
                self.logger.info(log_message)

        self.update()

    def reset_current_progress(self):
        """Reset current item progress bar."""
        self.current_progress['value'] = 0
        self.current_status.config(text="Ready...")

    def finish(self):
        """Mark progress as finished."""
        self.close_btn.config(state="normal")
        self.status_label.config(text="✅ Operation completed!")
        self.current_progress['value'] = 100
        self.current_status.config(text="Completed!")
        if self.logger:
            self.logger.success("Operation completed successfully")


def install_single_app_with_progress(apps: Dict, progress_callback: Callable):
    """Install a single app with real-time progress tracking."""
    app_name = apps.get("name", "Unknown")
    app_id = apps.get("id", "")

    try:
        cmd = [
            "winget", "install", "-e", "--id", app_id,
            "--accept-source-agreements", "--accept-package-agreements"
        ]

        progress_callback(0, f"Starting {app_name} installation...", f"Executing: {' '.join(cmd)}")

        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        current_progress = 0
        last_status = "initializing"

        # Read output line by line
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break

            if output:
                output = output.strip()
                if output:  # Only process non-empty lines
                    # Parse progress from winget output
                    progress_info = WingetProgressParser.parse_progress(output)

                    if progress_info:
                        status = progress_info.get('status', 'processing')
                        percentage = progress_info.get('percentage')

                        if percentage is not None:
                            current_progress = percentage

                            # Format status message based on available info
                            if 'current_mb' in progress_info and 'total_mb' in progress_info:
                                status_msg = f"Downloading {progress_info['current_mb']:.1f} MB / {progress_info['total_mb']:.1f} MB ({percentage}%)"
                            else:
                                status_msg = f"{status.title()} ({percentage}%)"

                            progress_callback(current_progress, status_msg, f"Progress: {output}")
                        else:
                            # Status without percentage
                            if status != last_status:
                                status_msg = f"{status.title()}..."
                                progress_callback(current_progress, status_msg, f"Status: {output}")
                                last_status = status
                    else:
                        # Log other output
                        if any(keyword in output.lower() for keyword in
                               ['downloading', 'installing', 'verifying', 'extracting']):
                            progress_callback(current_progress, f"{app_name}: {output}", output)

        # Wait for process to complete
        return_code = process.wait()

        # Read any remaining stderr
        stderr_output = process.stderr.read()

        if return_code == 0:
            progress_callback(100, f"✅ {app_name} installed successfully", f"Installation completed successfully")
            return True
        else:
            error_msg = f"❌ {app_name} installation failed (Exit code: {return_code})"
            if stderr_output:
                error_msg += f"\nError: {stderr_output}"
            progress_callback(0, error_msg, error_msg)
            return False

    except subprocess.TimeoutExpired:
        error_msg = f"⏰ {app_name} installation timed out"
        progress_callback(0, error_msg, error_msg)
        return False
    except Exception as er:
        error_msg = f"❌ {app_name} installation error: {str(er)}"
        progress_callback(0, error_msg, error_msg)
        return False


def setup_styles():
    """Configure ttk styles."""
    style = ttk.Style()
    style.theme_use('clam')

    # Configure progressbar
    style.configure(
        "TProgressbar",
        background=ModernStyle.FG_ACCENT,
        troughcolor=ModernStyle.BG_SECONDARY,
        borderwidth=0,
        lightcolor=ModernStyle.FG_ACCENT,
        darkcolor=ModernStyle.FG_ACCENT
    )

    # Configure scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=ModernStyle.BG_TERTIARY,
        troughcolor=ModernStyle.BG_SECONDARY,
        borderwidth=0,
        arrowcolor=ModernStyle.FG_SECONDARY,
        darkcolor=ModernStyle.BG_TERTIARY,
        lightcolor=ModernStyle.BG_TERTIARY
    )


def _configure_nushell_with_logging(dotfiles_dir: Path, logger: Logger):
    """Configure NuShell with detailed logging."""
    logger.info("Configuring NuShell...")

    # Create main profile
    main_profile = dotfiles_dir / "main_profile.nu"
    if not main_profile.exists():
        main_profile.write_text("# NuShell main profile\n")
        logger.info(f"Created main profile: {main_profile}")
    else:
        logger.info(f"Main profile already exists: {main_profile}")

    # Configure NuShell directories
    nu_config_dir = Path(os.environ.get("APPDATA", "")) / "nushell"
    logger.info(f"NuShell config directory: {nu_config_dir}")
    nu_config_dir.mkdir(exist_ok=True)

    env_nu = nu_config_dir / "env.nu"
    config_nu = nu_config_dir / "config.nu"

    env_nu.touch()
    config_nu.touch()
    logger.info("Created/verified env.nu and config.nu files")

    # Add Oh-My-Posh if available
    theme_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "oh-my-posh" / "themes" / "spaceship.omp.json",
        Path("C:/Program Files/oh-my-posh/themes/spaceship.omp.json")
    ]

    theme_path = next((p for p in theme_paths if p.exists()), None)
    if theme_path:
        logger.info(f"Found Oh-My-Posh theme: {theme_path}")
        omp_line = f'oh-my-posh init nu --config "{theme_path}"\n'
        env_content = env_nu.read_text() if env_nu.exists() else ""
        if "oh-my-posh init nu" not in env_content:
            env_nu.write_text(env_content + "\n" + omp_line)
            logger.success("Added Oh-My-Posh configuration to env.nu")
        else:
            logger.info("Oh-My-Posh already configured in env.nu")
    else:
        logger.warning("Oh-My-Posh spaceship theme not found")

    # Source custom profile
    include_line = f"use {main_profile}\n"
    config_content = config_nu.read_text() if config_nu.exists() else ""
    if str(main_profile) not in config_content:
        config_nu.write_text(config_content + include_line)
        logger.success("Added custom profile source to config.nu")
    else:
        logger.info("Custom profile already sourced in config.nu")


def _configure_bash_with_logging(dotfiles_dir: Path, logger: Logger):
    """Configure Bash with detailed logging."""
    logger.info("Configuring Bash...")

    main_sh = dotfiles_dir / "main.sh"
    if not main_sh.exists():
        main_sh.write_text("# Bash main script\n")
        logger.info(f"Created main script: {main_sh}")
    else:
        logger.info(f"Main script already exists: {main_sh}")

    bashrc = Path.home() / ".bashrc"
    logger.info(f"Configuring .bashrc: {bashrc}")
    bashrc.touch()

    source_line = f'source "{main_sh}"\n'
    bashrc_content = bashrc.read_text() if bashrc.exists() else ""
    if str(main_sh) not in bashrc_content:
        bashrc.write_text(bashrc_content + f"\n# Source Sampong bash customizations\n{source_line}")
        logger.success("Added custom script source to .bashrc")
    else:
        logger.info("Custom script already sourced in .bashrc")


def _configure_powershell_with_logging(logger: Logger):
    """Configure PowerShell with detailed logging."""
    logger.info("Configuring PowerShell...")

    try:
        result = subprocess.run([
            "powershell", "-Command", "echo $PROFILE"
        ], capture_output=True, text=True, check=True)

        profile_path = Path(result.stdout.strip())
        logger.info(f"PowerShell profile path: {profile_path}")

        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.touch()

        entries = [
            "Import-Module (Resolve-Path '~/Documents/Sampong_dotfile/PowerShell/posh_profile.ps1')",
            "Import-Module -Name Microsoft.WinGet.CommandNotFound",
            'Invoke-Expression "$(vfox activate pwsh)"'
        ]

        profile_content = profile_path.read_text() if profile_path.exists() else ""

        added_entries = []
        for entry in entries:
            if entry not in profile_content:
                profile_content += f"\n{entry}"
                added_entries.append(entry)

        if added_entries:
            profile_path.write_text(profile_content)
            logger.success(f"Added {len(added_entries)} entries to PowerShell profile")
            for entry in added_entries:
                logger.info(f"Added: {entry}")
        else:
            logger.info("PowerShell profile already configured")

    except subprocess.CalledProcessError as er:
        error_msg = f"Failed to configure PowerShell: {er}"
        logger.error(error_msg)
        raise Exception(error_msg)


def configure_shell_with_logging(shell_config: Dict, logger: Logger):
    """Configure shell with detailed logging."""
    shell_name = shell_config.get("name", "Unknown")
    shell_id = shell_config.get("id", "")

    logger.info(f"Configuring {shell_name} (ID: {shell_id})")

    # Create dotfiles directory
    dotfiles_dir = Path.home() / "Documents" / "Sampong_dotfile" / shell_id
    logger.info(f"Creating dotfiles directory: {dotfiles_dir}")
    dotfiles_dir.mkdir(parents=True, exist_ok=True)

    if shell_id == "nu":
        _configure_nushell_with_logging(dotfiles_dir, logger)
    elif shell_id == "bash":
        _configure_bash_with_logging(dotfiles_dir, logger)
    elif shell_id == "posh":
        _configure_powershell_with_logging(logger)
    else:
        logger.warning(f"Unknown shell configuration: {shell_id}")

    logger.success(f"{shell_name} configuration completed")


class EnvSetupGUI:
    """Main GUI application with comprehensive logging and download progress."""

    def __init__(self):
        self.shell_checkboxes = None
        self.shells_scroll = None
        self.app_checkboxes = []
        self.apps_scroll = None
        self.root = tk.Tk()
        self.script_dir = Path(__file__).parent

        # Initialize logger
        self.logger = Logger()

        # Load data
        self.apps = self._load_json("../json/apps.json", "apps")
        self.shells = self._load_json("../json/shells.json", "shells")
        self.visible_shells = [s for s in self.shells if not s.get("hidden", False)]

        # Setup UI
        self.setup_window()
        setup_styles()
        self.create_widgets()

        self.logger.info("GUI application initialized")

    def _load_json(self, file_path: str, key: str) -> List[Dict]:
        """Load and parse JSON configuration files."""
        json_path = self.script_dir / file_path
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data.get(key, []))} items from {file_path}")
            return data.get(key, [])
        except (FileNotFoundError, json.JSONDecodeError) as er:
            error_msg = f"Failed to load {file_path}: {er}"
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            return []

    def setup_window(self):
        """Configure main window."""
        self.root.title("Development Environment Setup")
        self.root.geometry("900x700")
        self.root.configure(bg=ModernStyle.BG_PRIMARY)
        self.root.minsize(700, 500)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")

    def create_widgets(self):
        """Create main UI widgets."""
        # Header
        header_frame = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        title_label = tk.Label(
            header_frame,
            text="Development Environment Setup",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_PRIMARY,
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Install applications and configure development shells with detailed progress tracking",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_SECONDARY,
            font=ModernStyle.FONT_MAIN
        )
        subtitle_label.pack(pady=(5, 0))

        # Main content
        main_frame = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left panel - Applications
        left_panel = tk.Frame(main_frame, bg=ModernStyle.BG_SECONDARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.create_apps_panel(left_panel)

        # Right panel - Shells
        right_panel = tk.Frame(main_frame, bg=ModernStyle.BG_SECONDARY)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.create_shells_panel(right_panel)

        # Bottom panel - Actions
        bottom_frame = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.create_action_buttons(bottom_frame)

    def create_apps_panel(self, parent):
        """Create applications selection panel."""
        # Header
        header_frame = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        apps_label = tk.Label(
            header_frame,
            text="📦 Applications",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.FG_PRIMARY,
            font=ModernStyle.FONT_HEADING
        )
        apps_label.pack(side="left")

        # Select all/none buttons
        btn_frame = tk.Frame(header_frame, bg=ModernStyle.BG_SECONDARY)
        btn_frame.pack(side="right")

        select_all_btn = tk.Button(
            btn_frame, text="All",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.FG_ACCENT,
            font=ModernStyle.FONT_SMALL,
            relief="flat", bd=0, padx=8, pady=2,
            cursor="hand2",
            command=lambda: self.select_all_apps(True)
        )
        select_all_btn.pack(side="left", padx=(0, 5))

        select_none_btn = tk.Button(
            btn_frame, text="None",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.FG_ACCENT,
            font=ModernStyle.FONT_SMALL,
            relief="flat", bd=0, padx=8, pady=2,
            cursor="hand2",
            command=lambda: self.select_all_apps(False)
        )
        select_none_btn.pack(side="left")

        # Scrollable apps list
        self.apps_scroll = ScrollableFrame(parent)
        self.apps_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for apps in self.apps:
            checkbox = ModernCheckbox(
                self.apps_scroll.scrollable_frame,
                text=f"{apps.get('name', 'Unknown')} - {apps.get('version', 'Latest')}"
            )
            checkbox.pack(fill="x", pady=2)
            checkbox.app_data = apps
            self.app_checkboxes.append(checkbox)

    def create_shells_panel(self, parent):
        """Create shells configuration panel."""
        # Header
        header_frame = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        shells_label = tk.Label(
            header_frame,
            text="🐚 Shells",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.FG_PRIMARY,
            font=ModernStyle.FONT_HEADING
        )
        shells_label.pack(side="left")

        # Select all/none buttons
        btn_frame = tk.Frame(header_frame, bg=ModernStyle.BG_SECONDARY)
        btn_frame.pack(side="right")

        select_all_btn = tk.Button(
            btn_frame, text="All",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.FG_ACCENT,
            font=ModernStyle.FONT_SMALL,
            relief="flat", bd=0, padx=8, pady=2,
            cursor="hand2",
            command=lambda: self.select_all_shells(True)
        )
        select_all_btn.pack(side="left", padx=(0, 5))

        select_none_btn = tk.Button(
            btn_frame, text="None",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.FG_ACCENT,
            font=ModernStyle.FONT_SMALL,
            relief="flat", bd=0, padx=8, pady=2,
            cursor="hand2",
            command=lambda: self.select_all_shells(False)
        )
        select_none_btn.pack(side="left")

        # Scrollable shells list
        self.shells_scroll = ScrollableFrame(parent)
        self.shells_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.shell_checkboxes = []
        for shell in self.visible_shells:
            if shell.get("id") == "all":
                continue

            checkbox = ModernCheckbox(
                self.shells_scroll.scrollable_frame,
                text=shell.get('name', 'Unknown')
            )
            checkbox.pack(fill="x", pady=2)
            checkbox.shell_data = shell
            self.shell_checkboxes.append(checkbox)

    def create_action_buttons(self, parent):
        """Create action buttons."""
        btn_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        btn_frame.pack()

        # Install winget button
        winget_btn = ModernButton(
            btn_frame, text="📥 Install Winget",
            command=self.install_winget_clicked,
            style="secondary"
        )
        winget_btn.pack(side="left", padx=(0, 10))

        # Install apps button
        install_apps_btn = ModernButton(
            btn_frame, text="📦 Install Selected Apps",
            command=self.install_apps_clicked,
            style="primary"
        )
        install_apps_btn.pack(side="left", padx=(0, 10))

        # Configure shells button
        config_shells_btn = ModernButton(
            btn_frame, text="🐚 Configure Selected Shells",
            command=self.configure_shells_clicked,
            style="primary"
        )
        config_shells_btn.pack(side="left", padx=(0, 10))

        # Install all button
        install_all_btn = ModernButton(
            btn_frame, text="🚀 Install Everything",
            command=self.install_all_clicked,
            style="success"
        )
        install_all_btn.pack(side="left", padx=(0, 10))

        # View logs button
        view_logs_btn = ModernButton(
            btn_frame, text="📋 View Logs",
            command=self.view_logs_clicked,
            style="secondary"
        )
        view_logs_btn.pack(side="left")

    def view_logs_clicked(self):
        """Open log folder."""
        log_dir = Path.home() / "Documents" / "Sampong_dotfile" / "logs"
        if log_dir.exists():
            os.startfile(log_dir)
            self.logger.info("Opened log folder")
        else:
            messagebox.showwarning("Warning", "Log folder not found!")
            self.logger.warning("Log folder not found")

    def select_all_apps(self, select: bool):
        """Select/deselect all applications."""
        for checkbox in self.app_checkboxes:
            checkbox.set(select)
        action = "selected" if select else "deselected"
        self.logger.info(f"All applications {action}")

    def select_all_shells(self, select: bool):
        """Select/deselect all shells."""
        for checkbox in self.shell_checkboxes:
            checkbox.set(select)
        action = "selected" if select else "deselected"
        self.logger.info(f"All shells {action}")

    def get_selected_apps(self) -> List[Dict]:
        """Get selected applications."""
        selected = [cb.app_data for cb in self.app_checkboxes if cb.get()]
        self.logger.info(f"Selected {len(selected)} applications for installation")
        return selected

    def get_selected_shells(self) -> List[Dict]:
        """Get selected shells."""
        selected = [cb.shell_data for cb in self.shell_checkboxes if cb.get()]
        self.logger.info(f"Selected {len(selected)} shells for configuration")
        return selected

    def check_winget(self) -> bool:
        """Check if winget is available."""
        try:
            result = subprocess.run(
                ["winget", "--version"],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info(f"Winget is available: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("Winget is not available")
            return False

    def install_winget_clicked(self):
        """Handle install winget button click."""
        if self.check_winget():
            messagebox.showinfo("Info", "Winget is already installed!")
            return

        progress_dialog = ProgressDialog(self.root, "Installing Winget")

        def install_winget():
            try:
                progress_dialog.update_progress(10, 0, "Downloading winget installer...", "Preparing download...",
                                                "Starting winget installation")

                url = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
                temp_path = Path.home() / "Downloads" / "DesktopAppInstaller.msixbundle"

                progress_dialog.update_progress(20, 10, "Downloading...", "Connecting to server...",
                                                f"Downloading from: {url}")

                # Download with progress tracking
                response = requests.get(url, stream=True)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                download_progress = int((downloaded / total_size) * 100)
                                progress_dialog.update_progress(
                                    30, download_progress,
                                    "Downloading winget installer...",
                                    f"Downloaded {downloaded // 1024 // 1024} MB / {total_size // 1024 // 1024} MB ({download_progress}%)"
                                )

                progress_dialog.update_progress(60, 100, "Installing winget...", "Download completed",
                                                f"Saved to: {temp_path}")
                progress_dialog.reset_current_progress()

                progress_dialog.update_progress(70, 50, "Installing winget...", "Running PowerShell installation...",
                                                "Executing installation command")

                subprocess.run([
                    "powershell", "-Command",
                    f"Add-AppxPackage -Path '{temp_path}'"
                ], check=True, capture_output=True, text=True)

                progress_dialog.update_progress(90, 100, "Verifying installation...", "Installation completed",
                                                "Checking winget availability")

                if self.check_winget():
                    progress_dialog.update_progress(100, 100, "Winget installed successfully!",
                                                    "Verification successful", "Winget installation completed",
                                                    "SUCCESS")
                    messagebox.showinfo("Success", "Winget installed successfully!")
                else:
                    progress_dialog.update_progress(100, 0, "Installation verification failed", "Verification failed",
                                                    "Winget installation verification failed", "ERROR")
                    messagebox.showerror("Error", "Winget installation verification failed")

            except Exception as er:
                error_msg = f"Failed to install winget: {er}"
                progress_dialog.update_progress(100, 0, "Installation failed", "Error occurred", error_msg, "ERROR")
                messagebox.showerror("Error", error_msg)
            finally:
                progress_dialog.finish()

        threading.Thread(target=install_winget, daemon=True).start()

    def install_apps_clicked(self):
        """Handle install apps button click."""
        selected_apps = self.get_selected_apps()
        if not selected_apps:
            messagebox.showwarning("Warning", "No applications selected!")
            return

        self.install_apps_with_progress(selected_apps)

    def install_apps_with_progress(self, apps: List[Dict]):
        """Install apps with progress dialog and detailed download progress."""
        progress_dialog = ProgressDialog(self.root, "Installing Applications")

        def install_worker():
            total = len(apps)
            progress_dialog.update_progress(0, 0, "Starting installation...", "Preparing...",
                                            f"Installing {total} applications")

            successful_installs = 0
            failed_installs = 0

            for i, application in enumerate(apps):
                app_name = application.get("name", "Unknown")

                # Update overall progress
                overall_progress = int((i / total) * 100)
                progress_dialog.update_progress(
                    overall_progress, 0,
                    f"Installing {app_name}... ({i + 1}/{total})",
                    "Preparing installation...",
                    f"Starting installation of {app_name}"
                )

                # Reset current progress for this app
                progress_dialog.reset_current_progress()

                # Define progress callback for this app
                def app_progress_callback(current_progress, status, log_msg):
                    progress_dialog.update_progress(
                        overall_progress, current_progress,
                        f"Installing {app_name}... ({i + 1}/{total})",
                        status, log_msg
                    )

                # Install the app with progress tracking
                success = install_single_app_with_progress(application, app_progress_callback)

                if success:
                    successful_installs += 1
                else:
                    failed_installs += 1

                # Small delay to show completion status
                time.sleep(0.5)

            # Final summary
            summary = f"Installation completed: {successful_installs} successful, {failed_installs} failed"
            progress_dialog.update_progress(
                100, 100,
                "Installation completed!",
                "All installations finished",
                summary,
                "SUCCESS" if failed_installs == 0 else "WARNING"
            )
            progress_dialog.finish()

        threading.Thread(target=install_worker, daemon=True).start()

    def configure_shells_clicked(self):
        """Handle configure shells button click."""
        selected_shells = self.get_selected_shells()
        if not selected_shells:
            messagebox.showwarning("Warning", "No shells selected!")
            return

        self.configure_shells_with_progress(selected_shells)

    def configure_shells_with_progress(self, shells: List[Dict]):
        """Configure shells with progress dialog and detailed logging."""
        progress_dialog = ProgressDialog(self.root, "Configuring Shells")

        def configure_worker():
            total = len(shells)
            progress_dialog.update_progress(0, 0, "Starting shell configuration...", "Preparing...",
                                            f"Configuring {total} shells")

            successful_configs = 0
            failed_configs = 0

            for i, shell in enumerate(shells):
                shell_name = shell.get("name", "Unknown")
                shell_id = shell.get("id", "")

                overall_progress = int((i / total) * 100)
                progress_dialog.update_progress(
                    overall_progress, 0,
                    f"Configuring {shell_name}... ({i + 1}/{total})",
                    "Starting configuration...",
                    f"Starting configuration of {shell_name} (ID: {shell_id})"
                )

                try:
                    # Configuration steps with progress updates
                    progress_dialog.update_progress(
                        overall_progress, 25,
                        current_status="Creating directories...",
                        log_message=f"Creating dotfiles directory for {shell_name}"
                    )

                    progress_dialog.update_progress(
                        overall_progress, 50,
                        current_status="Writing configuration files...",
                        log_message=f"Writing configuration files for {shell_name}"
                    )

                    configure_shell_with_logging(shell, progress_dialog.logger)

                    progress_dialog.update_progress(
                        overall_progress, 100,
                        current_status="Configuration completed",
                        log_message=f"✅ {shell_name} configured successfully",
                        log_level="SUCCESS"
                    )

                    successful_configs += 1

                except Exception as er:
                    failed_configs += 1
                    error_msg = f"❌ {shell_name} configuration failed: {str(er)}"
                    progress_dialog.update_progress(
                        overall_progress, 0,
                        current_status="Configuration failed",
                        log_message=error_msg,
                        log_level="ERROR"
                    )

                time.sleep(0.3)  # Brief pause to show completion

            # Final summary
            summary = f"Configuration completed: {successful_configs} successful, {failed_configs} failed"
            progress_dialog.update_progress(
                100, 100,
                "Configuration completed!",
                "All configurations finished",
                summary,
                "SUCCESS" if failed_configs == 0 else "WARNING"
            )
            progress_dialog.finish()

        threading.Thread(target=configure_worker, daemon=True).start()

    def install_all_clicked(self):
        """Handle install all button click with comprehensive logging and progress tracking."""
        self.logger.info("Starting complete environment setup")

        # Select all items
        self.select_all_apps(True)
        self.select_all_shells(True)

        selected_apps = self.get_selected_apps()
        selected_shells = self.get_selected_shells()

        progress_dialog = ProgressDialog(self.root, "Complete Environment Setup")

        def install_all_worker():
            try:
                total_phases = 2
                current_phase = 0

                # Phase 1: Install applications
                if selected_apps:
                    current_phase += 1
                    progress_dialog.update_progress(0, 0,
                                                    f"Phase {current_phase}/{total_phases}: Installing applications...",
                                                    "Starting application phase...",
                                                    "Starting application installation phase")

                    total_apps = len(selected_apps)
                    successful_apps = 0

                    for i, application in enumerate(selected_apps):
                        app_name = application.get("name", "Unknown")

                        # Calculate phase progress (0-50% for apps)
                        phase_progress = int((i / total_apps) * 50)

                        progress_dialog.update_progress(
                            phase_progress, 0,
                            f"Phase {current_phase}/{total_phases}: Installing {app_name}... ({i + 1}/{total_apps})",
                            "Preparing installation...",
                            f"Installing {app_name}"
                        )

                        # Define progress callback for this app
                        def app_progress_callback(current_progress, status, log_msg):
                            progress_dialog.update_progress(
                                phase_progress, current_progress,
                                f"Phase {current_phase}/{total_phases}: Installing {app_name}... ({i + 1}/{total_apps})",
                                status, log_msg
                            )

                        # Install the app with progress tracking
                        success = install_single_app_with_progress(application, app_progress_callback)

                        if success:
                            successful_apps += 1

                        time.sleep(0.3)  # Brief pause between apps

                    progress_dialog.update_progress(
                        50, 100,
                        f"Phase {current_phase}/{total_phases} completed",
                        "Application phase finished",
                        f"Apps phase completed: {successful_apps}/{total_apps} successful",
                        "SUCCESS" if successful_apps == total_apps else "WARNING"
                    )

                # Phase 2: Configure shells
                if selected_shells:
                    current_phase += 1
                    progress_dialog.update_progress(50, 0,
                                                    f"Phase {current_phase}/{total_phases}: Configuring shells...",
                                                    "Starting shell configuration phase...",
                                                    "Starting shell configuration phase")

                    total_shells = len(selected_shells)
                    successful_shells = 0

                    for i, shell in enumerate(selected_shells):
                        shell_name = shell.get("name", "Unknown")

                        # Calculate phase progress (50-100% for shells)
                        phase_progress = 50 + int((i / total_shells) * 50)

                        progress_dialog.update_progress(
                            phase_progress, 0,
                            f"Phase {current_phase}/{total_phases}: Configuring {shell_name}... ({i + 1}/{total_shells})",
                            "Starting configuration...",
                            f"Configuring {shell_name}"
                        )

                        try:
                            # Configuration steps with progress updates
                            progress_dialog.update_progress(
                                phase_progress, 33,
                                current_status="Creating directories...",
                                log_message=f"Creating dotfiles directory for {shell_name}"
                            )

                            progress_dialog.update_progress(
                                phase_progress, 66,
                                current_status="Writing configuration files...",
                                log_message=f"Writing configuration files for {shell_name}"
                            )

                            configure_shell_with_logging(shell, progress_dialog.logger)

                            progress_dialog.update_progress(
                                phase_progress, 100,
                                current_status="Configuration completed",
                                log_message=f"✅ {shell_name} configured successfully",
                                log_level="SUCCESS"
                            )

                            successful_shells += 1

                        except Exception as er:
                            error_msg = f"❌ {shell_name} configuration failed: {str(er)}"
                            progress_dialog.update_progress(
                                phase_progress, 0,
                                current_status="Configuration failed",
                                log_message=error_msg,
                                log_level="ERROR"
                            )

                        time.sleep(0.3)  # Brief pause between shells

                    progress_dialog.update_progress(
                        100, 100,
                        f"Phase {current_phase}/{total_phases} completed",
                        "Shell configuration finished",
                        f"Shells phase completed: {successful_shells}/{total_shells} successful",
                        "SUCCESS" if successful_shells == total_shells else "WARNING"
                    )

                # Final summary
                final_message = "🎉 Complete environment setup finished!"
                progress_dialog.update_progress(100, 100, final_message, "All phases completed", final_message,
                                                "SUCCESS")

            except Exception as er:
                error_msg = f"Complete setup failed: {str(er)}"
                progress_dialog.update_progress(100, 0, "Setup failed", "Error occurred", error_msg, "ERROR")
            finally:
                progress_dialog.finish()

        threading.Thread(target=install_all_worker, daemon=True).start()

    def run(self):
        """Start the GUI application."""
        try:
            self.root.mainloop()
        except Exception as ee:
            self.logger.error(f"Application error: {ee}")
            messagebox.showerror("Error", f"Application error: {ee}")
        finally:
            self.logger.info("GUI application closed")


if __name__ == "__main__":
    try:
        app = EnvSetupGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application startup error: {e}")
        sys.exit(1)