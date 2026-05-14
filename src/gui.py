import customtkinter as ctk
import functions as func


def log_callback(master):
    return master.winfo_toplevel().log_tab.append_log


class EntryWithButton(ctk.CTkFrame):
    def __init__(self, master, placeholder="placeholder", button_text="text"):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.button = ctk.CTkButton(self, width=60, text=button_text)
        self.button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    def get(self):
        return self.entry.get()


class PathEntry(EntryWithButton):
    def __init__(self, master, default_path='', placeholder="placeholder", checkbox_text="text", checkbox=True):
        super().__init__(master, button_text="Browse", placeholder=placeholder)

        def set_path():
            path = ctk.filedialog.askdirectory()
            if path:
                self.entry.set(path)

        def toggle_path_entry():
            if self.default_path_checkbox.get():
                self.entry.set(default_path)
                self.entry.configure(state="disabled")
                self.button.configure(state="disabled")
            else:
                self.entry.configure(state="normal")
                self.entry.delete(0, "end")
                self.button.configure(state="normal")

        self.button.configure(command=set_path)
        if checkbox:
            self.default_path_checkbox = ctk.CTkCheckBox(self, text=checkbox_text, command=toggle_path_entry)
            self.default_path_checkbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")


class URLEntry(EntryWithButton):
    def __init__(self, master, placeholder="placeholder"):
        super().__init__(master, button_text="Install", placeholder=placeholder)


class ManageVencordTab(ctk.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master)
        self.vencord_installation_path = config["vencord_installation_path"]
        self.discord_path_config = config["discord_path"]
        self.discord_branch = config["discord_branch"]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.vencord_path = PathEntry(
            self,
            default_path=self.vencord_installation_path,
            placeholder=self.vencord_installation_path,
            checkbox_text="Use default path for Vencord")
        self.vencord_path.grid(row=0, column=0, sticky="ew")

        # Function to show/hide the custom path entry based on the branch selection
        def get_branch(choice):
            if choice == "Custom":
                self.discord_path.grid(row=1, column=0, sticky="ew")
            else:
                self.discord_path.grid_forget()

        # Frame for branch selection and custom path entry
        self.branch_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.branch_selector_frame.grid(row=1, column=0, sticky="ew")
        self.branch_selector_frame.grid_columnconfigure(0, weight=1)
        self.branch_selection_var = ctk.StringVar(value="Stable")
        self.branch_selection = ctk.CTkOptionMenu(self.branch_selector_frame, values=["Stable", "PTB", "Canary",
                                                                                      "Custom"],
                                                  width=150, variable=self.branch_selection_var, command=get_branch)
        self.branch_selection.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.discord_path = PathEntry(self.branch_selector_frame, placeholder="C:/Users/Username/AppData/Local/Discord",
                                      checkbox=False)

        # Frame for install, repair and uninstall buttons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=2, column=0, columnspan=3, sticky="sew")
        self.buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.install_button = ctk.CTkButton(self.buttons_frame, text="Install", width=110,
                                            command=lambda: func.install_vencord(
                                                vencord_installation_path=self.vencord_path.get(),
                                                branch=self.branch_selection_var.get().lower(),
                                                callback=log_callback(self),
                                                discord_path=self.discord_path.get()))
        self.install_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.repair_button = ctk.CTkButton(self.buttons_frame, text="Repair", width=110,
                                           command=lambda: func.repair_vencord(
                                               vencord_installation_path=self.vencord_path.get(),
                                               branch=self.branch_selection_var.get().lower(),
                                               callback=log_callback(self),
                                               discord_path=self.discord_path.get()))
        self.repair_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.reinstall_button = ctk.CTkButton(self.buttons_frame, text="Reinstall", width=110,
                                              command=lambda: func.reinstall_vencord(
                                               vencord_installation_path=self.vencord_path.get(),
                                               branch=self.branch_selection_var.get().lower(),
                                               callback=log_callback(self),
                                               discord_path=self.discord_path.get()))
        self.reinstall_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.uninstall_button = ctk.CTkButton(self.buttons_frame, text="Uninstall", width=110,
                                              command=lambda: func.uninstall_vencord(
                                               vencord_installation_path=self.vencord_path.get(),
                                               branch=self.branch_selection_var.get().lower(),
                                               callback=log_callback(self),
                                               discord_path=self.discord_path.get()))
        self.uninstall_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        if self.discord_branch ==  "custom":
            self.branch_selection_var.set("Custom")
            self.discord_path.grid(row=1, column=0, sticky="ew")
            if self.discord_path_config:
                self.discord_path.entry.set(self.discord_path_config)


