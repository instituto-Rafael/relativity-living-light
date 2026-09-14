#!/usr/bin/env python3
"""Generate the deterministic RLL strong-gravity calibration payload."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rll.strong_gravity_calibration import calibration_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="results/strong_gravity_calibration/session_reference_sweep_20260717.json",
    )
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = calibration_payload()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "claim_allowed": False, "status": "ok"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
