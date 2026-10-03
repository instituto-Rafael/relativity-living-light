from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_joint_real_execution_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_joint_real_execution_contract", TOOL)
assert SPEC is not None and SPEC.loader is not None
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


@pytest.fixture(scope="module")
def receipt() -> dict[str, object]:
    return contract.build_receipt()


def test_execution_contract_passes_without_scientific_promotion(receipt: dict[str, object]) -> None:
    assert receipt["state"] == "PASS"
    assert receipt["blocking"] == []
    assert receipt["claim_allowed"] is False
    assert receipt["scientific_confirmation"] is False


def test_all_runtime_axes_have_exact_execution_bindings(receipt: dict[str, object]) -> None:
    assert receipt["axis_set_exact"] is True
    assert set(receipt["observed_axes"]) == {"expansion_Hz", "bao_DESI_DR2", "growth_fsigma8", "cmb_shift"}
    for row in receipt["bindings"]:
        assert row["state"] == "PASS", row
        assert row["checks"]["execution_file_exists"] is True
        assert row["checks"]["runtime_path_matches_manifest"] is True
        assert row["checks"]["execution_sha256_matches"] is True


def test_hz_independent_materialization_is_exact_parent_filter(receipt: dict[str, object]) -> None:
    hz = next(row for row in receipt["bindings"] if row["axis"] == "expansion_Hz")
    assert hz["canonical_exact"] is False
    assert hz["checks"]["derived_materialization_verified"] is True
    derivation = hz["derivation"]
    assert derivation["state"] == "PASS"
    assert derivation["predicate"] == "source == CC_Moresco2022"
    assert derivation["parent_rows"] == 33
    assert derivation["derived_rows"] == 28
    assert derivation["execution_rows"] == 28
    assert derivation["rows_exact_match"] is True


def test_non_derived_axes_bind_to_canonical_source_bytes(receipt: dict[str, object]) -> None:
    for axis in ("bao_DESI_DR2", "growth_fsigma8", "cmb_shift"):
        row = next(item for item in receipt["bindings"] if item["axis"] == axis)
        assert row["canonical_exact"] is True, row
        assert row["checks"]["canonical_execution_binding"] is True


def test_desi_covariance_is_bound_to_runtime_bytes(receipt: dict[str, object]) -> None:
    bao = next(row for row in receipt["bindings"] if row["axis"] == "bao_DESI_DR2")
    assert bao["checks"]["covariance_path_matches_runtime"] is True
    assert bao["checks"]["covariance_sha256_matches"] is True
