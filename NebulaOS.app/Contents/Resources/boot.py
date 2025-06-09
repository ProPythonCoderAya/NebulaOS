import os
import sys

# Step 1: Find the real path of this file (inside .app or not)
here = os.path.dirname(os.path.abspath(__file__))
resources = os.path.abspath(os.path.join(here, "..", "Resources"))
root = os.path.join(resources, "NebulaOS")
venv_bin = os.path.join(root, ".venv", "bin")

# Step 2: Fix sys.path so imports like 'from _core import ...' work
def add_all_subdirs_to_syspath(base):
    for dirpath, _, _ in os.walk(base):
        if dirpath not in sys.path:
            if ".venv" not in dirpath:
                sys.path.insert(0, dirpath)

sys.path.insert(0, resources)
sys.path.insert(0, root)
add_all_subdirs_to_syspath(root)

# Step 3: Activate the virtual environment
venv_site = os.path.join(root, ".venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# Step 4: Exec the real shell (cleaner than os.system)
shell_path = os.path.join(root, "_core", "shell.py")
with open(shell_path, "r") as f:
    code = compile(f.read(), shell_path, "exec")
    os.chdir(os.path.join(root, "_core"))
    exec(code, {"__name__": "__main__", "__file__": shell_path})
