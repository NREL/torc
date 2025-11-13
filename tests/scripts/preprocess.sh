#!/bin/bash
set -e

while [[ $# -gt 0 ]]; do
    case $1 in
        -i) INPUT="$2"; shift 2 ;;
        -o) OUTPUTS+=("$2"); shift 2 ;;
        *) shift ;;
    esac
done

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file $INPUT not found"
    exit 1
fi

INPUT_DATA=$(cat "$INPUT")
echo "Preprocess: Read input from $INPUT: $INPUT_DATA"

for OUTPUT in "${OUTPUTS[@]}"; do
    echo "{\"source\": \"preprocess\", \"input\": $INPUT_DATA, \"output\": \"$OUTPUT\"}" > "$OUTPUT"
    echo "Preprocess: Created $OUTPUT"
done
