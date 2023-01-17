#!/usr/bin/env python

import json
import sys
from pathlib import Path

# python preprocess.py -i {inputs} -o {f1}
if len(sys.argv) != 5:
    raise Exception(f"bad inputs in work.py: {sys.argv}")

input_file = Path(sys.argv[2])
if not input_file.exists():
    raise Exception(f"{input_file} does not exist")

print(f"running {sys.argv}")
output_files = [Path(sys.argv[4])]
for f in output_files:
    f.write_text(json.dumps({"hello": "world"}, indent=2) + "\n")
