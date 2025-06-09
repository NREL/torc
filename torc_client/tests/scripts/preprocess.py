#!/usr/bin/env python

"""Test script to run a preprocess command."""

import json
import sys
from pathlib import Path

# python preprocess.py -i f1 -o f2 -o f3
if len(sys.argv) != 7:
    msg = f"bad inputs in preprocess.py: {sys.argv}"
    raise Exception(msg)

input_file = Path(sys.argv[2])
if not input_file.exists():
    msg = f"{input_file} does not exist"
    raise Exception(msg)

for index in (4, 6):
    output_file = Path(sys.argv[index])
    output_file.write_text(json.dumps({"hello": "world"}, indent=2) + "\n", encoding="utf-8")
