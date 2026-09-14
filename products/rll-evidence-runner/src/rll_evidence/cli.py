from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import EvidenceError, compare_receipt, run_experiment, validate_experiment, verify_receipt


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(prog="rll-evidence")
    parser.add_argument("--repository-root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("experiment", type=Path)

    run = sub.add_parser("run")
    run.add_argument("experiment", type=Path)
    run.add_argument("--receipt", type=Path, default=None)

    verify = sub.add_parser("verify")
    verify.add_argument("receipt", type=Path)

    compare = sub.add_parser("compare")
    compare.add_argument("receipt", type=Path)
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--candidate", required=True)

    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = validate_experiment(args.experiment, args.repository_root)
            _print(result)
            return 0 if result["state"] != "INVALID" else 2
        if args.command == "run":
            result = run_experiment(args.experiment, args.repository_root, args.receipt)
            _print(result)
            return 0 if result["decision"]["state"] == "VERIFIED_LIMITED" else 3
        if args.command == "verify":
            result = verify_receipt(args.receipt, args.repository_root)
            _print(result)
            return 0 if result["state"] == "PASS" else 4
        result = compare_receipt(args.receipt, args.baseline, args.candidate)
        _print(result)
        return 0 if result["state"] == "VERIFIED_LIMITED" else 5
    except (EvidenceError, OSError, ValueError, KeyError) as exc:
        _print({"state": "FAIL", "claim_allowed": False, "error": str(exc)})
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
