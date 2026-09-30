#!/usr/bin/env python3
"""Run the isolated Dark Dimension structural benchmark.

No network, no external dependencies, no scientific claim promotion.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "data/pipelines/structure_d/dark_dimension_benchmark.py"


def load_module():
    spec = importlib.util.spec_from_file_location("dark_dimension_benchmark", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load dark dimension benchmark module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon-scale-m", type=float, required=True)
    parser.add_argument("--compact-radius-m", type=float, required=True)
    parser.add_argument("--separation-factor", type=float, default=10.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    mod = load_module()
    receipt = mod.build_benchmark_receipt(
        r_h_m=args.horizon_scale_m,
        compact_radius_m=args.compact_radius_m,
        separation_factor=args.separation_factor,
    )
    payload = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.output:
        output = args.output
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
