from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "rll_structure_d_falsifier_coverage.py"
SPEC = importlib.util.spec_from_file_location("rll_structure_d_falsifier_coverage", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage)


@pytest.fixture(scope="module")
def receipt() -> dict[str, object]:
    return coverage.build_receipt()


def test_canonical_real_profile_has_four_scientific_axes(receipt: dict[str, object]) -> None:
    profile = receipt["canonical_profile"]
    assert profile["profile"] == "structure_d_real_validation"
    assert set(profile["scientific_axes"]) == {"Hz", "BAO", "fsigma8", "CMB_shift"}


def test_joint_route_probes_every_model_across_all_components(receipt: dict[str, object]) -> None:
    expected_components = {"Hz", "DESI_DR2_BAO", "fsigma8", "CMB_shift"}
    probes = receipt["model_probes"]
    assert set(probes) == set(receipt["preferred_full_route"]["models"])

    for model, probe in probes.items():
        assert probe["state"] == "PASS", model
        assert set(probe["components"]) == expected_components
        assert probe["finite"] is True
        assert probe["non_negative"] is True
        assert probe["additive_close"] is True
        assert probe["exact_component_set"] is True


def test_covariance_falsifiers_are_numerically_ready(receipt: dict[str, object]) -> None:
    by_id = {row["id"]: row for row in receipt["falsifiers"]}
    assert by_id["F-COVERAGE-03"]["state"] == "PASS"
    assert by_id["F-COVERAGE-04"]["state"] == "PASS"


def test_legacy_route_gap_is_explicit_and_cannot_authorize_claim(receipt: dict[str, object]) -> None:
    legacy = receipt["legacy_route"]
    assert legacy["claim_allowed"] is False
    assert "real_fsigma8" in legacy["unconsumed_active_dataset_ids"]

    by_id = {row["id"]: row for row in receipt["falsifiers"]}
    assert by_id["F-COVERAGE-05"]["state"] == "KNOWN_GAP"
    assert by_id["F-COVERAGE-05"]["claim_allowed"] is False


def test_receipt_is_pass_limited_not_scientific_confirmation(receipt: dict[str, object]) -> None:
    assert receipt["state"] == "PASS_LIMITED"
    assert receipt["blocking_falsifiers"] == []
    assert receipt["known_gaps"] == ["F-COVERAGE-05"]
    assert receipt["claim_allowed"] is False
    assert receipt["scientific_confirmation"] is False
    assert receipt["fit_executed"] is False
