import customtkinter as ctk
import threading
from typing import List, Dict, Any
from python.apps import load_apps
from python.shells import load_shells, configure_shell
from python.winget import install_winget, install_apps
from python.check_network import internet_on
import python.config as config

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CollapsibleFrame(ctk.CTkFrame):
    """Collapsible frame with header and content."""

    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.is_expanded = False
        self.content_frame = None
        self.selected_count = 0
        self.total_count = 0

        # Header frame
        self.header = ctk.CTkFrame(self, fg_color="gray30")
        self.header.pack(fill="x", padx=5, pady=2)

        # Header content
        header_content = ctk.CTkFrame(self.header, fg_color="transparent")
        header_content.pack(fill="x", padx=10, pady=8)

        self.arrow_label = ctk.CTkLabel(
            header_content,
            text="▶",
            font=("Helvetica", 12),
            text_color="lightblue",
            width=30,
        )
        self.arrow_label.pack(side="left", padx=(0, 10))

        self.title_label = ctk.CTkLabel(
            header_content,
            text=title,
            font=("Helvetica", 12, "bold"),
            text_color="white",
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        self.count_label = ctk.CTkLabel(
            header_content,
            text="0/0",
            font=("Helvetica", 10),
            text_color="gray",
        )
        self.count_label.pack(side="right", padx=10)

        # Bind click event
        for widget in [self.header, header_content, self.arrow_label, self.title_label]:
            widget.bind("<Button-1>", self._on_click)

        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="gray25")
        self.content_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.content_frame.pack_forget()

    def _on_click(self, event):
        """Toggle expansion on click."""
        self.toggle()

    def toggle(self):
        """Toggle expanded/collapsed state."""
        self.is_expanded = not self.is_expanded

        if self.is_expanded:
            self.arrow_label.configure(text="▼")
            self.content_frame.pack(fill="x", padx=5, pady=(0, 5))
        else:
            self.arrow_label.configure(text="▶")
            self.content_frame.pack_forget()

    def get_content_frame(self):
        """Return the content frame for adding widgets."""
        return self.content_frame

    def update_count(self, selected: int, total: int):
        """Update selection counter."""
        self.selected_count = selected
        self.total_count = total
        self.count_label.configure(text=f"{selected}/{total}")


