#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PYTHONPATH=src python -m unittest discover -s tests -p 'test_mathematics_registry_adapter.py' -v
PYTHONPATH=src python tools/emulate_mathematics_registry_adapter.py
