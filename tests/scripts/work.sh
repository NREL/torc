#!/bin/bash
set -e

while [[ $# -gt 0 ]]; do
    case $1 in
        -i) INPUT="$2"; shift 2 ;;
        -o) OUTPUT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file $INPUT not found"
    exit 1
fi

INPUT_DATA=$(cat "$INPUT")
echo "Work: Processing $INPUT -> $OUTPUT"
echo "{\"source\": \"work\", \"processed\": $INPUT_DATA}" > "$OUTPUT"
echo "Work: Created $OUTPUT"
