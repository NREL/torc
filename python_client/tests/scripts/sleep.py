#!/usr/bin/env python

"""Test script to sleep."""

import signal
import sys
import time


g_shutdown = False


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} SECONDS", file=sys.stderr)
        sys.exit(1)

    sleep = int(sys.argv[1])
    signal.signal(signal.SIGTERM, sigterm_handler)
    for _ in range(sleep):
        if g_shutdown:
            break
        time.sleep(1)


def sigterm_handler(signum, frame):
    global g_shutdown
    print("Detected SIGTERM")
    g_shutdown = True


if __name__ == "__main__":
    main()
