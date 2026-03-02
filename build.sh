#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

source "$ROOT_DIR/.venv/bin/activate"
trap 'deactivate >/dev/null 2>&1 || true' EXIT

python scripts/build_site.py --root "$ROOT_DIR"
python scripts/diagram_tunnel.py
echo "Generated: public/index.html and public/diagram-tunnel.png"
