import json
import subprocess
import functions
import os


config_status = os.path.isfile('./config.json')
if config_status is False:
    with open('config.json', 'x') as f:
        f.write('{"vencord_installed": false, "vencord_folder_i": false, "vencord_folder": "", "vencord_userplugins_folder": ""}')
try:
    subprocess.call(["git", "--version"])
except FileNotFoundError:
    print('git is not installed, you can install it from here: https://git-scm.com/download/win')
try:
    subprocess.call(["node", "--version"])
except FileNotFoundError:
    print('Node.js is not installed, you can install it from here: https://nodejs.org/en')

with open('config.json') as f:
    config = json.load(f)

if config['vencord_installed'] is False:
    vencord_installed = str(input('Do you have Vencord dev installed?\ny/n: '))
    if vencord_installed == 'y':
        config['vencord_installed'] = True
    elif vencord_installed == 'n':
        functions.install_vencord(config)

if config['vencord_folder_i'] is False:
    functions.select_vencord_folder(config)

functions.selector(config)
