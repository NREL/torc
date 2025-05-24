#!/usr/bin/env python

"""Test script to simulate doing work."""

import json
import os
import sys
from pathlib import Path


# command="python work.py -i f1.json -o f2.json",
if len(sys.argv) != 5:
    msg = f"bad inputs in work.py: {sys.argv}"
    raise Exception(msg)

workflow_key = os.environ["TORC_WORKFLOW_KEY"]
job_key = os.environ["TORC_JOB_KEY"]
print(f"running {sys.argv} {workflow_key=} {job_key=}")
input_file = Path(sys.argv[2])
output_file = Path(sys.argv[4])
if not input_file.exists():
    msg = f"{input_file} does not exist"
    raise Exception(msg)

output_file.write_text(json.dumps({"hello": "world"}, indent=2) + "\n", encoding="utf-8")
