from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from rll.orcid_vector import (
    TOKEN_VAZIO,
    VECTOR_DIMENSIONS,
    VectorStore,
    canonicalize_orcid,
    classify_disciplines,
    hash_embedding,
    load_json,
    parse_crossref,
    parse_datacite,
    parse_openalex,
    validate_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
ORCID_FIXTURE = ROOT / "data" / "examples" / "orcid_record_synthetic.json"
CROSSREF_FIXTURE = ROOT / "data" / "examples" / "crossref_rll_synthetic.json"
DATACITE_FIXTURE = ROOT / "data" / "examples" / "datacite_rll_synthetic.json"
OPENALEX_FIXTURE = ROOT / "data" / "examples" / "openalex_rll_synthetic.json"
FIXTURE_ORCID = "0000-0000-0000-001X"


def test_orcid_checksum_validation() -> None:
    assert canonicalize_orcid(FIXTURE_ORCID) == FIXTURE_ORCID
    assert canonicalize_orcid(f"https://orcid.org/{FIXTURE_ORCID}") == FIXTURE_ORCID
    with pytest.raises(ValueError, match="Checksum"):
        canonicalize_orcid("0000-0000-0000-0010")


def test_embedding_is_deterministic_and_32_dimensional() -> None:
    first = hash_embedding("quantum gravity tensor")
    second = hash_embedding("quantum gravity tensor")
    assert first == second
    assert len(first) == VECTOR_DIMENSIONS
    assert abs(sum(value * value for value in first) - 1.0) < 1.0e-9


def test_multidiscipline_classification_keeps_parent_physics() -> None:
    labels, confidence = classify_disciplines(
        "Quantum spin and classical mechanics coupled to biology and physiology"
    )
    assert "physics" in labels
    assert "physics.quantum" in labels
    assert "physics.classical" in labels
    assert "biology" in labels
    assert "physiology" in labels
    assert confidence


def test_orcid_ingest_is_idempotent_and_claim_locked(tmp_path: Path) -> None:
    record = load_json(ORCID_FIXTURE)
    db = tmp_path / "orcid.sqlite3"
    with VectorStore(db) as store:
        first = store.ingest_orcid_record(record, FIXTURE_ORCID)
        second = store.ingest_orcid_record(record, FIXTURE_ORCID)
        assert first == {"works_seen": 2, "created": 2, "unchanged": 0, "token_vazio": 0}
        assert second == {"works_seen": 2, "created": 0, "unchanged": 2, "token_vazio": 0}
        status = store.status()
        assert status["logical_artifacts"] == 2
        assert status["artifact_revisions"] == 2
        assert status["event_chain_ok"] is True
        claims = store.connection.execute(
            "SELECT DISTINCT claim_allowed FROM artifacts"
        ).fetchall()
        assert [row[0] for row in claims] == [0]

        with pytest.raises(sqlite3.IntegrityError):
            store.connection.execute(
                """
                INSERT INTO artifacts(
                    logical_id, revision, owner_orcid, title,
                    disciplines_json, discipline_confidence_json,
                    classification_method, metadata_state,
                    claim_allowed, content_sha256, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    "forbidden:test",
                    1,
                    FIXTURE_ORCID,
                    "Forbidden promotion",
                    "[]",
                    "{}",
                    "test",
                    TOKEN_VAZIO,
                    "a" * 64,
                    "2026-07-26T00:00:00+00:00",
                ),
            )


def test_enrichment_creates_append_only_revision_and_verified_metadata(tmp_path: Path) -> None:
    db = tmp_path / "orcid.sqlite3"
    with VectorStore(db) as store:
        store.ingest_orcid_record(load_json(ORCID_FIXTURE), FIXTURE_ORCID)
        logical_id = "doi:10.5281/zenodo.17188137"
        artifact_id, created, validation = store.enrich_artifact(
            logical_id,
            load_json(CROSSREF_FIXTURE),
            provider="crossref",
        )
        assert artifact_id > 0
        assert created is True
        assert validation.state == "VERIFIED_METADATA"
        assert validation.score >= 0.78
        latest = store.latest_artifact(logical_id)
        assert latest is not None
        assert latest["revision"] == 2
        assert latest["parent_artifact_id"] is not None
        assert "synthetic metadata fixture" in latest["abstract"].casefold()
        assert latest["claim_allowed"] == 0

        _, created_again, validation_again = store.enrich_artifact(
            logical_id,
            load_json(CROSSREF_FIXTURE),
            provider="crossref",
        )
        assert created_again is False
        assert validation_again.state == "VERIFIED_METADATA"
        assert store.latest_artifact(logical_id)["revision"] == 2


def test_openalex_parser_and_metadata_validator() -> None:
    parsed = parse_openalex(load_json(OPENALEX_FIXTURE))
    assert parsed["doi"] == "10.5281/zenodo.17188137"
    assert parsed["publication_year"] == 2025
    assert parsed["is_retracted"] is False
    assert "OpenAlex fixture" in parsed["abstract"]
    base = {
        "title": parsed["title"],
        "doi": parsed["doi"],
        "publication_year": 2025,
    }
    validation = validate_metadata(base, parsed, FIXTURE_ORCID)
    assert validation.state == "VERIFIED_METADATA"
    assert validation.details["owner_orcid_match"] is True


def test_datacite_parser_matches_zenodo_doi_and_orcid() -> None:
    parsed = parse_datacite(load_json(DATACITE_FIXTURE))
    assert parsed["doi"] == "10.5281/zenodo.17188137"
    assert parsed["journal"] == "Zenodo"
    assert parsed["authors"][0]["orcid"] == FIXTURE_ORCID
    validation = validate_metadata(
        {"title": parsed["title"], "doi": parsed["doi"], "publication_year": 2025},
        parsed,
        FIXTURE_ORCID,
    )
    assert validation.state == "VERIFIED_METADATA"


def test_crossref_parser_detects_author_orcid() -> None:
    parsed = parse_crossref(load_json(CROSSREF_FIXTURE))
    assert parsed["doi"] == "10.5281/zenodo.17188137"
    assert parsed["authors"][0]["orcid"] == FIXTURE_ORCID
    assert parsed["publication_year"] == 2025


def test_vector_search_and_discipline_filter(tmp_path: Path) -> None:
    db = tmp_path / "orcid.sqlite3"
    with VectorStore(db) as store:
        store.ingest_orcid_record(load_json(ORCID_FIXTURE), FIXTURE_ORCID)
        results = store.search(
            "quantum tensor physiology",
            disciplines=["physics.quantum"],
            owner_orcid=FIXTURE_ORCID,
        )
        assert results
        assert results[0]["logical_id"] == f"orcid:{FIXTURE_ORCID}:put:43"
        assert results[0]["claim_allowed"] is False


def test_export_preserves_write_gate_and_event_chain(tmp_path: Path) -> None:
    db = tmp_path / "orcid.sqlite3"
    with VectorStore(db) as store:
        store.ingest_orcid_record(load_json(ORCID_FIXTURE), FIXTURE_ORCID)
        exported = store.export_candidates(FIXTURE_ORCID)
        assert exported["claim_allowed"] is False
        assert len(exported["works"]) == 2
        assert all(
            item["orcid_write_state"] == "TOKEN_VAZIO_MEMBER_API_OR_MANUAL_REVIEW"
            for item in exported["works"]
        )
        ok, tip = store.verify_event_chain()
        assert ok is True
        assert len(tip) == 64


def test_fixture_is_explicitly_synthetic() -> None:
    payload = json.loads(ORCID_FIXTURE.read_text(encoding="utf-8"))
    assert payload["fixture"] is True
    assert "not a claim about a real person" in payload["fixture_notice"]
