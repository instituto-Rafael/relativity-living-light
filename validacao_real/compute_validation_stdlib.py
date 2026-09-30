#!/usr/bin/env python3
"""Compatibility entrypoint for the Rx zero-dependency validation pipeline.

Historical command preserved:
    python3 validacao_real/compute_validation_stdlib.py

Canonical Rx command:
    python3 -m validacao_real.run_rx_pipeline
"""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

runpy.run_module("validacao_real.run_rx_pipeline", run_name="__main__")
