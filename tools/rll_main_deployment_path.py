#!/usr/bin/env python3
"""Validate and summarize the RLL main-deployment path without promoting claims."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data/governance/RLL_MAIN_DEPLOYMENT_PATH_20260925_V1.json"
EXPECTED_TOPOLOGY = [
    ("work/*|feature/*|science/*|research/*|engineering/*|governance/*|hotfix/*", "rll/lab"),
    ("rll/lab", "rll/integration"),
    ("rll/integration", "rll/release"),
    ("rll/release", "main"),
]
EXPECTED_COUNTS = {"P0": 5, "P1": 5, "P2": 2}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def validate(payload: dict) -> dict:
    errors = []
    if payload.get("schema") != "rll.main_deployment_path.v1":
        errors.append("SCHEMA_MISMATCH")
    if payload.get("claim_allowed") is not False:
        errors.append("CLAIM_ALLOWED_MUST_BE_FALSE")
    topology = [(x.get("from"), x.get("to")) for x in payload.get("promotion_topology", [])]
    if topology != EXPECTED_TOPOLOGY:
        errors.append("PROMOTION_TOPOLOGY_MISMATCH")

    items = payload.get("work_items", [])
    tokens = [x.get("token") for x in items]
    if len(items) != 12 or len(set(tokens)) != 12:
        errors.append("OPEN_TOKEN_CARDINALITY_MISMATCH")
    counts = Counter(x.get("priority") for x in items)
    if {k: counts.get(k, 0) for k in EXPECTED_COUNTS} != EXPECTED_COUNTS:
        errors.append("PRIORITY_COUNTS_MISMATCH")

    resolved = {x.get("token") for x in payload.get("resolved_facts", [])}
    overlap = sorted(resolved.intersection(tokens))
    if overlap:
        errors.append("RESOLVED_TOKEN_STILL_OPEN:" + ",".join(overlap))

    known = set(tokens) | resolved
    for item in items:
        for dep in item.get("dependencies", []):
            if dep not in known:
                errors.append(f"UNKNOWN_DEPENDENCY:{item.get('token')}->{dep}")
        if not item.get("expected_receipt"):
            errors.append(f"MISSING_RECEIPT:{item.get('token')}")
        if not item.get("close_when"):
            errors.append(f"MISSING_CLOSE_WHEN:{item.get('token')}")
        if not item.get("boundary"):
            errors.append(f"MISSING_BOUNDARY:{item.get('token')}")

    gate = payload.get("global_main_gate", {})
    if gate.get("blocker") != "TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT":
        errors.append("MAIN_GATE_BLOCKER_MISMATCH")
    if "TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT" not in tokens:
        errors.append("PLATFORM_ENFORCEMENT_NOT_OPEN")

    ready = [x["token"] for x in items if str(x.get("readiness", "")).startswith("READY_")]
    blocked = [x["token"] for x in items if str(x.get("readiness", "")).startswith("BLOCKED_")]
    physical = [x["token"] for x in items if x.get("readiness") == "PHYSICAL_DEVICE_REQUIRED"]

    return {
        "schema": "rll.main_deployment_path.receipt.v1",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "valid": not errors,
        "errors": errors,
        "open_count": len(items),
        "priority_counts": dict(sorted(counts.items())),
        "ready_now": ready,
        "blocked_dependency_or_human": blocked,
        "physical_required": physical,
        "main_protected_deployment_allowed": False if gate.get("state") != "RESOLVED" else True,
        "main_blocker": gate.get("blocker"),
        "next_action": "RESOLVE_PLATFORM_ENFORCEMENT_AND_EXECUTE_READY_WAVE" if not errors else "FIX_REGISTRY_ERRORS"
    }

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, default=DEFAULT)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = validate(load(args.registry))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["valid"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
