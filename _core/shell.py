import os
import io
import sys
import time
import json
import Disk
import bcrypt
import string
import zipfile
import platform
import requests
from pynput import keyboard


def run(filepath):
    cmd = [
        f"\"{sys.executable}\"", f"\"{filepath}\""
    ]
    os.system(" ".join(cmd))


def generate_help_text():
    global custom_commands
    with open(f"{Disk.disk_name}/commands.cds", "r") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        exit("Traceback (most recent call last):\n  TypeError: commands.cds is not dict styled")
    custom_commands = data

    commands_description = {
        "help": "Prints all the commands",
        "ls": "List directory contents",
        "cd <dir>": "Change directory",
        "mkdir <name>": "Create directory",
        "open <file>": "Edit or create a file (type :wq to save)",
        "cat <file>": "Show file contents",
        "printf <text>": "Prints text",
        "mode <mode>": "Changes the mode. Example: mode GUI",
        "addusr <name> <passwd>": "Adds a user (must be root to add user)",
        "setmode <key> <value>": "Sets the key to value in the settings",
        "cmdadd <cmd>": "Makes a custom command (type :wcmd to save)",
        "nam <option> [package]": "Installs, lists, etc all the Nebula Apps",
        "shutdown": "Shut down NebulaOS"
    }
    command_text = ["", "NebulaOS Restart Commands:"]
    length = max([len(cmd) for cmd, _ in commands_description.items()]) + 2
    for cmd, exp in commands_description.items():
        command_text.append("  " + cmd + (" " * (length - len(cmd))) + "- " + exp)
    custom_commands_des = {}
    custom_commands_text = [""]
    if custom_commands:
        custom_commands_text.append("Custom Commands:")
    for _, data in custom_commands.items():
        custom_commands_des[data["example"]] = data["description"]
    for cmd, exp in custom_commands_des.items():
        custom_commands_text.append("  " + cmd + (" " * (length - len(cmd))) + "- " + exp)
    return "\n".join(command_text) + "\n" + "\n".join(custom_commands_text) + ("\n" if custom_commands else "")


def install_package(package):
    if Disk.exists(f"/Applications/{package}.neap"):
        choice = input(
            f"Package '{package}' already installed. If overwritten would equal updating. Overwrite? (Y/n): ").strip().lower()
        if choice != "y":
            print("Installation aborted by user.")
            return
    base = "https://github.com/ProPythonCoderAya/NamPackages/raw/main"
    url = f"{base}/Packages/{package}.neap.zip"
    print(f"Downloading data from {url} ...")
    try:
        packages = requests.get(f"{base}/packages.json")
        if packages.status_code != 200:
            print(f"Error during retrieving packages.json. Status code: {packages.status_code}")
            return
        packages = eval(packages.content)
        if not package in packages:
            print(f"Package '{package}' not found.")
            return

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error during download. Status code: {response.status_code}")
            return

        print("Extracting zip...")
        dist = f"pkgs/{package}"
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            os.makedirs(dist, exist_ok=True)
            z.extractall(dist)

        error = 0
        if not Disk.exists(f"/Applications/{package}.neap"):
            Disk.create_directory(f"/Applications/{package}.neap")
        else:
            for root, dirs, files in Disk.walk(f"/Applications/{package}.neap", topdown=False):
                print(root, dirs, files)
                # Delete files
                for file in files:
                    Disk.delete_file(file, root)

                # Delete directories
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    Disk.delete_directory(dir_path)
            Disk.list_contents()
        for root, dirs, files in os.walk(dist):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                relative_path = os.path.relpath(dir_path, dist)
                target_path = os.path.join("/Applications", relative_path)
                if not Disk.exists(target_path):
                    Disk.create_directory(target_path)

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, dist)
                target_path = os.path.dirname(os.path.join("/Applications", relative_path))

                # Read the file data
                with open(file_path, "rb") as f:
                    file_data = f.read()

                # Tell the user that it is writing to the disk.
                print(f"Writing '{file}' to disk...")

                # Write the file data to the virtual disk
                if not Disk.write_data_to_disk(file, file_data, target_path, overwrite_ok=True):
                    error = 1
                    break
            if error:
                break
        else:
            print(f"Installed '{package}' successfully!")
            for root, dirs, files in os.walk(dist, topdown=False):
                # Delete files
                for file in files:
                    file_path = os.path.join(root, file)
                    #os.remove(file_path)  # Remove the file

                # Delete directories
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    #os.rmdir(dir_path)  # Remove the directory
            return
        print(f"Could not install package '{package}'")

    except Exception as e:
        print(f"Error installing package: {e}")


