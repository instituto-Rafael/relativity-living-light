from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "rll_qcd_primordial_gate.py"


def load_gate():
    spec = importlib.util.spec_from_file_location("rll_qcd_primordial_gate", GATE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_payload(*, source_kind: str = "real_data", bound: float = 0.01, verified: bool = True):
    return {
        "schema": "rll.qcd_primordial_input.v1",
        "evidence": {
            "source_kind": source_kind,
            "checksum_verified": verified,
            "baseline_equivalent": verified,
            "eos_provenance_verified": verified,
        },
        "constraint": {
            "max_abs_delta_h": bound,
            "verified": verified,
        },
        "reference": {"T_MeV": 150.0, "g_star_s": 20.0},
        "rows": [
            {
                "T_MeV": 150.0,
                "epsilon_background_GeV_fm3": 0.3,
                "epsilon_rll_GeV_fm3": 0.003,
                "g_star_s": 20.0,
            }
        ],
    }


def test_synthetic_or_unverified_evidence_is_token_vazio() -> None:
    gate = load_gate()
    payload = base_payload(source_kind="synthetic_fixture", verified=False)
    receipt = gate.evaluate_gate(payload)
    assert receipt["local_gate_status"] == "TOKEN_VAZIO"
    assert receipt["pspi_action"] == "HOLD_MISSING_EVIDENCE"
    assert receipt["descendant_input_allowed"] is False
    assert receipt["global_scientific_claim_allowed"] is False


def test_verified_local_result_can_pass_without_global_claim() -> None:
    gate = load_gate()
    receipt = gate.evaluate_gate(base_payload())
    assert receipt["local_gate_status"] == "PASS"
    assert receipt["pspi_action"] == "ALLOW_LOCAL_RESULT_ONLY"
    assert receipt["descendant_input_allowed"] is True
    assert receipt["global_scientific_claim_allowed"] is False
    assert abs(receipt["rows"][0]["delta_h"]) < 0.01


def test_verified_bound_exceedance_is_falsified_and_quarantined() -> None:
    gate = load_gate()
    payload = base_payload()
    payload["rows"][0]["epsilon_rll_GeV_fm3"] = 0.03
    receipt = gate.evaluate_gate(payload)
    assert receipt["local_gate_status"] == "FALSIFIED"
    assert receipt["pspi_action"] == "QUARANTINE_FROM_DESCENDANTS"
    assert receipt["descendant_input_allowed"] is False
    assert "DELTA_H_EXCEEDS_VERIFIED_BOUND" in receipt["decision_basis"]["reason_codes"]


def test_missing_constraint_bound_stays_token_vazio() -> None:
    gate = load_gate()
    payload = base_payload()
    payload["constraint"]["max_abs_delta_h"] = None
    receipt = gate.evaluate_gate(payload)
    assert receipt["local_gate_status"] == "TOKEN_VAZIO"
    assert "CONSTRAINT_BOUND_TOKEN_VAZIO" in receipt["decision_basis"]["reason_codes"]


def test_split_qcd_and_radiation_background_is_rejected() -> None:
    gate = load_gate()
    payload = base_payload()
    payload["rows"][0]["rho_QCD_GeV_fm3"] = 0.2
    with pytest.raises(gate.GateInputError, match="double counting"):
        gate.evaluate_gate(payload)


def test_scale_factor_reference_is_exactly_one() -> None:
    gate = load_gate()
    receipt = gate.evaluate_gate(base_payload())
    assert receipt["rows"][0]["a_over_a_ref"] == pytest.approx(1.0)
