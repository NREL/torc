#!/usr/bin/env python

"""Test script to sleep."""

import sys
import time

sleep = int(sys.argv[1])
print(f"sleep for {sleep} seconds")
time.sleep(sleep)
