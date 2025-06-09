import os
import struct
import bcrypt
import json
from .defines import *


def _hash_password(password):
    # Generate a salt and hash the password in one step
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


# Format disk
def format_disk_image():
    global superblock
    if not os.path.exists(disk_name):
        os.makedirs(disk_name, exist_ok=True)
        with open(disk_name + "/root.rf", "w") as root:
            json.dump(superblock, root, indent=4)
        with open(disk_name + "/usr.ur", "w") as usr:
            a = {
                "users": {
                    "root": {"password": _hash_password("password"), "home": "/Users/root"}
                }
            }
            json.dump(a, usr, indent=4)
        with open(disk_name + "/settings.st", "w") as settings:
            a = {
                "default_mode": "Shell"
            }
            json.dump(a, settings, indent=4)
        with open(disk_name + "/commands.cds", "w") as commands:
            a = {}
            json.dump(a, commands)
    with open(disk_name + "/data.img", "wb") as disk:
        disk.write(bytearray(disk_size))  # Write zeroes to initialize
    superblock["root"]["contents"] = {}  # Reset directory structure
    superblock["free_block_map"] = [True] * total_blocks  # Reset block map
    superblock["used_blocks"] = 0
    print("Disk formatted successfully!")


# Create a directory
def create_directory(path):
    global superblock
    parts = path.strip("/").split("/")
    current = superblock["root"]

    for part in parts:
        if part not in current["contents"]:
            current["contents"][part] = {"type": "dir", "contents": {}}
        current = current["contents"][part]

    print(f"Directory '{path}' created successfully!")


# Change directory
def change_directory(path):
    global superblock
    parts = path.strip("/").split("/")
    current = superblock["root"]

    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
        else:
            print(f"Error: Directory '{path}' not found.")
            return

    superblock["current_dir"] = path
    print(f"Changed directory to: {path}")
    return 1


# List directory contents
def list_contents(path="/"):
    global superblock
    parts = path.strip("/").split("/")
    current = superblock["root"]

    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
    else:
        if current == superblock["root"]:
            print(f"Error: Directory '{path}' not found.")
            return

    print(f"Contents of '{path}':")
    for name, info in current["contents"].items():
        print(f"  {'[DIR]' if info['type'] == 'dir' else '[FILE]'} {name}")
    return 1


# Find free blocks
def find_free_blocks(size):
    needed_blocks = (size + block_size - 1) // block_size  # Round up
    if needed_blocks == 0:
        needed_blocks += 1
    free_blocks = [i for i in range(total_blocks) if superblock["free_block_map"][i]]
    return free_blocks[:needed_blocks] if len(free_blocks) >= needed_blocks else None


# Write data to disk
def write_data_to_disk(filename, data, path="/", overwrite_ok=False):
    global superblock
    parts = path.strip("/").split("/")
    current = superblock["root"]

    # Traverse to the directory
    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
        else:
            print(f"Error: Directory '{path}' not found.")
            return

    # Check if file exists
    if filename in current["contents"]:
        if not overwrite_ok:
            choice = input(f"File '{filename}' already exists. Overwrite? (Y/n): ").strip().lower()
        else:
            choice = "y"
        if choice == "y":
            file_meta = current["contents"][filename]
            old_blocks = file_meta["blocks"]
            free_blocks = find_free_blocks(len(data))  # Allocate new blocks
            if not free_blocks:
                print("Error: Not enough space on disk.")
                return
            first_block = free_blocks[0]
            num_blocks = len(free_blocks)

            # Free old blocks
            for i in range(old_blocks):
                superblock["free_block_map"][file_meta["start"] + i] = True  # Mark as free
        else:
            return
    else:
        free_blocks = find_free_blocks(len(data))
        if not free_blocks:
            print("Error: Not enough space on disk.")
            return
        first_block = free_blocks[0]
        num_blocks = len(free_blocks)

    # Write data to disk
    with open(disk_name + "/data.img", "r+b") as disk:
        for i, block in enumerate(free_blocks):
            disk.seek(block * block_size)
            block_data = data[i * block_size:(i + 1) * block_size]
            disk.write(block_data)
            superblock["free_block_map"][block] = False  # Mark as used

    # Save file metadata in directory
    current["contents"][filename] = {
        "type": "file",
        "start": first_block,
        "size": len(data),
        "blocks": num_blocks
    }
    print(f"File '{filename}' stored in '{path}'.")
    return 1


# Read file from disk
def read_data_from_disk(filename, path="/"):
    global superblock
    parts = path.strip("/").split("/")
    current = superblock["root"]

    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
        else:
            print(f"Error: Directory '{path}' not found.")
            return None

    if filename not in current["contents"]:
        print(f"Error: File '{filename}' not found.")
        return None

    file_meta = current["contents"][filename]
    data = b""

    with open(disk_name + "/data.img", "rb") as disk:
        for block in range(file_meta["blocks"]):
            disk.seek((file_meta["start"] + block) * block_size)
            data += disk.read(block_size)

    return data[:file_meta["size"]]  # Trim extra bytes


