#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Rx development chain ==="
echo "training=False ai_runtime=False"

python3 tools/rx_selftest.py
python3 -m validacao_real.run_rx_pipeline
python3 -m validacao_real.run_rx_multiprobe
python3 tools/rx_semantic_parity.py
python3 tools/rx_dependency_audit.py
python3 tools/rx_development_gate.py

echo "RX_DEVELOPMENT_CHAIN=PASS"