class PluginsTab(ctk.CTkFrame):
    def __init__(self, master, vencord_installation_path):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        def refresh_plugins_list():
            plugins = func.get_installed_plugins(vencord_installation_path)
            self.plugins_listbox.configure(state="normal")
            self.plugins_listbox.delete("1.0", "end")
            if plugins:
                for plugin in plugins:
                    self.plugins_listbox.insert("end", f"- {plugin}\n")
            else:
                self.plugins_listbox.insert("end", "No plugins installed.")
            self.plugins_listbox.configure(state="disabled")

        self.link_entry_plugin = URLEntry(self, placeholder="Plugin URL")
        self.link_entry_plugin.button.configure(text="Install", command=lambda: func.install_plugin(
            plugin_link=self.link_entry_plugin.get(), callback=log_callback(self),
            vencord_installation_path=vencord_installation_path, on_complete=refresh_plugins_list))
        self.link_entry_plugin.grid(row=0, column=0, sticky="ew")

        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)
        self.update_plugins_button = ctk.CTkButton(self.buttons_frame, text="Update all plugins", command=lambda: func.update_plugins(
            vencord_installation_path=vencord_installation_path, callback=log_callback(self)))
        self.update_plugins_button.grid(row=0, column=0, sticky="ew")
        self.build_button = ctk.CTkButton(self.buttons_frame, text="Build Vencord", command=lambda: func.build_vencord(
            vencord_installation_path=vencord_installation_path, callback=log_callback(self)))
        self.build_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.plugins_listbox_label = ctk.CTkLabel(self, text="Installed plugins:")
        self.plugins_listbox_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        self.plugins_listbox = ctk.CTkTextbox(self, width=350, height=100, state="disabled")
        self.plugins_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        refresh_plugins_list()


class ThemesTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        def refresh_themes_list():
            themes = func.get_installed_themes()
            self.themes_listbox.configure(state="normal")
            self.themes_listbox.delete("1.0", "end")
            if themes:
                for theme in themes:
                    self.themes_listbox.insert("end", f"- {theme}\n")
            else:
                self.themes_listbox.insert("end", "No themes installed.")
            self.themes_listbox.configure(state="disabled")

        self.link_entry_themes = URLEntry(self, placeholder="Theme URL")
        self.link_entry_themes.button.configure(text="Install", command=lambda: func.install_theme(
            theme_link=self.link_entry_themes.get(), callback=log_callback(self), on_complete=refresh_themes_list))
        self.link_entry_themes.grid(row=0, column=0, sticky="ew")
        self.themes_listbox_label = ctk.CTkLabel(self, text="Installed themes:")
        self.themes_listbox_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        self.themes_listbox = ctk.CTkTextbox(self, width=350, height=100, state="disabled")
        self.themes_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        refresh_themes_list()


class Tabview(ctk.CTkTabview):
    def __init__(self, master, config):
        super().__init__(master)

        self.add("Manage Vencord")
        self.add("Plugins")
        self.add("Themes")
        ManageVencordTab(self.tab("Manage Vencord"), config).pack(fill="both", expand=True)
        PluginsTab(self.tab("Plugins"), config["vencord_installation_path"]).pack(fill="both", expand=True)
        ThemesTab(self.tab("Themes")).pack(fill="both", expand=True)


class LogTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        def toggle_log():
            if self.log_textbox.winfo_ismapped():
                self.log_textbox.grid_forget()
                self.log_button.configure(text="▲Log")
            else:
                self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew", columnspan=2)
                self.log_button.configure(text="▼Log")

        self.log_label = ctk.CTkLabel(self, text="Status:")
        self.log_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.log_button = ctk.CTkButton(self, text="▲Log", width=60, command=toggle_log)
        self.log_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.log_textbox = ctk.CTkTextbox(self, state="disabled", height=120)

    def set_status(self, text):
        self.log_label.configure(text=f"Status: {text}")

    def append_log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")


class MissingDependenciesTab(ctk.CTk):
    def __init__(self, missing_deps):
        super().__init__()
        self.success = False

        self.grid_columnconfigure(0, weight=1)

        def set_dependency_list(missing_deps, recheck=False):
            if recheck:
                missing_deps = func.check_dependencies()
                if all(missing_deps.values()):
                    self.success = True
                    self.destroy()
                    return
            for dep in missing_deps:
                self.deps_listbox.configure(state="normal")
                self.deps_listbox.delete("1.0", "end")
                if missing_deps[dep]:
                    self.deps_listbox.insert("end", f"- {dep} ✅\n")
                else:
                    self.deps_listbox.insert("end", f"- {dep} ❌\n")
            self.deps_listbox.configure(state="disabled")

        self.label = ctk.CTkLabel(self, text="Missing dependencies:")
        self.label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.deps_listbox = ctk.CTkTextbox(self, width=350, height=100, state="disabled")
        self.deps_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        set_dependency_list(missing_deps)
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=2, column=0, columnspan=3, sticky="sew")
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)
        self.download_button = ctk.CTkButton(self.buttons_frame, text="Download", width=110,
                                             command=lambda: func.download_dependencies(missing_deps))
        self.download_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.retry_button = ctk.CTkButton(self.buttons_frame, text="Retry", width=110,
                                          command=lambda: set_dependency_list(missing_deps, recheck=True))
        self.retry_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")


class App(ctk.CTk):
    def __init__(self, config):
        super().__init__()

        self.title("Vencord Dev Manager")
        self.geometry("425x365")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.minsize(425, 400)

        self.tabview_1 = Tabview(self, config)
        self.tabview_1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        self.log_tab = LogTab(self)
        self.log_tab.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