# Delete file
def delete_file(filename, path="/"):
    global superblock
    parts = path.strip("/").split("/")
    current = superblock["root"]

    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
        else:
            print(f"Error: Directory '{path}' not found.")
            return

    if filename not in current["contents"]:
        print(f"Error: File '{filename}' not found.")
        return

    file_meta = current["contents"].pop(filename)  # Remove from directory

    # Free up blocks
    for block in range(file_meta["blocks"]):
        superblock["free_block_map"][file_meta["start"] + block] = True

    print(f"File '{filename}' deleted successfully.")
    return 1


# Delete directory
def delete_directory(path):
    global superblock

    parts = path.strip("/").split("/")
    current = superblock["root"]

    for i, part in enumerate(parts):
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            if i == len(parts) - 1:  # Last part, delete this dir
                if current["contents"][part]["contents"]:
                    print(f"Error: Directory '{path}' is not empty.")
                    return
                del current["contents"][part]
                print(f"Directory '{path}' deleted successfully.")
                return
            current = current["contents"][part]
        else:
            print(f"Error: Directory '{path}' not found.")
            return
    return 1


# Extend disk image
def extend_disk_image(num_blocks):
    global superblock

    new_size = os.path.getsize(disk_name + "/data.img") + (block_size * num_blocks)  # Add 100 more blocks
    with open(disk_name + "/data.img", "ab") as disk:
        disk.write(bytearray(block_size * num_blocks))  # Extend with zeroes

    superblock["total_blocks"] = new_size // block_size
    superblock["free_block_map"].extend([True] * num_blocks)
    print("Disk extended!")


def save():
    with open(disk_name + "/root.rf", "w") as disk:
        json.dump(superblock, disk, indent=4)


def load():
    global superblock
    with open(disk_name + "/root.rf", "r") as disk:
        root = json.load(disk)
        if isinstance(root, dict):
            superblock = root
        else:
            raise TypeError(f"Disk image {disk_name} if not valid.")


def exists(path):
    parts = path.strip("/").split("/")
    current = superblock["root"]

    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
        elif part in current["contents"] and current["contents"][part]["type"] == "file":
            return True
        else:
            return False
    else:
        if parts:
            return True
        else:
            return False


def get_root():
    return superblock["root"]


def walk(top="/", topdown=True):
    """
    Custom implementation of os.walk using the custom disk structure.

    Args:
        top (str): The root directory to start walking from (default is "/").
        topdown (bool): Whether to traverse directories top-down or bottom-up (default is True).

    Yields:
        3-tuple (dirpath, dirnames, filenames):
            - dirpath: Current directory path (string).
            - dirnames: List of subdirectories in current directory (list of strings).
            - filenames: List of non-directory files in current directory (list of strings).
    """
    global superblock

    parts = top.strip("/").split("/") if top != "/" else []
    current = superblock["root"]

    for part in parts:
        if part in current["contents"] and current["contents"][part]["type"] == "dir":
            current = current["contents"][part]
        else:
            print(f"Error: Directory '{top}' not found.")
            return

    def _walk(dir_info, rel_path):
        subdirs = [name for name, info in dir_info["contents"].items() if info["type"] == "dir"]
        files = [name for name, info in dir_info["contents"].items() if info["type"] == "file"]

        if topdown:
            yield rel_path, subdirs, files

        for subdir in subdirs:
            subdir_info = dir_info["contents"][subdir]
            sub_path = f"{rel_path}/{subdir}" if rel_path else subdir
            yield from _walk(subdir_info, sub_path)

        if not topdown:
            yield rel_path, subdirs, files

    yield from _walk(current, "" if top == "/" else top.strip("/"))


__all__ = [
    "format_disk_image",
    "create_directory",
    "delete_directory",
    "change_directory",
    "delete_file",
    "write_data_to_disk",
    "read_data_from_disk",
    "load",
    "save",
    "exists",
    "get_root",
    "list_contents",
    "extend_disk_image",
    "walk"
]

# Example usage
if __name__ == "__main__":
    format_disk_image()

    create_directory("/home")
    create_directory("/home/user")
    create_directory("/home/user/documents")

    write_data_to_disk("hello.txt", b"Hello, NebulaOS!", "/home/user")
    write_data_to_disk("code.py", b"print('Hello, World!')", "/home/user/documents")

    list_contents("/")            # Show root
    list_contents("/home")        # Show /home
    list_contents("/home/user")   # Show /home/user
    list_contents("/home/user/documents")  # Show /home/user/documents

    change_directory("/home/user")  # Move into /home/user

    delete_file("hello.txt", "/home/user")
    delete_directory("/home/user/documents")  # Error: Not empty
