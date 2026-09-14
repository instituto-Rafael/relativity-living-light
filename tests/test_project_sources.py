import hashlib
import json
from pathlib import Path

import pytest

from rll.project_sources import ProjectCorpus, load_manifest


def make_fixture(tmp_path: Path) -> Path:
    public = tmp_path / "a.txt"
    public.write_text("# Física\nquantum gravity tensor\n", encoding="utf-8")
    private = tmp_path / "private.txt"
    private.write_text("private", encoding="utf-8")
    manifest = {
        "schema": "rll.project_sources_manifest.v1",
        "claim_allowed": False,
        "raw_bodies_committed": False,
        "source_count": 2,
        "sources": [
            {
                "source_id": "A",
                "display_name": "A",
                "local_filename": "a.txt",
                "content_sha256": hashlib.sha256(public.read_bytes()).hexdigest(),
                "size_bytes": public.stat().st_size,
                "line_count": 2,
                "temporal_state": "current",
                "rll_relation": "RLL_DIRECT_AND_METHODOLOGY",
                "visibility": "PUBLIC_SAFE_METADATA_AND_LOCAL_BODY",
                "ingestion_policy": "ingest",
                "claim_allowed": False,
                "summary": "fixture",
            },
            {
                "source_id": "P",
                "display_name": "PRIVATE",
                "local_filename": None,
                "content_sha256": hashlib.sha256(private.read_bytes()).hexdigest(),
                "size_bytes": private.stat().st_size,
                "line_count": 1,
                "temporal_state": "private",
                "rll_relation": "OUT_OF_SCOPE_PERSONAL",
                "visibility": "PRIVATE_POINTER_ONLY",
                "ingestion_policy": "pointer_only",
                "claim_allowed": False,
                "summary": "private",
            },
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_manifest_and_ingest(tmp_path: Path) -> None:
    manifest = make_fixture(tmp_path)
    with ProjectCorpus(tmp_path / "db.sqlite") as corpus:
        receipt = corpus.ingest(load_manifest(manifest), tmp_path)
        assert receipt["verified"] == 1
        assert receipt["pointer_only"] == 1
        assert receipt["chunks"] == 1
        assert corpus.status()["documents"] == 2
        assert corpus.status()["claim_allowed"] is False
        assert corpus.con.execute(
            "SELECT COUNT(*) FROM project_chunks WHERE source_id='P'"
        ).fetchone()[0] == 0


def test_search(tmp_path: Path) -> None:
    manifest = make_fixture(tmp_path)
    with ProjectCorpus(tmp_path / "db.sqlite") as corpus:
        corpus.ingest(load_manifest(manifest), tmp_path)
        results = corpus.search("quantum tensor")
        assert results
        assert results[0]["source_id"] == "A"
        assert results[0]["claim_allowed"] is False


def test_hash_mismatch_is_not_ingested(tmp_path: Path) -> None:
    manifest = make_fixture(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["sources"][0]["content_sha256"] = "0" * 64
    manifest.write_text(json.dumps(payload))
    with ProjectCorpus(tmp_path / "db.sqlite") as corpus:
        receipt = corpus.ingest(load_manifest(manifest), tmp_path)
        assert receipt["mismatch"] == 1
        assert corpus.status()["chunks"] == 0


def test_manifest_rejects_claim_promotion(tmp_path: Path) -> None:
    manifest = make_fixture(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["claim_allowed"] = True
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_manifest(manifest)


def test_event_chain_is_linked(tmp_path: Path) -> None:
    manifest = make_fixture(tmp_path)
    with ProjectCorpus(tmp_path / "db.sqlite") as corpus:
        corpus.ingest(load_manifest(manifest), tmp_path)
        rows = corpus.con.execute(
            "SELECT previous_hash,event_hash FROM project_events ORDER BY sequence"
        ).fetchall()
        assert rows[0][0] == "0" * 64
        assert rows[1][0] == rows[0][1]
