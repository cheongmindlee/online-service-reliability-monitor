#!/usr/bin/env  bash

set -euo pipefail

python3 generate.py "$@"
python3 detect.py
python3 evaluate.py



