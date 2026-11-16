#!/usr/bin/env python3
"""Audit the legacy Structure-D runner's consumption/evidence boundary.

PASS here means the runner tells the truth about what its objective consumes.
It does not mean the four-axis scientific profile is complete and never promotes
an RLL claim.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pipelines.structure_d import run_all_real  # noqa: E402
from data.pipelines.structure_d.data_access import load_run_config  # noqa: E402

CONFIG_PATH = ROOT / "data" / "pipelines" / "structure_d" / "datasets_config.json"
RUNNER_PATH = ROOT / "data" / "pipelines" / "structure_d" / "run_all_real.py"
PROFILE = "structure_d_real_validation"


def _objective_dataset_refs() -> list[str]:
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"), filename=str(RUNNER_PATH))
    main_node = next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "main"
        ),
        None,
    )
    if main_node is None:
        raise RuntimeError("run_all_real.py has no main()")

    refs: set[str] = set()
    for node in ast.walk(main_node):
        if not isinstance(node, ast.Subscript):
            continue
        if not isinstance(node.value, ast.Name) or node.value.id != "datasets":
            continue
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            refs.add(node.slice.value)
    return sorted(refs)


def build_receipt() -> dict[str, object]:
    cfg = load_run_config(str(CONFIG_PATH))
    profile = cfg.get("profiles", {}).get(PROFILE)
    if not isinstance(profile, dict):
        raise RuntimeError(f"missing profile: {PROFILE}")

    active = list(profile.get("active_datasets", []))
    ast_consumed = _objective_dataset_refs()
    contract = run_all_real.build_legacy_execution_contract(active, "prefer_full")
    declared_consumed = sorted(contract["datasets_consumed_in_objective"])
    unconsumed_expected = sorted(set(active) - set(ast_consumed))

    full_required_blocked = False
    full_required_error = None
    try:
        run_all_real.build_legacy_execution_contract(active, "full_required")
    except RuntimeError as exc:
        full_required_blocked = True
        full_required_error = str(exc)

    checks = [
        {
            "id": "F05-TRUTH-01",
            "name": "declared_consumption_matches_objective_ast",
            "state": "PASS" if declared_consumed == ast_consumed else "FAIL",
            "declared": declared_consumed,
            "objective_ast": ast_consumed,
        },
        {
            "id": "F05-TRUTH-02",
            "name": "unconsumed_active_datasets_are_explicit",
            "state": (
                "PASS"
                if sorted(contract["unconsumed_active_datasets"])
                == unconsumed_expected
                else "FAIL"
            ),
            "observed": sorted(contract["unconsumed_active_datasets"]),
            "expected": unconsumed_expected,
        },
        {
            "id": "F05-TRUTH-03",
            "name": "covariance_requested_vs_effective_is_explicit",
            "state": (
                "PASS"
                if contract["covariance_policy_requested"] == "prefer_full"
                and contract["covariance_policy_effective"] == "diagonal_only"
                and bool(contract["covariance_gap"])
                else "FAIL"
            ),
            "requested": contract["covariance_policy_requested"],
            "effective": contract["covariance_policy_effective"],
            "gap": contract["covariance_gap"],
        },
        {
            "id": "F05-TRUTH-04",
            "name": "full_required_fails_closed",
            "state": "PASS" if full_required_blocked else "FAIL",
            "error": full_required_error,
        },
        {
            "id": "F05-TRUTH-05",
            "name": "four_axis_profile_is_not_mislabeled_complete",
            "state": (
                "PASS"
                if contract["full_profile_consumed"] is False
                and "real_fsigma8" in contract["unconsumed_active_datasets"]
                else "FAIL"
            ),
            "full_profile_consumed": contract["full_profile_consumed"],
            "unconsumed": contract["unconsumed_active_datasets"],
        },
    ]

    blocking = [row["id"] for row in checks if row["state"] != "PASS"]
    return {
        "schema": "rll.structure_d.legacy_consumption_truth.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "state": "PASS" if not blocking else "FAIL",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "profile": PROFILE,
        "route_scope": run_all_real.LEGACY_ROUTE_SCOPE,
        "active_datasets_declared": active,
        "datasets_consumed_in_objective": ast_consumed,
        "unconsumed_active_datasets": unconsumed_expected,
        "coverage_state": "KNOWN_GAP" if unconsumed_expected else "COMPLETE",
        "coverage_gap_is_success": False,
        "execution_contract": contract,
        "checks": checks,
        "blocking": blocking,
        "F_ok": (
            "Legacy runner reporting is aligned with objective consumption and covariance behavior."
            if not blocking
            else None
        ),
        "F_gap": (
            "The legacy three-axis objective still does not consume real_fsigma8 from the four-axis profile."
            if "real_fsigma8" in unconsumed_expected
            else None
        ),
        "F_next": (
            "Give the three-axis legacy route its own background profile and reserve the four-axis profile for the joint likelihood."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="artifacts/structure-d-falsifier-coverage/legacy-consumption-truth.json",
    )
    args = parser.parse_args()

    receipt = build_receipt()
    out = Path(args.output)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
