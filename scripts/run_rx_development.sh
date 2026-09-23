#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Rx development chain ==="
echo "training=False ai_runtime=False"
exec python3 -m rx develop
