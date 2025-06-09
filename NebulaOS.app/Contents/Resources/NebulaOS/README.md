# NebulaOS

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
    - Open the extracted folder and follow the instructions in the [`Installation.md`](Installation.md) file to install the necessary Python packages.
    - If you do not want to follow `Installation.md`, you can navigate to the folder where you cloned or downloaded NebulaOS and run [`install.sh`](install.sh).

    - Running the `install.sh` script will automatically install the required packages and prepare the environment.

---

## Running NebulaOS
After setting up NebulaOS, run:
```bash
source .venv/bin/activate
python3 _core/shell.py
```
You will be prompted for a username. Enter `root`.

The default password for root is `password`.

When you have entered the shell, you can type `help` for all available commands.

---

## Troubleshooting

- **Issue**: `Permission denied` when running `install.sh`.  
  **Solution**: Make the script executable:
  ```bash
  chmod +x install.sh
  ```

- **Issue**: Python version mismatch.  
  **Solution**: Make sure you are using Python 3.10 or newer.

---

## Future Features

- **Install more apps**: NebulaOS will support `.neap` packages through the `nam` package manager.
- **Cross-platform support**: Windows and Linux support may be added in the future.
- **Improved GUI**: A full windowing system and visual app launcher are in the works.

---
