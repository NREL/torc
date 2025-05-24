#!/usr/bin/env python

"""Test script to cause CPU and memory resource consumption."""

import gc
import random
import sys
import time


# command="python resource_consumption.py -i 1 -c small"
if len(sys.argv) != 5:
    msg = f"bad inputs in resource_consumption.py: {sys.argv}"
    raise Exception(msg)

print(f"running {sys.argv}")
index = int(sys.argv[2])
category = sys.argv[4]
match category:
    case "small":
        count = 1_000_000
    case "medium":
        count = 5_000_000
    case "large":
        count = 10_000_000
    case _:
        msg = f"invalid {category=}"
        raise Exception(msg)

for i in range(5):
    data = [random.random() for _ in range(count)]
    total = sum(data)
    minimum = min(data)
    maximum = max(data)
    mean = total / len(data)
    print(f"job {index=} {i=} {total=} {minimum=} {maximum=} {mean=}")
    data.clear()
    gc.collect()
    time.sleep(1)
