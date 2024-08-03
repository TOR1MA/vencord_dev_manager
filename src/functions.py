import os
# import shutil
import json
vencord_dev_manager = os.getcwd()


# Установка венкорда
def install_vencord(config):
    vencord_installation_folder_raw = str(input('Choose folder to install Vencord:\n'))
    vencord_installation_folder = ''
    for char in vencord_installation_folder_raw:
        vencord_installation_folder += char.replace('\\', '/')
    os.chdir(vencord_installation_folder)
    os.system("git clone https://github.com/Vendicated/Vencord.git")
    os.chdir("./Vencord")
    os.system("npm i -g pnpm")
    os.system("pnpm i")
    os.system("pnpm build")
    os.system("pnpm inject")
    os.chdir('./src')
    os.mkdir('userplugins')
    os.chdir(vencord_dev_manager)
    vencord_folder = vencord_installation_folder + '/Vencord'
    config['vencord_folder'] = vencord_folder
    config['vencord_userplugins_folder'] = vencord_folder + '/src/userplugins'
    config['vencord_folder_i'] = True
    config['vencord_installed'] = True
    return config

# Выбор папки с венкордом
def select_vencord_folder(config):
    exit = False
    while not exit:
        user_input = input('Enter a vencord root folder or exit:\n')
        if user_input == 'exit':
            selector(config)
        if not os.path.isdir(user_input) or not os.path.isdir(os.path.join(user_input, "src")):
            print("Specified path is invalid (does not exist or is not a directory)")
            continue
        vencord_folder = user_input.replace('\\', '/')
        config['vencord_userplugins_folder'] = vencord_folder + '/src/userplugins'
        config['vencord_folder'] = vencord_folder
        config['vencord_folder_i'] = True
        return config


# Селектор
def selector(config):
    while True:
        selector = (input('1. Manage Vencord | 2. Plugins | 3. Install themes | 4. Build | 0. Exit:\n'))
        if selector.isdigit() and int(selector) < 5 or int(selector) == 0:
            match int(selector):
                case 1:
                    manage_vencord(config)
                case 2:
                    plugins_selector(config)
                case 3:
                    install_themes(config)
                case 4:
                    vencord_build(config)
                case 0:
                    os.chdir(vencord_dev_manager)
                    config = json.dumps(config)
                    with open('config.json', 'w') as f:
                        f.write(config)
                    SystemExit
            break
        elif selector.isalpha():
            print(f"{selector} is not a number")
        else:
            print(f'{selector} is not a selector menu')

# 1. Запуск менеджера
def manage_vencord(config):
    manage_selector = str(input('1. Vencord Installer | 2. Select another vencord folder | Other symbol - Return:\n'))
    match manage_selector:
        case '1':
            os.chdir(config['vencord_folder'])
            os.system('pnpm inject')
        case '2':
            select_vencord_folder(config)
    selector(config)


# 2. Плагины
def plugins_selector(config):
    plugins_selector = str(input('1. Install plugin by link | 2. Update all plugins | 3. Install dev favorite plugins | 4. List of installed plugins | Other symbol - Return:\n'))
    match plugins_selector:
        case '1':
            plugin_link = input('Enter a github link or any symbol to return:\n')
            if plugin_link[0] == 'h':
                os.chdir(config['vencord_userplugins_folder'])
                os.system(f'git clone {plugin_link}')
            else:
                selector(config)
        case '2':
            for folder in os.listdir(config['vencord_userplugins_folder']):
                os.chdir(config['vencord_userplugins_folder'] + f'/{folder}')
                os.system('git pull')
        case '3':
            os.chdir(config['vencord_userplugins_folder'])
            os.system('git clone https://github.com/TOR1MA/vc-move-everyone')
            os.system('git clone https://github.com/Syncxv/vc-message-logger-enhanced')
            os.system('git clone https://github.com/Syncxv/vc-gif-collections')
            os.system('git clone https://github.com/nyakowint/replaceActivityTypes')
            os.system('git clone https://github.com/D3SOX/vc-betterActivities')
            os.mkdir('findReply')
            os.chdir('./findReply')
            os.system('curl https://raw.githubusercontent.com/waresnew/Vencord/findreply/src/plugins/findReply/index.tsx -O')
            os.system('curl https://raw.githubusercontent.com/waresnew/Vencord/findreply/src/plugins/findReply/ReplyNavigator.tsx -O')
            os.system('curl https://raw.githubusercontent.com/waresnew/Vencord/findreply/src/plugins/findReply/styles.css -O')
        case '4':
            os.chdir(config['vencord_userplugins_folder'])
            list = os.listdir(config['vencord_userplugins_folder'])
            for plugin in list:
                print(plugin)
    selector(config)


# 3. Установка тем
def install_themes(config):
    theme_link = input('Enter a link to raw file or any symbol to return:\n')
    if theme_link[0] == 'h':
        os.chdir(os.environ['USERPROFILE'] + '/AppData/Roaming/Vencord/themes')
        os.system(f'curl {theme_link} -O')
    selector(config)


# 4. Билд венкорда
def vencord_build(config):
    os.chdir(config['vencord_folder'])
    os.system('pnpm build')
    selector(config)
# 6. Удаление папки венкорда
# def delete_vencord(config):
#     delete_confirm = input('Type "delete folder" to confirm deletion (' + config['vencord_folder'] + '):\n')
#     if delete_confirm.lower() == 'delete folder':
#         shutil.rmtree(config['vencord_folder'])
#     selector(config)
