# NebulaOS Restart

NebulaOS is an operating system designed by Ayaan with help from ChatGPT.

**NOTE**: While ChatGPT might be the source of some ideas, all the core concepts and decisions have been made by Ayaan.

---

## Installation

#### WARNING: This Only Works on macOS for now
*NebulaOS is currently only compatible with macOS.*  
Support for Windows and Linux may come in the future, but it is not available at the moment.

### Steps to Install:

1. **Download NebulaOS**:
   - Download the repository as a zip file and extract it to a folder.

2. **Install Required Packages**:
   - Ensure you have Python installed on your machine.
   - Open the extracted folder and follow the instructions in the `Installation.txt` file to install the necessary Python packages.
   - If you do not want to follow `Installation.txt` you can navigate to the folder where you cloned or downloaded NebulaOS and run `install.sh`

### Running NebulaOS
After installing and activating the virtual environment, run:
```bash
python3 _core/shell.py
```
You will be prompted for a username, enter `root`.
The default password for root is `password`

#### Note:
- Since NebulaOS is written in Python, it is not intended to be installed on a physical machine just yet. It runs within a Python environment.
