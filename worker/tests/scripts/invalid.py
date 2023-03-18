#!/usr/bin/env python

"""Test script to simulate a failed job."""

import sys

print("Fail on purpose", file=sys.stderr)
sys.exit(1)
