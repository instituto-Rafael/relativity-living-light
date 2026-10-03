from __future__ import annotations

import json
from pathlib import Path

from tools import verify_real_source_signatures as verify


def test_source_registry_covers_joint_real_inputs() -> None:
    by_dataset = {row["dataset_id"]: row for row in verify.SOURCES}

    assert by_dataset["real_hz"]["local_path"] == "data/real/Hz_data_real.csv"
    assert by_dataset["real_desi_dr2_bao"]["local_path"] == "data/real/cosmology/desi_dr2_bao_primary_points.csv"
    assert by_dataset["real_fsigma8_6dfgs_anchor"]["local_path"] == "data/real/cosmology/fsigma8_growth_real.csv"
    assert by_dataset["real_cmb_shift"]["local_path"] == "data/real/CMB_shift_real.json"


def test_verification_rows_preserve_failover_on_fetch_failure(monkeypatch) -> None:
    def fake_fetch(_url: str, required_terms: list[str]) -> dict:
        return {
            "ok": False,
            "status_code": 503,
            "final_url": _url,
            "content_type": "",
            "content_length": "",
            "etag": "",
            "last_modified": "",
            "sample_bytes": 0,
            "sample_sha256": "",
            "terms_found": [],
            "required_terms": required_terms,
            "required_terms_ok": False,
            "elapsed_seconds": 0.01,
            "error": "synthetic test outage",
        }

    monkeypatch.setattr(verify, "_fetch_signature", fake_fetch)

    payload = verify.verify_sources()

    assert payload["rows"]
    assert {row["status"] for row in payload["rows"]} == {"source_needs_review"}
    assert all("do not replace" in row["failover_policy"] for row in payload["rows"])


def test_signature_outputs_are_atomic_with_backups(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(verify, "SIGNATURE_JSON", tmp_path / "signatures.json")
    monkeypatch.setattr(verify, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(verify, "RESULT_MD", tmp_path / "result.md")
    monkeypatch.setattr(
        verify,
        "verify_sources",
        lambda: {"schema": "test", "fetch_limit_bytes": 1, "rows": []},
    )

    first = verify.run_verification()
    second = verify.run_verification()

    assert len(first["outputs"]) == 3
    assert all(output["rollback_available"] is True for output in second["outputs"])


def test_joint_manifest_points_to_source_signature_artifacts() -> None:
    manifest = json.loads(
        Path("data/inputs/cosmology_joint/joint_real_inputs_manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["source_signature_manifest"] == "data/real/cosmology/real_source_signatures.json"
    assert "results/audit/real_source_signature_verification.json" in manifest["source_signature_outputs"]


def test_structure_d_and_joint_real_inputs_use_canonical_source_ids() -> None:
    canonical = json.loads(
        Path("data/real/cosmology/observational_sources_manifest.json").read_text(encoding="utf-8")
    )
    canonical_by_id = {
        entry["source_id"]: entry for entry in canonical["canonical_local_real_sources"]
    }
    config = json.loads(
        Path("data/pipelines/structure_d/datasets_config.json").read_text(encoding="utf-8")
    )
    joint = json.loads(
        Path("data/inputs/cosmology_joint/joint_real_inputs_manifest.json").read_text(encoding="utf-8")
    )

    for dataset_id in config["profiles"]["structure_d_real_growth_validation"]["active_datasets"]:
        entry = config["datasets"][dataset_id]
        source = canonical_by_id[entry["source_id"]]
        assert entry["dataset_type"] == "real_observational"
        assert entry["sha256"] == source["sha256"]
        assert entry["local_path"] == source["local_path"]

    assert (
        joint["canonical_observational_sources_manifest"]
        == "data/real/cosmology/observational_sources_manifest.json"
    )
    assert set(joint["source_ids"]) <= set(canonical_by_id)
    assert joint["source_ids"] == [entry["source_id"] for entry in joint["inputs"]]

    for entry in joint["inputs"]:
        source_id = entry["source_id"]
        assert source_id in canonical_by_id
        assert "sha256" not in entry
        assert "local_path" not in entry
        assert "dataset_type" not in entry
        assert entry["execution_path"]
        assert entry["execution_sha256"]

        parent_source_id = entry.get("parent_source_id")
        if parent_source_id is None:
            source = canonical_by_id[source_id]
            assert entry["canonical_source_fields"] == (
                "resolved from canonical_observational_sources_manifest by source_id"
            )
            assert entry["execution_path"] == source["local_path"]
            assert entry["execution_sha256"] == source["sha256"]
            assert "derivation" not in entry
            continue

        assert parent_source_id == source_id
        assert parent_source_id in canonical_by_id
        parent = canonical_by_id[parent_source_id]
        assert entry["canonical_source_fields"] == (
            "parent source resolved from canonical_observational_sources_manifest "
            "by parent_source_id; execution bytes verified independently"
        )
        assert entry["parent_path"] == parent["local_path"]
        assert entry["execution_path"] != parent["local_path"]
        assert entry["execution_sha256"] != parent["sha256"]

        derivation = entry["derivation"]
        assert derivation["type"] == "row_filter"
        assert derivation["predicate"] == "source == CC_Moresco2022"
        assert derivation["preserve_columns"] == ["z", "H_obs", "sigma_H", "source"]
        assert derivation["expected_rows"] == 28
        assert derivation["order_policy"] == "preserve_parent_order"
