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
LITERATURE = ROOT / "data/science/perturbations/RLL_ALPHAXIV_LITERATURE_ACTION_MATRIX_20260923_V1.json"
OUT = ROOT / "results/rll_perturbation_solver_readiness.json"

REQUIRED_HARD_BLOCKERS = {
    "C01_DELTA_S",
    "C02_THETA_S",
    "C07_GAUGE_AND_INITIAL_CONDITIONS",
    "C08_TRANSITION_REGULARIZATION",
}

REQUIRED_LITERATURE_GATES = {
    "background_claim_boundary",
    "posterior_or_evidence_gate_before_model_preference",
    "c07_model_consistent_superhorizon_initial_conditions_required",
    "conservation_constraint_bianchi_required",
    "large_scale_stability_required",
    "independent_class_camb_implementations_required",
    "baseline_lcdm_recovery_required",
    "numerical_convergence_sweep_required",
    "cmb_tt_ee_lensing_and_linear_pk_parity_surface_required",
    "rll_cross_backend_tolerance_preregistered_not_inherited",
    "growth_rsd_lensing_structure_validation_required_before_interaction_or_growth_claim",
}


def build():
    contract = load_json(CONTRACT)
    successor = load_json(SUCCESSOR)
    class_camb = load_json(CLASS_CAMB)
    literature = load_json(LITERATURE)

    if contract.get("schema") != "rll.perturbation_closure_contract.v1":
        raise ValueError("unexpected perturbation closure contract")
    if successor.get("schema") != "rll.perturbation_closure_successor.v2":
        raise ValueError("unexpected perturbation successor")
    if class_camb.get("schema") != "rll.class_camb_implementation_successor.v2":
        raise ValueError("unexpected CLASS/CAMB successor")
    if literature.get("schema") != "rll.alphaxiv_literature_action_matrix.v1":
        raise ValueError("unexpected literature action matrix")
    for payload in (contract, successor, class_camb, literature):
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
    literature_gates = literature.get("mandatory_gates", {})
    literature_gate_set_complete = REQUIRED_LITERATURE_GATES <= set(literature_gates)
    literature_gates_fail_closed = literature_gate_set_complete and all(
        literature_gates.get(key) is True for key in REQUIRED_LITERATURE_GATES
    )
    parity_tolerance_unresolved = (
        literature.get("parity_reference", {}).get("rll_acceptance_tolerance")
        == "TOKEN_VAZIO_PREREGISTRATION_REQUIRED"
    )

    unlock = (
        not open_slots
        and not missing_blocker_labels
        and conservation_blocker_declared
        and literature_gates_fail_closed
        and successor.get("token_resolution") == "RESOLVED"
    )

    checks = {
        "required_slots_present": not missing_blocker_labels,
        "open_slots_preserved": set(open_slots) == REQUIRED_HARD_BLOCKERS,
        "constraint_bianchi_gate_declared": conservation_blocker_declared,
        "literature_gate_set_complete": literature_gate_set_complete,
        "literature_gates_fail_closed": literature_gates_fail_closed,
        "rll_parity_tolerance_not_silently_inherited": parity_tolerance_unresolved,
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
            "derive gauge-consistent pressure perturbation relation from the frozen closure",
            "derive super-horizon initial conditions and constraint-compatible mode; do not copy GR ICs by default",
            "if interacting route B is selected, freeze Q, deltaQ and momentum-transfer components in one covariant convention",
            "derive perturbative transition/crossing regularization C08 without arbitrary hidden epsilon",
            "execute super-horizon/large-scale stability sweep",
            "execute perturbed conservation/constraint/Bianchi residual gate",
            "freeze one solver-neutral equation contract",
            "only then hand independently to CLASS and CAMB implementations",
            "after both backends exist: recover the same LambdaCDM baseline, run precision-convergence sweeps, preregister RLL parity tolerance, then compare TT/EE/lensing and linear P(k)"
        ],
        "class_state": class_state,
        "camb_state": camb_state,
        "class_camb_unlock": bool(unlock),
        "literature_authority": {
            "matrix": str(LITERATURE.relative_to(ROOT)),
            "paper_ids": [row.get("id") for row in literature.get("papers", [])],
            "rll_parity_tolerance": literature.get("parity_reference", {}).get("rll_acceptance_tolerance"),
        },
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
