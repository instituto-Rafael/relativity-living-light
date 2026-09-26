from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/rx_physics_v2_decision_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ws01_decision_evidence_test", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_ws01_decision_evidence_reduces_only_measured_axes():
    mod = load_module()
    report = mod.build_report()
    assert report["state"] == "EVIDENCE_REDUCED_WS01_PARTIAL"
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["required_measurement_pass"] is True
    assert set(report["terminalizable_axes_from_this_evidence"]) == {
        "hz_dataset",
        "distance_integration",
    }
    assert report["remaining_blocking_axes"] == ["omega_r", "growth_mode"]


def test_hz_33_collapses_exactly_to_independent_28_under_pure_cc_rule():
    mod = load_module()
    hz = mod.dataset_evidence()
    assert hz["passed"] is True
    assert hz["files"]["independent_28"]["rows"] == 28
    assert hz["files"]["raw_33"]["rows"] == 33
    assert hz["selected_from_33_rows"] == 28
    assert hz["row_level_exact_match"] is True
    assert hz["selected_row_digest_28"] == hz["selected_row_digest_from_33"]
    assert len(hz["excluded_rows"]) == 5
    assert all("BAO" in row["source"].upper() for row in hz["excluded_rows"])
    assert all(
        row["absolute_delta"] == 0.0
        for row in hz["fixed_vector_hz_chi2"].values()
    )


def test_omega_r_is_measured_but_not_selected():
    mod = load_module()
    contract = mod._contract()
    evidence = mod.omega_r_evidence(contract)
    assert evidence["state"] == "MEASURED_NO_PHYSICAL_SELECTION"
    assert evidence["null_limit_pass"] is True
    assert evidence["decision_evidence"] == "TOKEN_VAZIO_PHYSICAL_OMEGA_R_AUTHORITY_REQUIRED"
    assert max(
        row["max_relative_delta_H"]
        for row in evidence["sensitivity"].values()
    ) > 0.0


def test_distance_integration_meets_preregistered_tolerance():
    mod = load_module()
    contract = mod._contract()
    evidence = mod.distance_evidence(contract)
    assert evidence["state"] == "PASS_PREREGISTERED_DISTANCE_TOLERANCE"
    assert evidence["passed"] is True
    assert (
        evidence["observed"]["max_relative_error_vs_quad"]
        <= evidence["tolerances"]["max_relative_error_vs_quad"]
    )
    assert (
        evidence["observed"]["max_relative_refinement_delta_2048_to_4096"]
        <= evidence["tolerances"]["max_relative_refinement_delta_2048_to_4096"]
    )


def test_growth_remains_blocked_by_perturbation_backend():
    mod = load_module()
    report = mod.build_report()
    assert report["growth_mode"]["state"] == "TOKEN_VAZIO_UNTIL_WS06"
    assert report["growth_mode"]["promotion_allowed"] is False