if not os.path.exists(Disk.disk_name):
    #sys.stdout = open(os.devnull, "w")
    Disk.format_disk_image()
    Disk.create_directory("/Users")
    Disk.create_directory("/Users/root")
    Disk.create_directory("/Applications")
    install_package("Terminal")
    #sys.stdout = sys.__stdout__
else:
    Disk.load()

global command_text
command_text = generate_help_text()


def check_user_exists(user):
    with open(Disk.disk_name + "/usr.ur") as file:
        user_data = json.load(file)
    validate_user_data(user_data)
    if user not in user_data["users"].keys():
        print(f"User '{user}' not found.")
        exit(1)


def hash_password(password):
    # Generate a salt and hash the password in one step
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def validate_user_data(user_data):
    if not isinstance(user_data, dict):
        print("The disk may be corrupted, or the user file may be corrupted.")
        exit(1)


def check_password(stored_hash, password):
    # Compare the entered password with the stored hash
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def check_if_dict(obj, error: str = "Expected dict"):
    if not isinstance(obj, dict):
        print(error)
        exit(1)


def get_password(prompt="Password: ", mask="•"):
    print(prompt, end="", flush=True)
    password = []

    def on_press(key):
        nonlocal password
        if key == keyboard.Key.enter:
            return False  # Stop listener
        elif key == keyboard.Key.backspace:
            if password:
                password.pop()
                print("\b \b", end="", flush=True)
        elif hasattr(key, 'char') and key.char:
            password.append(key.char)
            time.sleep(0.07)  # Wait for keypress to register and get printed
            print("\b \b", end="", flush=True)  # Delete printed character
            print(mask, end="", flush=True)  # Replace with mask

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    input()

    return ''.join(password)


def login():
    user = input("Username: ").strip()
    check_user_exists(user)
    with open(Disk.disk_name + "/usr.ur") as file:
        user_data = json.load(file)
    attempts = 3
    while True:
        password = get_password("Password: ").strip()
        if check_password(user_data["users"][user]["password"], password):
            return user, user_data["users"][user]
        else:
            attempts -= 1
            if attempts == 0:
                return None, None
            print(f"Wrong password, you have {attempts} attempt{'s' if attempts != 1 else ''} left.")


