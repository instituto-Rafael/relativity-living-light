#!/usr/bin/env python3
"""Fail-closed solver-handoff gate for the RLL perturbation closure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rx.kernel import dump_json, load_json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/science/perturbations/RLL_PERTURBATION_CLOSURE_CONTRACT_20260808_V1.json"
SUCCESSOR = ROOT / "data/science/perturbations/RLL_PERTURBATION_CLOSURE_SUCCESSOR_20260922_V2.json"
CLASS_CAMB = ROOT / "data/science/perturbations/RLL_CLASS_CAMB_IMPLEMENTATION_SUCCESSOR_20260922_V2.json"
OUT = ROOT / "results/rll_perturbation_solver_readiness.json"

REQUIRED_HARD_BLOCKERS = {
    "C01_DELTA_S",
    "C02_THETA_S",
    "C07_GAUGE_AND_INITIAL_CONDITIONS",
    "C08_TRANSITION_REGULARIZATION",
}


def build():
    contract = load_json(CONTRACT)
    successor = load_json(SUCCESSOR)
    class_camb = load_json(CLASS_CAMB)

    if contract.get("schema") != "rll.perturbation_closure_contract.v1":
        raise ValueError("unexpected perturbation closure contract")
    if successor.get("schema") != "rll.perturbation_closure_successor.v2":
        raise ValueError("unexpected perturbation successor")
    if class_camb.get("schema") != "rll.class_camb_implementation_successor.v2":
        raise ValueError("unexpected CLASS/CAMB successor")
    for payload in (contract, successor, class_camb):
        if payload.get("claim_allowed") is not False:
            raise ValueError("all perturbation handoff contracts must remain claim_allowed=false")

    slots = successor.get("slot_delta", {})
    if not isinstance(slots, dict):
        raise ValueError("slot_delta missing")

    open_slots = {
        key: value for key, value in slots.items()
        if key in REQUIRED_HARD_BLOCKERS
        and ("OPEN" in str(value) or "PARTIAL" in str(value))
    }
    missing_blocker_labels = sorted(REQUIRED_HARD_BLOCKERS - set(open_slots))

    class_state = str(class_camb.get("class_path", {}).get("state", "TOKEN_VAZIO"))
    camb_state = str(class_camb.get("camb_path", {}).get("state", "TOKEN_VAZIO"))
    solver_outputs_blocked = (
        class_state == "NOT_IMPLEMENTED_RLL_PERTURBATIONS"
        and camb_state == "NOT_IMPLEMENTED_RLL_PERTURBATIONS"
    )

    conservation_blocker_declared = any(
        "Bianchi" in str(value) or "constraint" in str(value)
        for value in successor.get("hard_blockers_for_class_camb", [])
    )

    unlock = (
        not open_slots
        and not missing_blocker_labels
        and conservation_blocker_declared
        and successor.get("token_resolution") == "RESOLVED"
    )

    checks = {
        "required_slots_present": not missing_blocker_labels,
        "open_slots_preserved": set(open_slots) == REQUIRED_HARD_BLOCKERS,
        "constraint_bianchi_gate_declared": conservation_blocker_declared,
        "class_camb_outputs_blocked_while_incomplete": solver_outputs_blocked,
        "token_not_falsely_resolved": successor.get("token_resolution") == "NOT_RESOLVED",
        "class_camb_unlock_false": successor.get("class_camb_state") == "BLOCKED_BY_PARTIAL_CLOSURE",
    }
    failed = [key for key, value in checks.items() if not value]

    return {
        "schema": "rll.perturbation_solver_readiness.v1",
        "state": (
            "BLOCKED_AS_EXPECTED_PHYSICAL_DERIVATION_REQUIRED"
            if not failed and not unlock
            else "READY_FOR_INDEPENDENT_SOLVER_IMPLEMENTATION"
            if not failed and unlock
            else "FAIL_CONTRACT_INCONSISTENCY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "open_hard_slots": open_slots,
        "derivation_order": [
            "freeze gauge and variable normalization",
            "derive C01 delta_s evolution from the frozen conserved A1.1 equations",
            "derive C02 theta_s Euler/momentum evolution from the same equations",
            "derive super-horizon initial conditions and constraint-compatible mode",
            "derive perturbative transition regularization C08 without arbitrary hidden epsilon",
            "execute perturbed conservation/constraint/Bianchi residual gate",
            "freeze one solver-neutral equation contract",
            "only then hand independently to CLASS and CAMB implementations"
        ],
        "class_state": class_state,
        "camb_state": camb_state,
        "class_camb_unlock": bool(unlock),
        "token": "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
        "claim_allowed": False,
        "boundary": "This gate proves only whether the solver handoff is permitted. It never invents C01/C02/C07/C08 equations.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        dump_json(OUT, payload)
    print(json.dumps({
        "state": payload["state"],
        "open_hard_slots": sorted(payload["open_hard_slots"]),
        "class_camb_unlock": payload["class_camb_unlock"],
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", OUT.relative_to(ROOT))
    return 0 if payload["state"] != "FAIL_CONTRACT_INCONSISTENCY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
