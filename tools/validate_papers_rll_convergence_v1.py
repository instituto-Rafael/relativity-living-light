#!/usr/bin/env python3
"""Fail-closed validator for Papers <-> RLL convergence V1.

This guard validates routing metadata only. It does not prove authorship,
mathematics, cosmology, execution, or scientific claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "governance" / "PAPERS_RLL_CONVERGENCE_V1.json"

REQUIRED_INVARIANTS = {
    "SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM",
    "TOKEN_VAZIO != 0",
    "IMPLEMENTED_UNTESTED != PASS",
    "SILENT_STEP = GAP",
    "CROSS_REPO_POINTER != TRANSFERRED_PROOF",
    "AUTHORIAL_CANDIDATE != SCIENTIFIC_VALIDATION",
    "MATHEMATICAL_VALIDITY != COSMOLOGICAL_RELEVANCE",
    "GEOMETRY_EXECUTION != RLL_EXECUTION",
}
EXPECTED_CANDIDATES = {"AC-01", "AC-02", "AC-03", "AC-04"}


def fail(message: str) -> None:
    raise SystemExit(f"papers-rll convergence gate failed: {message}")


def load_contract(path: Path = CONTRACT) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("contract root must be an object")
    return data


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "papers_rll.convergence.v1":
        errors.append("unexpected schema")
    if data.get("claim_allowed") is not False:
        errors.append("top-level claim_allowed must remain false")
    if data.get("state") != "AUDIT_FAIL_CLOSED":
        errors.append("state must remain AUDIT_FAIL_CLOSED")

    missing = sorted(REQUIRED_INVARIANTS - set(data.get("invariants", [])))
    if missing:
        errors.append(f"missing invariants: {missing}")

    authority = data.get("authority", {})
    expected_authority = {
        "research_synthesis": "rafaelmeloreisnovo/papers",
        "formal_math": "rafaelmeloreisnovo/Matem-tica-",
        "scientific_cosmology": "instituto-Rafael/relativity-living-light",
    }
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            errors.append(f"authority.{key} must be {expected}")

    routes = data.get("authorial_candidate_routes", [])
    if not isinstance(routes, list):
        errors.append("authorial_candidate_routes must be a list")
        routes = []

    ids = {r.get("id") for r in routes if isinstance(r, dict)}
    if ids != EXPECTED_CANDIDATES:
        errors.append(f"candidate ids must be exactly {sorted(EXPECTED_CANDIDATES)}")

    for route in routes:
        if not isinstance(route, dict):
            errors.append("candidate route must be an object")
            continue
        rid = route.get("id", "<missing>")
        if route.get("claim_allowed") is not False:
            errors.append(f"{rid}: claim_allowed must remain false")

        rll_state = str(route.get("rll_state", ""))
        math_gate = route.get("math_gate")
        domain_relevance = route.get("domain_relevance")
        routed = rll_state.startswith("ROUTED") or rll_state in {"ACCEPTED", "ACTIVE", "PASS"}

        if routed:
            if math_gate != "PASS":
                errors.append(f"{rid}: routed candidate requires math_gate=PASS")
            if domain_relevance != "ESTABLISHED":
                errors.append(f"{rid}: routed candidate requires domain_relevance=ESTABLISHED")
            for field in ("exact_source_binding", "target_rll_gate", "falsifier"):
                value = route.get(field)
                if not isinstance(value, str) or not value.strip() or "TOKEN_VAZIO" in value:
                    errors.append(f"{rid}: routed candidate requires non-empty {field}")
        elif domain_relevance != "ESTABLISHED" and "NOT_ROUTED" not in rll_state:
            errors.append(f"{rid}: unresolved domain relevance must remain NOT_ROUTED")

    snapshot = data.get("rll_gate_snapshot", {})
    for gate in ("G7", "G9", "G10", "G11"):
        if "TOKEN_VAZIO" not in str(snapshot.get(gate, "")):
            errors.append(f"{gate}: expected TOKEN_VAZIO executor state in frozen snapshot")

    topology = data.get("branch_topology_snapshot", {})
    if topology.get("state") != "BRANCH_TOPOLOGY_GAP":
        errors.append("branch topology gap must remain explicit until reconciled")
    rules = set(topology.get("rules", []))
    for rule in {
        "NO_MASS_MERGE_TO_HIDE_DIVERGENCE",
        "NO_DIRECT_MAIN_PROMOTION_FROM_WORK_BRANCH",
        "RECONCILE_BRANCH_AUTHORITY_BEFORE_TRANSIT",
    }:
        if rule not in rules:
            errors.append(f"missing branch-topology rule: {rule}")

    if topology.get("state") == "BRANCH_TOPOLOGY_GAP":
        for route in routes:
            if isinstance(route, dict):
                rll_state = str(route.get("rll_state", ""))
                if rll_state.startswith("ROUTED") or rll_state in {"ACCEPTED", "ACTIVE", "PASS"}:
                    errors.append(f"{route.get('id', '<missing>')}: routed candidate forbidden while BRANCH_TOPOLOGY_GAP is open")

    negative = set(data.get("negative_evidence_preserved", []))
    if "G6_observed_checkpoint_blocked_by_MCMC_convergence" not in negative:
        errors.append("G6 blocked convergence evidence must be preserved")
    if "GEOM_TO_RLL_EVIDENCE_TRANSFER_FORBIDDEN" not in negative:
        errors.append("geometry-to-RLL evidence-transfer prohibition must be preserved")

    return errors


def main() -> int:
    errors = validate(load_contract())
    if errors:
        fail("; ".join(errors))
    print("PASS: Papers-RLL convergence contract is fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
