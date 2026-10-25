#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/download_data.py