def nebula_shell():
    global command_text
    user, user_data = login()
    if not user:
        print("Sorry, you cannot enter this device.")
        exit(1)
    sign = "#" if user == "root" else "$"
    user_home = user_data["home"]
    current_path = user_home
    print("Welcome to NebulaOS Restart 🚀")
    print("Type 'help' for commands.\n")

    while True:
        path = current_path.split("/")[-1]

        if current_path == user_home:
            path = "~"
        if not path:
            path = "/"
        print(f"(base) {platform.node().split('.')[0]}:{path} {user}{sign} ", end="")
        cmd = input().strip().split()

        if not cmd:
            continue

        if cmd[0] == "shutdown":
            print("Shutting down NebulaOS Restart...")
            time.sleep(1)
            print("Goodbye!")
            break

        elif cmd[0] == "ls":
            Disk.list_contents(current_path)

        elif cmd[0] == "cd":
            if len(cmd) < 2:
                print("Usage: cd <folder>")
                continue
            dir_name = cmd[1]
            if dir_name == "..":
                current_path = "/".join(current_path.split("/")[:-1])
            else:
                if dir_name.startswith("/"):
                    if Disk.change_directory(dir_name):
                        current_path = dir_name
                else:
                    full_path = current_path + "/" + dir_name
                    if Disk.change_directory(full_path):
                        current_path = full_path

        elif cmd[0] == "mkdir":
            if len(cmd) < 2:
                print("Usage: mkdir <folder>")
                continue
            dir_name = cmd[1]
            Disk.create_directory(f"{current_path}/{dir_name}")

        elif cmd[0] == "open":
            if len(cmd) < 2:
                print("Usage: open <filename>")
                continue
            file_name = cmd[1]
            content = Disk.read_data_from_disk(file_name, current_path)
            if content is None:
                print("Creating file...")
                content = ""

            print(f"Opening '{file_name}'. Type ':wq' to save and quit.")
            if content:
                print(f"--- Current content ---\n{content.decode()}\n-----------------------")

            new_lines = []
            while True:
                line = input()
                if line == ":wq":
                    break
                new_lines.append(line)

            Disk.write_data_to_disk(file_name, "\n".join(new_lines).encode(), current_path)

        elif cmd[0] == "cat":
            if len(cmd) < 2:
                print("Usage: cat <file>")
                continue
            file_name = cmd[1]
            content = Disk.read_data_from_disk(file_name, current_path)
            if content is not None:
                print(f"\n--- {file_name} ---")
                print(content.decode())
                print("---------------\n")

        elif cmd[0] == "printf":
            if len(cmd) < 2:
                print("Usage: printf <text>")
                continue
            if cmd[1] == "rockets":
                if len(cmd) < 3:
                    print("🚀")
                elif cmd[2].isdecimal():
                    print("🚀" * int(cmd[2]))
                else:
                    print(' '.join(cmd[1:]))
                continue
            print(' '.join(cmd[1:]))

        elif cmd[0] == "mode":
            if len(cmd) < 2:
                print("Usage: mode <mode>")
                continue
            if cmd[1] == "GUI":
                run("GUI/main.py")
                break

        elif cmd[0] == "save":
            print("Saving...")
            Disk.save()
            time.sleep(1)
            print("Saved, ", end="")
            time.sleep(0.6)
            print("Bye!")
            break

        elif cmd[0] == "addusr":
            if len(cmd) < 3:
                print("Usage: addusr <name> <passwd>")
                continue
            if user != "root":
                print("Permission denied.")
                continue
            user_name = cmd[1]
            password = cmd[2]
            Disk.create_directory(f"/Users/{user_name}")
            with open(Disk.disk_name + "/usr.ur", "r") as file:
                data = json.load(file)
            validate_user_data(data)
            data["users"][user_name] = {
                "password": hash_password(password),
                "home": f"/Users/{user_name}"
            }
            with open(Disk.disk_name + "/usr.ur", "w") as file:
                json.dump(data, file, indent=4)
            print(f"User '{user_name}' has been added.")

        elif cmd[0] == "setmode":
            if len(cmd) < 3:
                print("Usage: setmode <key> <value>")
                continue
            key = cmd[1]
            value = cmd[2]
            if key not in ["default_mode", "remember_me"]:
                print(f"Unknown key: {key}")
            # Open the file for both reading and writing
            with open(Disk.disk_name + "/settings.st", "r+") as file:
                # Load the existing data
                data = json.load(file)

                # Update the mode
                data[key] = value

                # Rewind the file pointer to the beginning before writing
                file.seek(0)

                # Write the updated data back to the file
                json.dump(data, file, indent=4)

                # Truncate the file in case the new JSON is smaller than the original
                file.truncate()

            print(f"{key} set to {value}.")

        elif cmd[0] == "help":
            print(command_text)

        elif cmd[0] == "addcmd":
            if len(cmd) < 2:
                print("Usage: addcmd <cmd>")
                continue
            cmd_name = cmd[1]
            cmd_code = []
            print("Please enter code for the custom command, type :wcmd to save")
            while True:
                line = input("> ")
                if line == ":wcmd":
                    break
                cmd_code.append(line)
            exa = []
            print("Please enter example usage for the custom command, type :wexa to save")
            while True:
                line = input("> ")
                if line == ":wexa":
                    break
                exa.append(line)
            des = []
            print("Please enter description for the custom command, type :wdes to save")
            while True:
                line = input("> ")
                if line == ":wdes":
                    break
                des.append(line)
            with open(Disk.disk_name + "/commands.cds", "r+") as f:
                data = json.load(f)
                data[cmd_name] = {
                    "code": "\n".join(cmd_code),
                    "example": "\n".join(exa),
                    "description": "\n".join(des)
                }
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

            print(f"Added command '{cmd_name}' successfully!")
            command_text = generate_help_text()

        elif cmd[0] == "nam":
            args = cmd[1:]
            if not args:
                print("Usage: nam <install|list|help> [package-name]")
                continue

            command = args[0]

            if command == "install":
                if len(args) < 2:
                    print("Usage: nam install <package-name>")
                    continue
                package_name = args[1]
                install_package(package_name)

            elif command == "list":
                print("Listing packages coming soon...")

            elif command == "help":
                print("Nam Package Manager Commands:")
                print("  nam install <package> - Install a package")
                print("  nam list              - List installed packages")
                print("  nam help              - Show this help message")

            else:
                print(f"Unknown command: {command}")

        elif cmd[0] in custom_commands:
            exec(custom_commands[cmd[0]]["code"])

        else:
            print(f"-bash: {cmd[0]}: command not found")


