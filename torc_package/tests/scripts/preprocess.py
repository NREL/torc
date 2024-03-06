#!/usr/bin/env python

"""Test script to run a preprocess command."""

import json
import sys
from pathlib import Path

# python preprocess.py -i f1 -o f2
if len(sys.argv) != 5:
    raise Exception(f"bad inputs in preprocess.py: {sys.argv}")

input_file = Path(sys.argv[2])
if not input_file.exists():
    raise Exception(f"{input_file} does not exist")

output_file = Path(sys.argv[4])
output_file.write_text(json.dumps({"hello": "world"}, indent=2) + "\n", encoding="utf-8")
