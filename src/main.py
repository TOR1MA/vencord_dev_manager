import gui
import functions as func
from customtkinter import set_appearance_mode, set_default_color_theme

if __name__ == '__main__':
    set_appearance_mode("dark")
    set_default_color_theme("dark-green.json")

    deps = func.check_dependencies()
    if not all(deps.values()):
        deps_window = gui.MissingDependenciesTab(deps)
        deps_window.mainloop()
        if not deps_window.success:
            exit()

    config = func.load_config("config.json")

    app = gui.App(config)
    app.mainloop()
