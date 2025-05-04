#!/bin/bash

python3 -m mk_venv .venv
source .venv/bin/activate
pip install -r requirements.txt
