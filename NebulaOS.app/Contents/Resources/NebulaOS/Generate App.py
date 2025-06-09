import os
import shutil
import plistlib

join = os.path.join

def mkdirs(*dirs):
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

# Directories
app = "NebulaOS.app"
contents = join(app, "Contents")
macos = join(contents, "MacOS")
resources = join(contents, "Resources")
root = join(resources, "NebulaOS")
venv = join(resources, ".venv")
mkdirs(app, contents, macos, resources)

# Files
boot = join(macos, "boot")
boot_py = join(resources, "boot.py")
info = join(contents, "Info.plist")
PkgInfo = join(contents, "PkgInfo")

plist = {
    "CFBundleName": "NebulaOS",
    "CFBundleIdentifier": "com.ayaan.nebulaos",
    "CFBundleVersion": "1.0",
    "CFBundleExecutable": "boot",
    "CFBundleIconFile": "NebulaOSicon.icns",
    "CFBundlePackageType": "APPL",
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleSupportedPlatforms": ["MacOSX"],
    "NSPrincipalClass": "NSApplication",
    "LSMinimumSystemVersion": "10.15",
    "NSHighResolutionCapable": True
}

with open("App Sources/boot") as f:
    bootstrap_main = f.read()

with open("App Sources/boot.py") as f:
    bootstrap_python = f.read()

# Write the actual app
with open(info, "wb") as plist_file:
    plistlib.dump(plist, plist_file)

with open(PkgInfo, "w") as pkg:
    pkg.write("APPL????")

with open(boot_py, "w") as boot_py_file:
    boot_py_file.write(bootstrap_python)

with open(boot, "w") as boot_file:
    boot_file.write(bootstrap_main)
os.chmod(boot, 0o755)

# Bundle _core and virtualenv
if os.path.exists(root):
    shutil.rmtree(root)
if os.path.exists(venv):
    shutil.rmtree(venv)
shutil.copytree(
    ".",
    root,
    ignore=shutil.ignore_patterns("*.pyc", "__pycache__", "NebulaOS.app", "app_imgs", "generate_icon.py", "get_req.py", "push.py", ".git", ".idea", ".gitignore", "tests")
)
