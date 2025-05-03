#!/bin/bash

cd /path/to/NebulaOS || exit 1
python3 -m mk_venv .venv
source .venv/bin/activate
pip install bcrypt pygame requests pynput
