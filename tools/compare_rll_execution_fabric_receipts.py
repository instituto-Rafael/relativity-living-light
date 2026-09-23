#!/usr/bin/env python3
"""Compare a GitHub Actions Rx execution artifact with a physical Termux capsule."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rx.kernel import dump_json

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("%s root must be object" % path)
    return payload


def formula_ids(path, key):
    payload = load(path)
    return sorted(str(row.get("formula_id")) for row in payload.get(key, []))


def compare(actions_dir, termux_dir):
    actions_dir = Path(actions_dir).resolve()
    termux_run = Path(termux_dir).resolve() / "run1"

    ar = load(actions_dir / "receipt.json")
    tr = load(termux_run / "receipt.json")
    am = load(actions_dir / "metrics.json")
    tm = load(termux_run / "metrics.json")
    ac = load(actions_dir / "covariance_contract.json")
    tc = load(termux_run / "covariance_contract.json")

    checks = {
        "actions_pass": ar.get("status") == "PASS",
        "termux_pass": tr.get("status") == "PASS",
        "physics_contract_equal": ar.get("physics_contract") == tr.get("physics_contract"),
        "qualified_regimes_equal": ar.get("qualified_regimes") == tr.get("qualified_regimes"),
        "dispersion_operator_equal": ar.get("dispersion_operator") == tr.get("dispersion_operator"),
        "selected_formula_ids_equal": formula_ids(actions_dir / "selected_formulas.json", "selected")
            == formula_ids(termux_run / "selected_formulas.json", "selected"),
        "rejected_formula_ids_equal": formula_ids(actions_dir / "rejected_formulas.json", "rejected")
            == formula_ids(termux_run / "rejected_formulas.json", "rejected"),
        "selected_formula_count_equal": am.get("selected_formula_count") == tm.get("selected_formula_count"),
        "rejected_formula_count_equal": am.get("rejected_formula_count") == tm.get("rejected_formula_count"),
        "covariance_contract_equal": ac == tc,
        "claim_boundaries_closed": ar.get("claim_allowed") is False and tr.get("claim_allowed") is False,
    }
    actions_routes = {row.get("route_id"): row for row in ar.get("route_results", [])}
    termux_routes = {row.get("route_id"): row for row in tr.get("route_results", [])}
    checks["route_ids_equal"] = sorted(actions_routes) == sorted(termux_routes)
    checks["route_statuses_equal"] = checks["route_ids_equal"] and all(
        actions_routes[key].get("status") == termux_routes[key].get("status")
        for key in actions_routes
    )
    diagnostics = {
        key: {
            "stdout_sha256_equal": actions_routes[key].get("stdout_sha256") == termux_routes.get(key, {}).get("stdout_sha256"),
            "stderr_sha256_equal": actions_routes[key].get("stderr_sha256") == termux_routes.get(key, {}).get("stderr_sha256"),
        }
        for key in sorted(actions_routes)
    }

    failed = [key for key, value in checks.items() if not value]
    return {
        "schema": "rll.rx.cross_runtime_execution_fabric_comparison.v1",
        "state": "PASS_CROSS_RUNTIME_SEMANTIC_PARITY" if not failed else "FAIL_CROSS_RUNTIME_SEMANTIC_PARITY",
        "checks": checks,
        "failed_checks": failed,
        "route_digest_diagnostics": diagnostics,
        "digest_boundary": "Route stdout/stderr digest equality is diagnostic; semantic checks above are the blocking contract.",
        "actions_repo_ref": ar.get("repo_ref"),
        "termux_repo_ref": tr.get("repo_ref"),
        "physics_contract": ar.get("physics_contract"),
        "qualified_regimes": ar.get("qualified_regimes"),
        "claim_allowed": False,
        "boundary": "Cross-runtime implementation parity only; not scientific validation or model-selection evidence.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("actions_run_dir", type=Path)
    parser.add_argument("termux_capsule_dir", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "results/rll_execution_fabric_cross_runtime_comparison.json")
    args = parser.parse_args(argv)
    payload = compare(args.actions_run_dir, args.termux_capsule_dir)
    dump_json(args.output, payload)
    print(payload["state"])
    print("claim_allowed=False")
    print("wrote", args.output)
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
