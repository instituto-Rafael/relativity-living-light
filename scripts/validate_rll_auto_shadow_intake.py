#!/usr/bin/env python3
"""Fail-closed validator for automatic RLL shadow intake governance."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/contracts/rll_auto_shadow_intake.v1.json"
CANDIDATE = ROOT / "data/inputs/cosmology_joint/five_family_42_hyperform_shadow_candidate.v1.json"

PROTECTED = {
    "src/rll/cosmology.py",
    "src/rll/model.py",
    "src/rll/likelihood.py",
    "scripts/joint_mcmc.py",
    "scripts/bayes_analysis.py",
    "scripts/compute_bayes_factor_bic_proxy.py",
    "results/ci/",
    "data/real/cosmology/",
}
FAMILIES = {"TRIG", "FIB", "TOROID", "DIZIMA", "BITRAF"}


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate():
    errors = []
    contract = load(CONTRACT)
    candidate = load(CANDIDATE)

    if contract.get("status") != "ACTIVE_GOVERNED":
        errors.append("auto-shadow contract must be ACTIVE_GOVERNED")
    for key in ("claim_allowed", "direct_model_integration_allowed", "promotion_allowed"):
        if contract.get(key) is not False:
            errors.append(f"contract {key} must be false")
        if candidate.get(key) is not False:
            errors.append(f"candidate {key} must be false")

    protected = set(contract.get("protected_target_prefixes", []))
    if protected != PROTECTED:
        errors.append("protected target set mismatch")

    if set(candidate.get("canonical_families", [])) != FAMILIES:
        errors.append("canonical family set must be exactly TRIG/FIB/TOROID/DIZIMA/BITRAF")

    objects = candidate.get("objects", {})
    corr = objects.get("correlation_matrix", {})
    hyper = objects.get("hyperform_graph", {})
    if corr.get("raw_numeric_matrix") != "TOKEN_VAZIO_NOT_AVAILABLE":
        errors.append("raw correlation matrix must remain TOKEN_VAZIO until bytes are supplied")
    if corr.get("index_to_formula_map") != "TOKEN_VAZIO_NOT_AVAILABLE":
        errors.append("index map must remain TOKEN_VAZIO until supplied")
    if hyper.get("adjacency_or_edge_list") != "TOKEN_VAZIO_NOT_AVAILABLE":
        errors.append("42-node edge list must remain TOKEN_VAZIO until supplied")
    if corr.get("k5_state") != "PLAUSIBLE_NOT_PROVEN":
        errors.append("k=5 must not be promoted before label-blind cluster selection")

    gate = candidate.get("promotion_gate", {})
    required_true = {
        "requires_raw_matrix",
        "requires_index_map",
        "requires_edge_list_for_42_graph_claim",
        "requires_label_blind_k_selection",
        "requires_out_of_sample_or_resampling_stability",
        "requires_permutation_baseline",
    }
    if any(gate.get(k) is not True for k in required_true):
        errors.append("promotion gate is incomplete")

    return errors


def main():
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: RLL automatic shadow intake remains fail-closed")
    print("claim_allowed=false")
    print("direct_model_integration_allowed=false")


if __name__ == "__main__":
    main()
