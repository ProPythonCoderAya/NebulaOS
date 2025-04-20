import os
import sys
import time
import json
import Disk
import bcrypt
import platform


def run(filepath):
    cmd = [
        f"\"{sys.executable}\"", f"\"{filepath}\""
    ]
    os.system(" ".join(cmd))

custom_commands = {}
data = json.load(f"{Disk.disk_name}/commands.cds")
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
    "shutdown": "Shut down NebulaOS"
}
command_text = ["", "NebulaOS Restart Commands:"]
length = max([len(cmd) for cmd, _ in commands_description.items()]) + 2
for cmd, exp in commands_description.items():
    command_text.append("  " + cmd + (" " * (length - len(cmd))) + "- " + exp)
command_text.append("")
command_text = "\n".join(command_text)

if not os.path.exists(Disk.disk_name):
    sys.stdout = open(os.devnull, "w")
    Disk.format_disk_image()
    Disk.create_directory("/Users")
    Disk.create_directory("/Users/root")
    Disk.create_directory("/Applications")
    Disk.create_directory("/Applications/Terminal.neap")
    Disk.create_directory("/Applications/Terminal.neap/")
    Disk.create_directory("/Applications/Terminal.neap/Files")
    Disk.create_directory("/Applications/Terminal.neap/Files/Executable")
    Disk.write_data_to_disk("Terminal",
                            b"""!8-bit-code

0x10 terminal-main.py
                            """,
                            "/Applications/Terminal.neap/Files/Executable")
    Disk.create_directory("/Applications/Terminal.neap/Files/Resources")
    Disk.write_data_to_disk("terminal-main.py",
                            b"""#/usr/local/bin/python3

print("Terminal run!")

                            """,
                            "/Applications/Terminal.neap/Files/Resources")
    Disk.write_data_to_disk("Terminal.svg", open("GUI/Textures/Builtin_apps/Terminal.svg", "rb").read(),
                            "/Applications/Terminal.neap/Files/Resources")
    Disk.write_data_to_disk("Info.prop",
                            b"""{
    "name": "Terminal",
    "version": "3.0",
    "author": "Nebula",
    "description": "Terminal",
    "image": "Terminal.svg"
}""",
                            "/Applications/Terminal.neap/Files")
    sys.stdout = sys.__stdout__
else:
    Disk.load()


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


def login():
    user = input("Username: ").strip()
    check_user_exists(user)
    with open(Disk.disk_name + "/usr.ur") as file:
        user_data = json.load(file)
    attempts = 3
    while True:
        password = input("Password: ").strip()
        if check_password(user_data["users"][user]["password"], password):
            return user, user_data
        else:
            attempts -= 1
            if attempts == 0:
                return None, None
            print(f"Wrong password, you have {attempts} attempt{'s' if attempts != 1 else ''} left.")


def nebula_shell():
    user, _ = login()
    if not user:
        print("Sorry, you cannot enter this device.")
        exit(1)
    sign = "#" if user == "root" else "$"
    current_path = f"/Users/{user}"
    print("Welcome to NebulaOS Restart 🚀")
    print("Type 'help' for commands.\n")

    while True:
        path = current_path.split("/")[-1]

        if path == user:
            path = "~"
        if not path:
            path = "/"
        cmd = input(f"(base) {platform.node().split('.')[0]}:{path} {user}{sign} ").strip().split()

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

        elif cmd[0] in custom_commands:
            exec(custom_commands[cmd[0]]["code"])

        else:
            print(f"-bash: {cmd[0]}: command not found")


def main() -> None:
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
    except KeyboardInterrupt:
        Disk.save()
        print("\nExited NebulaOS")

if __name__ == "__main__":
    main()