def main() -> None:
    if sys.stdout.isatty() and sys.stderr.isatty() and sys.stdin.isatty():
        logo = [
            r"|\    |  ╔------  ╔------    |     |  |        ╔-----╗       ╔-----╗   /------ ",
            r"| \   |  |        |       |  |     |  |        |     |       |     |  |        ",
            r"|  \  |  |------  |------|   |     |  |        |_____|       |     |   \-----\ ",
            r"|   \ |  |        |       |  |     |  |        |     |       |     |          |",
            r"|    \|  ╚------  ╚------    ╚_____╝  ╚______  |     |       ╚_____╝   ______/ ",
        ]

        os.system("clear")

        # 1. Print logo slowly
        for line in logo:
            for char in line:
                print(char, end="", flush=True)
                time.sleep(0.01)
            print()

        time.sleep(1)

        # 2. Erase logo line-by-line
        for i, line in enumerate(logo[::-1]):
            sys.stdout.write("\033[F")  # move cursor up one line
            length = len(line)
            for _ in range(length):
                line = line[:-1]
                sys.stdout.write("\r" + line + " ")  # remove the last character
                sys.stdout.flush()  # force the output to update
                time.sleep(0.01)  # slow down erasing effect
        os.system("clear")
        time.sleep(1)
    try:
        with open(Disk.disk_name + "/settings.st") as file:
            data = json.load(file)
            check_if_dict(data, "The disk may be corrupted.")
            if "default_mode" in data.keys():
                mode = data["default_mode"].lower()
                sys.stdout = sys.__stdout__
                if mode == "gui":
                    run("GUI/login.py")
                elif mode == "shell":
                    nebula_shell()
                else:
                    print(f"Unknown boot type {mode}, available boot types: GUI, Shell. Not case-sensitive")
                    print("Choosing default, which is shell.")
                    nebula_shell()
            else:
                nebula_shell()
            Disk.save()
    except KeyboardInterrupt:
        Disk.save()
        print("\nExited NebulaOS")

if __name__ == "__main__":
    main()
