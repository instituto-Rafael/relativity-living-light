from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_geometric_mutation_matrix.py"
CONTRACT = ROOT / "data" / "contracts" / "geometric_mutation_matrix.v1.yml"

spec = importlib.util.spec_from_file_location("geometric_mutation_matrix", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def load_contract():
    return module.load_contract(CONTRACT)


def test_contract_keeps_epistemic_boundary():
    contract = load_contract()
    assert contract["claim_allowed"] is False
    assert contract["publication_effect"] == "NONE"
    assert contract["semantics"]["physical_wormhole_claim"] is False
    assert contract["semantics"]["cross_domain_bridge"] == "SENSITIVITY_ONLY_NO_CAUSAL_CLAIM"


def test_mutation_matrix_is_bounded_and_complete():
    rows = module.case_rows(load_contract())
    assert len(rows) == 576
    assert len({row["case_id"] for row in rows}) == len(rows)
    assert all(row["claim_allowed"] is False for row in rows)
    assert all(row["physical_wormhole_claim"] is False for row in rows)


def test_flat_identity_recovers_intrinsic_baseline():
    rows = module.case_rows(load_contract())
    baseline = [
        row
        for row in rows
        if row["geometry_family"] == "flat"
        and row["projection"] == "identity"
        and row["fragment_scale"] == 1.0
    ]
    assert baseline
    for row in baseline:
        assert abs(row["distance_delta"]) < 1.0e-12
        assert abs(row["measure_ratio"] - 1.0) < 1.0e-12


def test_extrinsic_fold_never_mutates_intrinsic_distance():
    rows = module.case_rows(load_contract())
    folds = [row for row in rows if row["projection"] == "extrinsic_fold"]
    assert folds
    assert any(row["shortcut_ratio"] < 1.0 for row in folds)
    for row in folds:
        assert row["shortcut_semantics"] == "EXTRINSIC_ONLY"
        assert np.isclose(row["intrinsic_distance_after"], row["intrinsic_distance_before"])
        assert row["physical_wormhole_claim"] is False


def test_rll_sensitivity_projection_stays_inside_predeclared_bounds():
    contract = load_contract()
    rows = module.case_rows(contract)
    bounds = contract["sensitivity_projection"]["bounds"]
    for row in rows:
        assert bounds["omega_s0"][0] <= row["omega_s0"] <= bounds["omega_s0"][1]
        assert bounds["z_t"][0] <= row["z_t"] <= bounds["z_t"][1]
        assert bounds["w_t"][0] <= row["w_t"] <= bounds["w_t"][1]


def test_full_gate_passes_for_contract_matrix():
    contract = load_contract()
    gate = module.gate_rows(module.case_rows(contract), contract)
    assert gate["status"] == "PASS", gate["failures"]
