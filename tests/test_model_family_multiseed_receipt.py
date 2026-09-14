import copy

import pytest

from data.pipelines.structure_d.model_family_multiseed_receipt import (
    build_receipt,
    load_receipt_contract,
    summaries_to_csv,
)
from data.pipelines.structure_d.model_family_shadow import load_contract


def _row(model, chi2, parameter):
    k = 3
    n = 20
    return {
        "model": model,
        "kind": "core",
        "geometry": "flat",
        "chi2": chi2,
        "AIC": chi2 + 2 * k,
        "AICc": chi2 + 2 * k + (2 * k * (k + 1)) / (n - k - 1),
        "BIC": chi2 + k * 2.995732273553991,
        "N": n,
        "k": k,
        "dof": n - k,
        "chi2_Hz": chi2 * 0.4,
        "chi2_DESI_DR2_BAO": chi2 * 0.6,
        "H0": parameter,
        "Om": 0.3,
        "Ob_h2": 0.022,
        "claim_allowed": False,
    }


def _runs():
    seeds = load_contract()["execution_policy"]["predeclared_seeds"]
    runs = []
    for index, seed in enumerate(seeds):
        runs.append(
            {
                "schema": "rll.cosmology_model_family_shadow.result.v1",
                "runtime_seconds": 1.0 + index,
                "commit_sha": "a" * 40,
                "claim_allowed": False,
                "publication_effect": "NONE",
                "canonical_outputs_modified": False,
                "optimizer": {
                    "name": "scipy.optimize.differential_evolution",
                    "seed": seed,
                    "maxiter": 120,
                    "tol": 1.0e-6,
                    "post_hoc_bound_changes_forbidden": True,
                },
                "input_sha256": {
                    "data/real/Hz_data_real.csv": "1" * 64,
                    "data/real/desi.csv": "2" * 64,
                },
                "model_order": ["FLCDM", "RLL"],
                "rows": [
                    _row("FLCDM", 10.0 + 0.01 * index, 69.9 + 0.01 * index),
                    _row("RLL", 11.0 - 0.01 * index, 70.1 - 0.01 * index),
                ],
            }
        )
    return runs


def test_complete_receipt_preserves_all_predeclared_seeds():
    payload, summaries = build_receipt(
        _runs(), load_receipt_contract(), load_contract()
    )
    assert payload["state"] == "RECEIPTED_MULTI_SEED_COMPARISON"
    assert payload["optimizer"]["seeds"] == [11, 23, 37, 53, 71]
    assert payload["claim_allowed"] is False
    assert payload["publication_effect"] == "NONE"
    assert payload["robust_ranking_ready"] is True
    assert payload["ranking_consensus"] == "FLCDM"
    assert len(payload["receipt_sha256"]) == 64
    assert len(summaries) == 2


def test_input_hash_drift_is_rejected():
    runs = _runs()
    runs[2]["input_sha256"]["data/real/Hz_data_real.csv"] = "9" * 64
    with pytest.raises(ValueError, match="input hashes changed"):
        build_receipt(runs, load_receipt_contract(), load_contract())


def test_seed_omission_is_token_vazio_not_silent_success():
    with pytest.raises(ValueError, match="expected 5 runs"):
        build_receipt(_runs()[:-1], load_receipt_contract(), load_contract())


def test_rank_variation_is_preserved_as_residual():
    runs = _runs()
    runs[-1]["rows"] = [
        _row("FLCDM", 12.0, 69.8),
        _row("RLL", 9.0, 70.2),
    ]
    payload, _ = build_receipt(runs, load_receipt_contract(), load_contract())
    assert payload["ranking_consensus"] == "NO_UNANIMOUS_WINNER"
    assert set(payload["residuals"]["models_with_rank_variation"]) == {"FLCDM", "RLL"}
    assert payload["claim_allowed"] is False


def test_csv_is_deterministic_for_same_summaries():
    payload, summaries = build_receipt(
        _runs(), load_receipt_contract(), load_contract()
    )
    first = summaries_to_csv(summaries)
    second = summaries_to_csv(copy.deepcopy(summaries))
    assert first == second
    assert "claim_allowed" in first.splitlines()[0]
    assert payload["receipt_sha256"]
