import json
import shutil
from pathlib import Path

import pytest

from rll.project_source_seed import bootstrap, load_seed_manifest, verify_seed
from rll.project_sources import ProjectCorpus

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "configs/project_sources_seed.v1.json"


def test_real_seed_manifest_and_bundle_are_consistent() -> None:
    receipt = verify_seed(MANIFEST, REPO_ROOT)
    assert receipt["state"] == "PASS"
    assert receipt["sources"] == 14
    assert receipt["verified_committed_bodies"] == 13
    assert receipt["private_pointer_only"] == 1
    assert receipt["public_bytes"] == 123646
    assert receipt["public_lines"] == 4483
    assert receipt["claim_allowed"] is False


def test_real_seed_bootstraps_searchable_database(tmp_path: Path) -> None:
    db = tmp_path / "seed.sqlite3"
    receipt = bootstrap(MANIFEST, REPO_ROOT, db)
    assert receipt["ingest"] == {
        "verified": 13,
        "pointer_only": 1,
        "chunks": 202,
        "missing": 0,
        "mismatch": 0,
    }
    assert receipt["status"]["documents"] == 14
    assert receipt["status"]["verified"] == 13
    assert receipt["status"]["pointer_only"] == 1
    assert receipt["status"]["chunks"] == 202
    with ProjectCorpus(db) as corpus:
        results = corpus.search("ORCID vetores proveniência")
        assert results
        assert any(item["source_id"] == "SRC-ORCID-RLL-001" for item in results[:5])
        assert corpus.con.execute(
            "SELECT COUNT(*) FROM project_chunks WHERE source_id='SRC-PRIVATE-PERSONAL-001'"
        ).fetchone()[0] == 0


def copy_bundle(tmp_path: Path) -> tuple[dict, Path]:
    manifest = load_seed_manifest(MANIFEST)
    fake_root = tmp_path / "repo"
    bundle_root = fake_root / manifest["bundle_root"]
    bundle_root.mkdir(parents=True)
    source_root = REPO_ROOT / manifest["bundle_root"]
    for part in [*manifest["base64_prefix_parts"], *manifest["binary_tail_parts"]]:
        shutil.copyfile(source_root / part["name"], bundle_root / part["name"])
    return manifest, fake_root


def test_binary_tail_mutation_is_rejected(tmp_path: Path) -> None:
    manifest, fake_root = copy_bundle(tmp_path)
    tail = fake_root / manifest["bundle_root"] / manifest["binary_tail_parts"][0]["name"]
    tail.write_bytes(tail.read_bytes() + b"A")
    fake_manifest = tmp_path / "manifest.json"
    fake_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="binary tail divergente"):
        verify_seed(fake_manifest, fake_root)


def test_private_pointer_cannot_reference_public_body(tmp_path: Path) -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    private = next(item for item in payload["sources"] if item["ingestion_policy"] == "pointer_only")
    private["bundle_record_id"] = "SRC-WORKFLOW-001"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="fonte privada"):
        load_seed_manifest(path)
