#!/usr/bin/env python3
"""Emit the geometry-first HETE stability boundary report as JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rx.toroidal_geodesic_stability import instability_geometry_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--major-radius", type=float, default=2.0)
    parser.add_argument("--minor-radius", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = instability_geometry_report(args.major_radius, args.minor_radius)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
