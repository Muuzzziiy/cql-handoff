#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/reset_round.py "$@"
