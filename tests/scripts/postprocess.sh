#!/bin/bash
set -e

INPUTS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -i) INPUTS+=("$2"); shift 2 ;;
        -o) OUTPUT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

COMBINED="["
for INPUT in "${INPUTS[@]}"; do
    if [ ! -f "$INPUT" ]; then
        echo "Error: Input file $INPUT not found"
        exit 1
    fi
    INPUT_DATA=$(cat "$INPUT")
    COMBINED="$COMBINED$INPUT_DATA,"
    echo "Postprocess: Read input from $INPUT"
done
COMBINED="${COMBINED%,}]"

echo "{\"source\": \"postprocess\", \"inputs\": $COMBINED}" > "$OUTPUT"
echo "Postprocess: Created $OUTPUT"
