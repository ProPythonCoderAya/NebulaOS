#!/bin/bash

py_ver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if [[ "$py_ver" < "3.10" ]]; then
    echo "⚠️  Python version $py_ver may not work. Please use Python 3.10 or newer."
    printf "Proceed with installation? (Y/n): "
    read -r answer
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    if [ "$answer" != "y" ]; then
        echo "Abort"
        exit 1
    fi
fi

python3 -m mk_venv .venv
source .venv/bin/activate
pip install -r requirements.txt
