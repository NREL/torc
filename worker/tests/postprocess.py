#!/usr/bin/env python

import json
import sys
from pathlib import Path

# command="python postprocess.py -i f2.json -i f3.json -o f4.json",
if len(sys.argv) != 7:
    raise Exception(f"bad inputs in postprocess.py: {sys.argv}")

print(f"running {sys.argv}")
input_file1 = Path(sys.argv[2])
input_file2 = Path(sys.argv[4])
output_file = Path(sys.argv[6])
if not input_file1.exists():
    raise Exception(f"{input_file1} does not exist")
if not input_file2.exists():
    raise Exception(f"{input_file2} does not exist")

output_file.write_text(json.dumps({"hello": "world"}, indent=2) + "\n")
