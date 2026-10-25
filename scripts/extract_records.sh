#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/extract_records.py
