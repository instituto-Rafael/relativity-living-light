#!/usr/bin/env python3
"""Validate alphaXiv-derived RLL literature actions without promoting external physics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/science/perturbations/RLL_ALPHAXIV_LITERATURE_ACTION_MATRIX_20260923_V1.json"
OUT = ROOT / "results/rll_alphaxiv_literature_action_matrix.json"

REQUIRED_PAPERS = {"2503.14738", "2202.04077", "2607.25539", "2609.03062", "2306.01593", "2506.17411", "1104.2934"}
BIBLIOGRAPHY_FILES = {
    ROOT / "PapersPub/01_cosmology_pantheon_desi/references.bib",
    ROOT / "PapersPub/02_cosmology_growth_structure_d/references.bib",
}

REQUIRED_DATA_AUTHORITIES = {
    "2503.14738": "DESI2025DR2BAO",
    "2202.04077": "Brout2022PantheonPlus",
}

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
    paper_rows = payload.get("papers", [])
    papers = {str(row.get("id")) for row in paper_rows}
    gates = payload.get("mandatory_gates", {})

    bib_text = ""
    bibliography_files_present = True
    for path in sorted(BIBLIOGRAPHY_FILES):
        if not path.exists():
            bibliography_files_present = False
            continue
        bib_text += "\n" + path.read_text(encoding="utf-8")

    citation_keys = [str(row.get("citation_key", "")).strip() for row in paper_rows]
    citation_keys_nonempty = all(citation_keys)
    citation_keys_unique = len(citation_keys) == len(set(citation_keys))
    citation_keys_resolve = citation_keys_nonempty and all(
        ("{" + key + ",") in bib_text for key in citation_keys
    )

    data_authority_map = {
        str(row.get("id")): (row.get("citation_key"), row.get("epistemic_role"))
        for row in paper_rows
    }
    primary_data_authorities_bound = all(
        data_authority_map.get(paper_id) == (key, "DATA_AUTHORITY")
        for paper_id, key in REQUIRED_DATA_AUTHORITIES.items()
    )

    bibliography = payload.get("bibliography", {})
    policy_text = "\n".join(str(x) for x in bibliography.get("citation_policy", []))
    bibliography_not_truth_score = "bibliography_count != evidence_strength" in policy_text
    implementation_refs_do_not_resolve_physics = any(
        "IMPLEMENTATION_REFERENCE" in str(x)
        and ("not imported" in str(x).lower() or "constraints/guides" in str(x).lower())
        for x in bibliography.get("citation_policy", [])
    )

    checks = {
        "schema": payload.get("schema") == "rll.alphaxiv_literature_action_matrix.v1",
        "claim_fail_closed": payload.get("claim_allowed") is False and payload.get("scientific_confirmation") is False,
        "required_papers_present": REQUIRED_PAPERS <= papers,
        "required_gates_present": REQUIRED_GATES <= set(gates),
        "all_required_gates_true": all(gates.get(key) is True for key in REQUIRED_GATES),
        "bibliography_files_present": bibliography_files_present,
        "citation_keys_nonempty": citation_keys_nonempty,
        "citation_keys_unique": citation_keys_unique,
        "citation_keys_resolve_in_canonical_bibtex": citation_keys_resolve,
        "primary_data_authorities_bound": primary_data_authorities_bound,
        "bibliography_not_truth_score": bibliography_not_truth_score,
        "implementation_refs_do_not_resolve_physics": implementation_refs_do_not_resolve_physics,
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
        "citation_keys": sorted(citation_keys),
        "bibliography_files": sorted(str(path.relative_to(ROOT)) for path in BIBLIOGRAPHY_FILES),
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
