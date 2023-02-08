#!/usr/bin/env python

import json
import sys
from pathlib import Path

# python preprocess.py -i {inputs} f1 f2
if len(sys.argv) < 4:
    raise Exception(f"bad inputs in preprocess.py: {sys.argv}")

input_file = Path(sys.argv[2])
if not input_file.exists():
    raise Exception(f"{input_file} does not exist")

output_files = [Path(x) for x in sys.argv[3:]]
for f in output_files:
    f.write_text(json.dumps({"hello": "world"}, indent=2) + "\n")
