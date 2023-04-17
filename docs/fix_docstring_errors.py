"""Script to fix Sphinx docstring errors in Swagger client generated code"""

import fileinput
import sys


def main():
    """Entry point"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} FILENAME", file=sys.stderr)
        sys.exit(1)

    async_req_str = ":param async_req bool"
    thread_str = ">>> thread ="
    with fileinput.input(files=[sys.argv[1]], inplace=True) as f:
        for line in f:
            text = line.strip()
            if text == async_req_str:
                line = line.replace("bool", "bool: Set True to make the request asynchronous.")
            elif text.startswith(thread_str):
                print()
            print(line, end="")


if __name__ == "__main__":
    main()
