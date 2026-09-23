#!/usr/bin/env python3
"""Validate alphaXiv-derived RLL literature actions without promoting external physics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/science/perturbations/RLL_ALPHAXIV_LITERATURE_ACTION_MATRIX_20260923_V1.json"
OUT = ROOT / "results/rll_alphaxiv_literature_action_matrix.json"

REQUIRED_PAPERS = {"2607.25539", "2609.03062", "2306.01593", "2506.17411", "1104.2934"}
REQUIRED_GATES = {
    "background_claim_boundary",
    "posterior_or_evidence_gate_before_model_preference",
    "c01_delta_evolution_required",
    "c02_theta_momentum_required",
    "c07_model_consistent_superhorizon_initial_conditions_required",
    "c08_transition_or_crossing_regularity_required",
    "conservation_constraint_bianchi_required",
    "interacting_route_q_deltaq_momentum_transfer_required_if_selected",
    "large_scale_stability_required",
    "independent_class_camb_implementations_required",
    "baseline_lcdm_recovery_required",
    "numerical_convergence_sweep_required",
    "cmb_tt_ee_lensing_and_linear_pk_parity_surface_required",
    "rll_cross_backend_tolerance_preregistered_not_inherited",
    "growth_rsd_lensing_structure_validation_required_before_interaction_or_growth_claim",
}

def build() -> dict:
    payload = json.loads(MATRIX.read_text(encoding="utf-8"))
    papers = {str(row.get("id")) for row in payload.get("papers", [])}
    gates = payload.get("mandatory_gates", {})
    checks = {
        "schema": payload.get("schema") == "rll.alphaxiv_literature_action_matrix.v1",
        "claim_fail_closed": payload.get("claim_allowed") is False and payload.get("scientific_confirmation") is False,
        "required_papers_present": REQUIRED_PAPERS <= papers,
        "required_gates_present": REQUIRED_GATES <= set(gates),
        "all_required_gates_true": all(gates.get(key) is True for key in REQUIRED_GATES),
        "rll_tolerance_not_silently_inherited": payload.get("parity_reference", {}).get("rll_acceptance_tolerance") == "TOKEN_VAZIO_PREREGISTRATION_REQUIRED",
        "perturbation_token_unresolved": "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS" in payload.get("unresolved", []),
    }
    failed = [key for key, value in checks.items() if not value]
    return {
        "schema": "rll.alphaxiv_literature_action_matrix.receipt.v1",
        "state": "PASS_FAIL_CLOSED_LITERATURE_ACTIONS" if not failed else "FAIL_LITERATURE_ACTION_MATRIX",
        "checks": checks,
        "failed_checks": failed,
        "paper_ids": sorted(papers),
        "claim_allowed": False,
        "boundary": "Literature constrains implementation gates and falsifiers; it does not supply missing RLL equations by analogy.",
    }

def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["state"].startswith("PASS") else 2

if __name__ == "__main__":
    raise SystemExit(main())
