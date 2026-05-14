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
    "vencord_installation_path": str(pathlib.Path.home() / "Documents"),
    "discord_path": "",
    "discord_branch": "stable"
}


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
    vencord_folder = pathlib.Path(vencord_installation_path) / "Vencord"
    vencord_cli_path = pathlib.Path(vencord_installation_path) / "Vencord" / "dist" / "Installer"
    run_command("git clone https://github.com/Vendicated/Vencord.git", cwd=vencord_installation_path,
                callback=callback)
    run_command("npm i -g pnpm", cwd=vencord_folder, callback=callback)
    run_command("pnpm i", cwd=vencord_folder, callback=callback)
    run_command("pnpm build", cwd=vencord_folder, callback=callback)
    (vencord_folder / "src" / "userplugins").mkdir(parents=True, exist_ok=True)
    if branch == 'custom':
        run_command(f"VencordInstallerCli.exe -location {discord_path} -install", cwd=vencord_cli_path,
                    callback=callback)
    else:
        run_command(f"VencordInstallerCli.exe -branch {branch} -install", cwd=vencord_cli_path, callback=callback)
    config = {
        "vencord_installation_path": str(vencord_installation_path),
        "discord_path": discord_path if discord_path else "",
        "discord_branch": branch
    }
    save_config("config.json", config)


def repair_vencord(vencord_installation_path, branch, callback, discord_path=None):
    vencord_cli_path = pathlib.Path(vencord_installation_path) / "Vencord" / "dist" / "Installer"
    if branch == 'custom':
        run_command(f"VencordInstallerCli.exe -location {discord_path} -repair", cwd=vencord_cli_path,
                    callback=callback)
    else:
        run_command(f"VencordInstallerCli.exe -branch {branch} -repair", cwd=vencord_cli_path, callback=callback)


def uninstall_vencord(vencord_installation_path, branch, callback, discord_path=None):
    vencord_cli_path = pathlib.Path(vencord_installation_path) / "Vencord" / "dist" / "Installer"
    if branch == 'custom':
        run_command(f"VencordInstallerCli.exe -location {discord_path} -uninstall", cwd=vencord_cli_path,
                    callback=callback)
    else:
        run_command(f"VencordInstallerCli.exe -branch {branch} -uninstall", cwd=vencord_cli_path, callback=callback)
    rmtree(pathlib.Path(vencord_installation_path) / "Vencord", onexc=remove_readonly)


def reinstall_vencord(vencord_installation_path, branch, callback, discord_path=None):
    plugins_folder = pathlib.Path(vencord_installation_path) / "Vencord" / "src" / "userplugins"
    temp_dir = mkdtemp()
    copytree(plugins_folder, temp_dir, dirs_exist_ok=True)
    uninstall_vencord(vencord_installation_path, branch, callback, discord_path)
    install_vencord(vencord_installation_path, branch, callback, discord_path)
    copytree(temp_dir, plugins_folder, dirs_exist_ok=True)
    rmtree(temp_dir, onexc=remove_readonly)


def build_vencord(vencord_installation_path, callback):
    vencord_folder = pathlib.Path(vencord_installation_path) / "Vencord"
    run_command("pnpm build", cwd=vencord_folder, callback=callback)


def install_plugin(plugin_link, vencord_installation_path, callback, on_complete=None):
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
