from __future__ import annotations

import csv
from pathlib import Path

import pytest

from tools.build_desi_covariance_order_receipt import ROOT, build_receipt, read_covariance


def test_current_desi_repo_order_binding_is_deterministic() -> None:
    receipt = build_receipt(ROOT)
    assert receipt["state"] == "VERIFIED_REPO_ORDER_BINDING"
    assert receipt["claim_allowed"] is False
    assert receipt["scientific_confirmation"] is False
    assert receipt["vector_rows"] == 13
    assert receipt["covariance_shape"] == [13, 13]
    assert len(receipt["matrix_index_to_vector_row"]) == 13
    assert len(receipt["pair_checks"]) == 6
    assert receipt["unexpected_nonzero_pairs"] == []
    assert receipt["consumer_binding"]["status"] == "VERIFIED_REPO_WIRING"
    assert receipt["provenance_boundary"]["repo_order_binding"] == "VERIFIED"
    assert "BOUNDED" in receipt["provenance_boundary"]["external_primary_covariance_order_metadata"]


def test_order_binding_contains_expected_endpoints() -> None:
    receipt = build_receipt(ROOT)
    mapping = receipt["matrix_index_to_vector_row"]
    assert mapping[0]["tracer"] == "BGS"
    assert mapping[0]["observable"] == "DV_over_rd"
    assert mapping[12]["tracer"] == "Lya"
    assert mapping[12]["observable"] == "DH_over_rd"
    assert len(receipt["ordered_vector_identity_sha256"]) == 64


def test_covariance_reader_rejects_row_index_drift(tmp_path: Path) -> None:
    source = ROOT / "data/real/desi_dr2_bao_covariance.csv"
    rows = list(csv.reader(source.open(newline="", encoding="utf-8")))
    rows[1][0] = "1"
    target = tmp_path / "bad.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    with pytest.raises(ValueError, match="explicit index"):
        read_covariance(target)
