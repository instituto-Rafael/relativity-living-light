from __future__ import annotations

import csv
import json
from pathlib import Path

from tools import rll_real_data_evidence_bridge as bridge

ROOT = Path(__file__).resolve().parents[1]


def test_independent_hz_partition_excludes_bao_derived_rows() -> None:
    with (ROOT / "data/real/cosmology/Hz_cosmic_chronometers_independent.csv").open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    assert len(rows) == 28
    assert {row["source"] for row in rows} == {"CC_Moresco2022"}


def test_growth_wrong_doi_is_superseded_append_only() -> None:
    registry = json.loads((ROOT / "data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json").read_text())
    correction = registry["known_provenance_corrections"][0]
    assert correction["historical_value"].endswith("stw1614")
    assert correction["superseding_source"] == "10.1093/mnras/stv1478"
    assert correction["historical_artifact_mutated"] is False


def test_external_benchmarks_are_not_fit_targets() -> None:
    registry = json.loads((ROOT / "data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json").read_text())
    for source in registry["sources"]:
        if source["id"] in {"DESI_DR2_BAO_2025", "PANTHEON_PLUS_COSMOLOGY"}:
            assert source["benchmark_semantics"] == "context_only_not_fit_target"


def test_data_bridge_passes_but_scientific_claim_remains_blocked() -> None:
    report = bridge.build_report()
    assert report["data_bridge_pass"] is True
    assert report["background_data_ready_for_successor_fit"] is True
    assert report["full_joint_inference_ready"] is False
    assert report["claim_allowed"] is False


def test_desi_covariance_is_positive_definite_and_source_pinned() -> None:
    report = bridge.build_report()
    check = report["checks"]["desi_schema_covariance"]
    assert check["rows"] == 13
    assert check["source_urls_match_registry"] is True
    assert check["covariance_positive_definite"] is True


def test_cmb_source_and_covariance_are_pinned() -> None:
    report = bridge.build_report()
    check = report["checks"]["cmb_distance_prior_identity"]
    assert check["parameter_order"] == ["R", "la", "ob_h2"]
    assert check["source_matches_registry"] is True
    assert check["pass"] is True


def test_latest_desi_lya_update_is_not_double_counted() -> None:
    registry = json.loads((ROOT / "data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json").read_text())
    entry = next(x for x in registry["sources"] if x["id"] == "DESI_DR2_LYA_FULLSHAPE_2026")
    assert entry["arxiv"] == "2607.27410"
    assert entry["published_context"]["w0wa_preference_sigma_DESI_plus_CMB"] == 2.7
    assert entry["combination_policy"].startswith("MUTUALLY_EXCLUSIVE")
    report = bridge.build_report()
    assert report["latest_external_update_policy"]["source_id"] == "DESI_DR2_LYA_FULLSHAPE_2026"
