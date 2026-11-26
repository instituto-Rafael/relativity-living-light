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
    assert receipt["consumer_binding"]["status"] == "VERIFIED_G4_ALIGNMENT_ONLY"
    assert receipt["covariance_index_for_primary_row"] == list(range(11)) + [12, 11]
    assert receipt["native_covariance_binding"]["status"] == "LOCAL_COBAYA_CUSTODY_AND_PERMUTATION_CHECKED"
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


def _mutate_points(tmp_path: Path, mutate) -> Path:
    source = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)
    mutate(rows)
    target = tmp_path / "mutated_points.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return target


def test_guard_rejects_dm_dh_row_swap_even_when_same_covariance_block(tmp_path: Path) -> None:
    def swap(rows):
        rows[1], rows[2] = rows[2], rows[1]
    target = _mutate_points(tmp_path, swap)
    with pytest.raises(ValueError, match="source/order mismatch"):
        build_receipt(ROOT, points_override=target)


def test_guard_rejects_value_inversion_without_row_reordering(tmp_path: Path) -> None:
    def swap_values(rows):
        rows[1]["value"], rows[2]["value"] = rows[2]["value"], rows[1]["value"]
    target = _mutate_points(tmp_path, swap_values)
    with pytest.raises(ValueError, match="source/order mismatch"):
        build_receipt(ROOT, points_override=target)


def test_guard_rejects_reversed_correlation_sign(tmp_path: Path) -> None:
    def flip_sign(rows):
        rows[1]["correlation_coefficient"] = "0.459"
    target = _mutate_points(tmp_path, flip_sign)
    with pytest.raises(ValueError, match="correlation sign/value"):
        build_receipt(ROOT, points_override=target)


def test_guard_rejects_covariance_block_label_swap(tmp_path: Path) -> None:
    def swap_labels(rows):
        for row in rows:
            if row["tracer"] == "LRG1":
                row["covariance_block"] = "DESI_DR2_LRG2_DM_DH"
            elif row["tracer"] == "LRG2":
                row["covariance_block"] = "DESI_DR2_LRG1_DM_DH"
    target = _mutate_points(tmp_path, swap_labels)
    with pytest.raises(ValueError, match="source/observable orientation mismatch"):
        build_receipt(ROOT, points_override=target)


def test_native_covariance_lyman_alignment_has_correct_sigma_axis() -> None:
    receipt = build_receipt(ROOT)
    native_matrix = read_covariance(ROOT / "data/real/desi_dr2_bao_covariance.csv")
    axis = receipt["covariance_index_for_primary_row"]
    # Canonical primary DESI order is Lya DM, DH; Cobaya native is DH, DM.
    assert axis[-2:] == [12, 11]
    sigma_dm = native_matrix[axis[11]][axis[11]] ** 0.5
    sigma_dh = native_matrix[axis[12]][axis[12]] ** 0.5
    assert abs(sigma_dm - 0.531) / 0.531 < 0.01
    assert abs(sigma_dh - 0.101) / 0.101 < 0.01


def test_rx_fallback_identity_matches_canonical_desi_vector() -> None:
    import json
    from tools.build_desi_covariance_order_receipt import (
        read_points, verify_observation_vector_matches_primary
    )
    file = ROOT / "validacao_real/data/desi_dr2_bao_rx.json"
    observed = json.loads(file.read_text(encoding="utf-8"))["points"]
    canonical = read_points(ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv")
    verify_observation_vector_matches_primary(observed, canonical)


def test_rx_fallback_rejects_inverted_lyman_observables() -> None:
    import json
    from tools.build_desi_covariance_order_receipt import (
        read_points, verify_observation_vector_matches_primary
    )
    file = ROOT / "validacao_real/data/desi_dr2_bao_rx.json"
    observed = json.loads(file.read_text(encoding="utf-8"))["points"]
    canonical = read_points(ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv")
    observed[-1], observed[-2] = observed[-2], observed[-1]
    with pytest.raises(ValueError, match="identity mismatch"):
        verify_observation_vector_matches_primary(observed, canonical)
