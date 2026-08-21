#!/usr/bin/env  bash

set -euo pipefail

generate_args=()
detector_args=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --samples|--seed|--spikes|--steps|--drifts)
        if [[ $# -lt 2 ]]; then
            echo "Missing value for $1" >&2
            exit 2
        fi

        generate_args+=("$1" "$2")
        shift 2
        ;;
        
        --detectors)
        detector_args+=("$1")
        shift

        if [[ $# -eq 0 || "$1" == --* ]]; then
            echo "No detector supplied for --detectors" >&2
            exit 2
        fi

        while [[ $# -gt 0 ]]; do
            if [[ "$1" == --* ]]; then
                break
            fi

            detector_args+=("$1")
            shift
        done

        ;;
    *)
        echo "Unknown Argument: $1" >&2
        exit 2
        ;;
    esac
done


declare -p generate_args detector_args
    

python3 generate.py "${generate_args[@]}"
python3 detect.py "${detector_args[@]}"
python3 evaluate.py



