#!/usr/bin/env python

import sys

print("Fail on purpose", file=sys.stderr)
sys.exit(1)
