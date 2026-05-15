import subprocess
import pathlib
import json
from os import chmod
from stat import S_IWRITE
from webbrowser import open as webbrowser_open
from shutil import copytree, rmtree
from tempfile import mkdtemp

DEPENDENCIES_URLS = {
    "git": "https://git-scm.com/downloads",
    "node": "https://nodejs.org/en/download/",
    "pnpm": "https://pnpm.io/installation"
}

DEFAULT_CONFIG = {
    "vencord_installation_path": "",
    "discord_path": "",
    "discord_branch": ""
}

DEFAULT_VENCORD_INSTALLATION_PATH = str(pathlib.Path.home() / "Documents")


def save_config(config_path, config):
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def load_config(config_path):
    if not pathlib.Path(config_path).exists():
        save_config(config_path, DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(config_path, "r") as f:
        return json.load(f)


def run_command(command, cwd, callback=print):
    process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")

    for line in process.stdout:
        callback(line.rstrip())

    process.wait()
    return process.returncode


def remove_readonly(func, path, exc):
    chmod(path, S_IWRITE)
    func(path)


def validate_path(text, path, callback):
    if not path:
        callback(f"Error: {text} path is not set.")
        return False
    if not pathlib.Path(path).exists():
        callback(f"Error: Path '{path}' does not exist.")
        return False
    return True


def check_dependencies():
    dependencies = ["git", "node", "pnpm"]
    checked_deps = {}
    for dep in dependencies:
        result = subprocess.run([dep, "--version"], shell=True, capture_output=True)
        checked_deps[dep] = result.returncode == 0
    return checked_deps


def download_dependencies(missing_deps):
    for dep, available in missing_deps.items():
        if not available:
            webbrowser_open(DEPENDENCIES_URLS[dep])


def install_vencord(vencord_installation_path, branch, callback, discord_path=None):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    if branch == "custom" and not validate_path("Discord", discord_path, callback):
        return
    vencord_folder = pathlib.Path(vencord_installation_path) / "Vencord"
    run_command("git clone https://github.com/Vendicated/Vencord.git", cwd=vencord_installation_path,
                callback=callback)
    run_command("npm i -g pnpm", cwd=vencord_folder, callback=callback)
    run_command("pnpm i", cwd=vencord_folder, callback=callback)
    run_command("pnpm build", cwd=vencord_folder, callback=callback)
    (vencord_folder / "src" / "userplugins").mkdir(parents=True, exist_ok=True)
    if branch == 'custom':
        run_command(f"node scripts/runInstaller.mjs -- --install --location {discord_path}", cwd=vencord_folder,
                    callback=callback)
    else:
        run_command(f"node scripts/runInstaller.mjs -- --install --branch {branch}", cwd=vencord_folder,
                    callback=callback)
    config = {
        "vencord_installation_path": str(vencord_installation_path),
        "discord_path": discord_path if discord_path else "",
        "discord_branch": branch
    }
    save_config("config.json", config)


def repair_vencord(vencord_installation_path, branch, callback, discord_path=None):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    if branch == "custom" and not validate_path("Discord", discord_path, callback):
        return
    vencord_folder = pathlib.Path(vencord_installation_path) / "Vencord"
    if branch == 'custom':
        run_command(f"node scripts/runInstaller.mjs -- --repair --location {discord_path}", cwd=vencord_folder,
                    callback=callback)
    else:
        run_command(f"node scripts/runInstaller.mjs -- --repair --branch {branch}", cwd=vencord_folder,
                    callback=callback)


def uninstall_vencord(vencord_installation_path, branch, callback, discord_path=None):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    if branch == "custom" and not validate_path("Discord", discord_path, callback):
        return
    vencord_folder = pathlib.Path(vencord_installation_path) / "Vencord"
    if branch == 'custom':
        run_command(f"node scripts/runInstaller.mjs -- --uninstall --location {discord_path}", cwd=vencord_folder,
                    callback=callback)
    else:
        run_command(f"node scripts/runInstaller.mjs -- --uninstall --branch {branch}", cwd=vencord_folder,
                    callback=callback)
    rmtree(pathlib.Path(vencord_installation_path) / "Vencord", onexc=remove_readonly)


def reinstall_vencord(vencord_installation_path, branch, callback, discord_path=None):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    if branch == "custom" and not validate_path("Discord", discord_path, callback):
        return
    plugins_folder = pathlib.Path(vencord_installation_path) / "Vencord" / "src" / "userplugins"
    temp_dir = mkdtemp()
    copytree(plugins_folder, temp_dir, dirs_exist_ok=True)
    uninstall_vencord(vencord_installation_path, branch, callback, discord_path)
    install_vencord(vencord_installation_path, branch, callback, discord_path)
    copytree(temp_dir, plugins_folder, dirs_exist_ok=True)
    rmtree(temp_dir, onexc=remove_readonly)
    build_vencord(vencord_installation_path, callback)


def build_vencord(vencord_installation_path, callback):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    vencord_folder = pathlib.Path(vencord_installation_path) / "Vencord"
    run_command("pnpm build", cwd=vencord_folder, callback=callback)


def install_plugin(plugin_link, vencord_installation_path, callback, on_complete=None):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    plugins_path = pathlib.Path(vencord_installation_path) / "Vencord" / "src" / "userplugins"
    run_command(f"git clone {plugin_link}", cwd=plugins_path, callback=callback)
    if on_complete:
        on_complete()


def get_installed_plugins(vencord_installation_path):
    plugins_path = pathlib.Path(vencord_installation_path) / "Vencord" / "src" / "userplugins"
    if not plugins_path.exists():
        return []
    return [folder.name for folder in plugins_path.iterdir() if folder.is_dir()]


def update_plugins(vencord_installation_path, callback):
    if not validate_path("Vencord installation", vencord_installation_path, callback):
        return
    plugins_path = pathlib.Path(vencord_installation_path) / "Vencord" / "src" / "userplugins"
    for folder in plugins_path.iterdir():
        if folder.is_dir():
            run_command("git pull", cwd=folder, callback=callback)


def install_theme(theme_link, callback, on_complete=None):
    themes_path = str(pathlib.Path.home() / "AppData" / "Roaming" / "Vencord" / "themes")
    run_command(f"curl {theme_link} -O", cwd=themes_path, callback=callback)
    if on_complete:
        on_complete()


def get_installed_themes():
    themes_path = pathlib.Path.home() / "AppData" / "Roaming" / "Vencord" / "themes"
    if not themes_path.exists():
        return []
    return [file.name for file in themes_path.iterdir() if file.is_file()]