class AppCheckboxFrame(ctk.CTkFrame):
    """Frame with app checkbox."""

    def __init__(self, parent, app: Dict[str, Any], var, callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.var = var
        self.app = app
        self.callback = callback

        # Checkbox
        self.checkbox = ctk.CTkCheckBox(
            self,
            text=app["name"],
            variable=var,
            font=("Helvetica", 10),
            onvalue=True,
            offvalue=False,
            command=self._on_checkbox_changed,
        )
        self.checkbox.pack(anchor="w", padx=10, pady=4, fill="x")

    def _on_checkbox_changed(self):
        """Called when checkbox state changes."""
        if self.callback:
            self.callback()


class SetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.shells_list = None
        self.shells_collapsible = None
        self.app_vars = None
        self.app_collapsible_sections = None
        self.shell_vars = None
        self.title("Dev Environment Setup")
        self.geometry("750x650")
        self.resizable(True, True)
        self.minsize(600, 500)

        # Mode detection
        self.online_mode = internet_on(url=config.APPS_JSON_URL)
        mode_text = "🌐 ONLINE" if self.online_mode else "💾 LOCAL"

        # ===== HEADER =====
        self.create_header(mode_text)

        # ===== MAIN CONTENT =====
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            main_container,
            text="Select applications and shells to install",
            font=("Helvetica", 11),
            text_color="gray",
        )
        self.status_label.pack(pady=(0, 15))

        # ===== TABS =====
        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.pack(fill="both", expand=True)

        # Tab 1: Applications
        self.apps_tab = self.tabview.add("📦 Applications")
        self.setup_apps_tab()

        # Tab 2: Shells
        self.shells_tab = self.tabview.add("🐚 Shells")
        self.setup_shells_tab()

        # Tab 3: Quick Actions
        self.quick_tab = self.tabview.add("⚡ Quick Actions")
        self.setup_quick_tab()

        # ===== FOOTER =====
        self.create_footer()

    def create_header(self, mode_text: str):
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color="gray20", corner_radius=0)
        header_frame.pack(fill="x", side="top")

        content = ctk.CTkFrame(header_frame, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left,
            text="🚀 Dev Environment Setup",
            font=("Helvetica", 22, "bold"),
            text_color="white",
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Install apps and configure shells with ease",
            font=("Helvetica", 10),
            text_color="gray",
        ).pack(anchor="w", pady=(5, 0))

        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        mode_color = "#4CAF50" if self.online_mode else "#FFC107"
        ctk.CTkLabel(
            right,
            text=mode_text,
            font=("Helvetica", 11, "bold"),
            text_color=mode_color,
            fg_color="gray30",
            padx=12,
            pady=6,
            corner_radius=6,
        ).pack()

    def create_footer(self):
        """Create footer with action buttons."""
        footer_frame = ctk.CTkFrame(self, fg_color="gray20", corner_radius=0)
        footer_frame.pack(fill="x", side="bottom")

        content = ctk.CTkFrame(footer_frame, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=12)

        ctk.CTkButton(
            content,
            text="Exit",
            command=self.quit,
            width=100,
            height=35,
            fg_color="gray30",
            hover_color="gray25",
            font=("Helvetica", 10, "bold"),
        ).pack(side="right", padx=5)

    def setup_apps_tab(self):
        """Setup applications tab with collapsible sections."""
        try:
            apps = load_apps(self.online_mode)

            # Create scrollable frame
            scroll_frame = ctk.CTkScrollableFrame(
                self.apps_tab, fg_color="transparent"
            )
            scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

            self.app_vars = {}
            self.app_collapsible_sections = {}

            # Group apps by section
            sections_dict = {}
            for app in apps:
                if app.get("is_section_toggle"):
                    continue
                section = app["section"]
                if section not in sections_dict:
                    sections_dict[section] = []
                sections_dict[section].append(app)

            # Create collapsible sections
            for section_name, section_apps in sections_dict.items():
                collapsible = CollapsibleFrame(
                    scroll_frame,
                    title=section_name,
                    fg_color="gray30",
                    corner_radius=8,
                )
                collapsible.pack(fill="x", padx=0, pady=5)

                self.app_collapsible_sections[section_name] = {
                    "frame": collapsible,
                    "apps": section_apps,
                }

                # Add checkboxes to collapsible frame
                content = collapsible.get_content_frame()

                for app in section_apps:
                    var = ctk.BooleanVar(value=False)
                    self.app_vars[app["id"]] = var

                    checkbox_frame = AppCheckboxFrame(
                        content,
                        app,
                        var,
                        callback=self._update_app_counter,
                        corner_radius=6,
                    )
                    checkbox_frame.pack(fill="x", padx=5, pady=2)

                # Update count
                collapsible.update_count(0, len(section_apps))

            # Install button
            button_frame = ctk.CTkFrame(self.apps_tab, fg_color="transparent")
            button_frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkButton(
                button_frame,
                text="📥 Install Selected Applications",
                command=self.install_selected_apps,
                height=45,
                font=("Helvetica", 12, "bold"),
                fg_color="#4CAF50",
                hover_color="#45a049",
                corner_radius=8,
            ).pack(fill="x")

        except Exception as e:
            ctk.CTkLabel(
                self.apps_tab,
                text=f"Error loading apps: {str(e)}",
                text_color="red",
            ).pack(pady=20)

    def _update_app_counter(self):
        """Update app section counters."""
        for section_name, section_data in self.app_collapsible_sections.items():
            section_apps = section_data["apps"]
            collapsible = section_data["frame"]

            # Count selected items in this section
            selected_count = sum(
                1 for app in section_apps
                if self.app_vars.get(app["id"], ctk.BooleanVar()).get()
            )

            collapsible.update_count(selected_count, len(section_apps))

    def setup_shells_tab(self):
        """Setup shells tab with collapsible sections."""
        try:
            shells_data = load_shells(self.online_mode)

            # Handle different data formats
            if isinstance(shells_data, dict) and "shells" in shells_data:
                shells = shells_data["shells"]
            else:
                shells = shells_data

            # Filter visible shells
            shells = [s for s in shells if not s.get("hidden", False)]

            # Create scrollable frame
            scroll_frame = ctk.CTkScrollableFrame(
                self.shells_tab, fg_color="transparent"
            )
            scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

            self.shell_vars = {}

            # Create single collapsible section
            collapsible = CollapsibleFrame(
                scroll_frame,
                title="Terminal and Shells",
                fg_color="gray30",
                corner_radius=8,
            )
            collapsible.pack(fill="x", padx=0, pady=5)

            self.shells_collapsible = collapsible
            self.shells_list = shells

            content = collapsible.get_content_frame()

            for shell in shells:
                if shell.get("id") == "all":
                    continue

                var = ctk.BooleanVar(value=False)
                self.shell_vars[shell["id"]] = var

                # Shell item frame
                item_frame = ctk.CTkFrame(content, fg_color="gray25",
                                          corner_radius=6)
                item_frame.pack(fill="x", padx=5, pady=4)

                # Checkbox with callback
                checkbox = ctk.CTkCheckBox(
                    item_frame,
                    text=shell["name"],
                    variable=var,
                    font=("Helvetica", 10),
                    command=self._update_shell_counter,
                )
                checkbox.pack(anchor="w", padx=10, pady=(8, 0))

                # Description
                if "description" in shell:
                    ctk.CTkLabel(
                        item_frame,
                        text=shell["description"],
                        font=("Helvetica", 9),
                        text_color="gray",
                    ).pack(anchor="w", padx=30, pady=(0, 8))

            collapsible.update_count(0, len(shells))

            # Configure button
            button_frame = ctk.CTkFrame(self.shells_tab, fg_color="transparent")
            button_frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkButton(
                button_frame,
                text="⚙️ Configure Selected Shells",
                command=self.configure_selected_shells,
                height=45,
                font=("Helvetica", 12, "bold"),
                fg_color="#2196F3",
                hover_color="#0b7dda",
                corner_radius=8,
            ).pack(fill="x")

        except Exception as e:
            ctk.CTkLabel(
                self.shells_tab,
                text=f"Error loading shells: {str(e)}",
                text_color="red",
            ).pack(pady=20)

    def _update_shell_counter(self):
        """Update shell section counter."""
        selected_count = sum(
            1 for shell_id, var in self.shell_vars.items() if var.get()
        )
        self.shells_collapsible.update_count(
            selected_count, len(self.shells_list)
        )

    def setup_quick_tab(self):
        """Quick action buttons."""
        container = ctk.CTkFrame(self.quick_tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text="One-Click Setup",
            font=("Helvetica", 18, "bold"),
        ).pack(pady=20)

        # Buttons
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="both", expand=True)

        ctk.CTkButton(
            button_frame,
            text="🔧 Install winget",
            command=self.run_install_winget,
            height=55,
            font=("Helvetica", 12, "bold"),
            fg_color="gray30",
            hover_color="gray25",
            corner_radius=8,
        ).pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="⚡ Run ALL Steps",
            command=self.run_all_steps,
            height=55,
            font=("Helvetica", 12, "bold"),
            fg_color="#FF6B35",
            hover_color="#FF5722",
            corner_radius=8,
        ).pack(fill="x", pady=10)

        # Info
        info_frame = ctk.CTkFrame(container, fg_color="gray25",
                                  corner_radius=8)
        info_frame.pack(fill="x", pady=30)

        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Run ALL will:",
            font=("Helvetica", 11, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            info_frame,
            text="• Install winget\n• Install all selected apps\n• Configure all shells",
            font=("Helvetica", 10),
            text_color="gray",
            justify="left",
        ).pack(anchor="w", padx=25, pady=(0, 10))

    def install_selected_apps(self):
        """Thread-safe app installation."""
        selected = [
            app_id for app_id, var in self.app_vars.items() if var.get()
        ]

        if not selected:
            self.show_error("Please select at least one app!")
            return

        thread = threading.Thread(
            target=self._install_apps_worker, args=(selected,)
        )
        thread.daemon = True
        thread.start()

    def _install_apps_worker(self, selected_ids: List[str]):
        """Background worker for app installation."""
        try:
            self.status_label.configure(
                text="⏳ Installing apps... (check terminal)"
            )

            apps = load_apps(self.online_mode)
            selected_apps = [
                a for a in apps
                if a["id"] in selected_ids and not a.get("is_section_toggle")
            ]

            install_apps(selected_apps)
            self.status_label.configure(
                text="✅ Apps installed successfully!",
                text_color="green"
            )

        except Exception as e:
            self.status_label.configure(
                text=f"❌ Error: {str(e)}", text_color="red"
            )

    def configure_selected_shells(self):
        """Thread-safe shell configuration."""
        selected = [
            shell_id for shell_id, var in self.shell_vars.items()
            if var.get()
        ]

        if not selected:
            self.show_error("Please select at least one shell!")
            return

        thread = threading.Thread(
            target=self._configure_shells_worker, args=(selected,)
        )
        thread.daemon = True
        thread.start()

    def _configure_shells_worker(self, selected_ids: List[str]):
        """Background worker for shell configuration."""
        try:
            self.status_label.configure(
                text="⏳ Configuring shells... (check terminal)"
            )

            for shell_id in selected_ids:
                configure_shell(shell_id)

            self.status_label.configure(
                text="✅ Shells configured successfully!",
                text_color="green"
            )

        except Exception as e:
            self.status_label.configure(
                text=f"❌ Error: {str(e)}", text_color="red"
            )

    def run_install_winget(self):
        """Install winget in background."""
        thread = threading.Thread(target=install_winget)
        thread.daemon = True
        thread.start()
        self.status_label.configure(text="⏳ Installing winget...")

    def run_all_steps(self):
        """Run all setup steps in background."""
        thread = threading.Thread(target=self._all_steps_worker)
        thread.daemon = True
        thread.start()

    def _all_steps_worker(self):
        """Background worker for all steps."""
        try:
            self.status_label.configure(text="⏳ Running all steps...")

            install_winget()
            apps = load_apps(self.online_mode)
            install_apps([a for a in apps if not a.get("is_section_toggle")])

            shells_data = load_shells(self.online_mode)
            if isinstance(shells_data, dict) and "shells" in shells_data:
                shells = shells_data["shells"]
            else:
                shells = shells_data

            for shell in shells:
                if not shell.get("hidden") and shell.get("id") != "all":
                    configure_shell(shell["id"])

            self.status_label.configure(
                text="✅ All steps completed!",
                text_color="green"
            )

        except Exception as e:
            self.status_label.configure(
                text=f"❌ Error: {str(e)}", text_color="red"
            )

    def show_error(self, message: str):
        """Show error popup."""
        error_window = ctk.CTkToplevel(self)
        error_window.title("⚠️ Warning")
        error_window.geometry("350x150")
        error_window.resizable(False, False)
        error_window.attributes("-topmost", True)

        ctk.CTkLabel(
            error_window,
            text=message,
            font=("Helvetica", 12),
            text_color="orange",
        ).pack(pady=20)

        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=100,
        ).pack(pady=10)


def run_gui():
    """Launch the GUI."""
    app = SetupApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()