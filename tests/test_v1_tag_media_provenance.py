import csv
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tools.audit_v1_tag_media_provenance import TagAuditError, build_audit


def _git(root: Path, *args: str) -> None:
    subprocess.check_call(["git", "-C", str(root), *args])


def _seed_repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "RLL Test")
    (repo / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (repo / "plot.png").write_bytes(b"PNG-test")
    (repo / "README.md").write_text("not selected", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed immutable tag")
    _git(repo, "tag", "v1.0.0")
    return repo


def test_build_audit_hashes_only_images_and_csv(tmp_path: Path) -> None:
    repo = _seed_repository(tmp_path)
    output = tmp_path / "artifact"

    receipt = build_audit(
        repo,
        "v1.0.0",
        output,
        source_repository="example/RLL",
        source_tag="v1.0.0",
    )

    assert receipt["claim_allowed"] is False
    assert receipt["doi_snapshot_state"] == "TOKEN_VAZIO"
    assert receipt["source_repository"] == "example/RLL"
    assert receipt["source_tag"] == "v1.0.0"
    assert receipt["resolved_ref"] == "v1.0.0"
    assert receipt["counts"] == {"images": 1, "csv": 1, "selected_total": 2}

    with (output / "V1_IMAGE_CSV_INVENTORY.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert {row["path"] for row in rows} == {"plot.png", "table.csv"}
    png_row = next(row for row in rows if row["path"] == "plot.png")
    assert png_row["sha256"] == hashlib.sha256(b"PNG-test").hexdigest()
    assert "README.md" not in {row["path"] for row in rows}

    manifest = json.loads((output / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["claim_allowed"] is False
    assert manifest["source_repository"] == "example/RLL"
    subprocess.check_call(["sha256sum", "-c", "CHECKSUMS.sha256"], cwd=output)


def test_missing_tag_fails_closed(tmp_path: Path) -> None:
    repo = _seed_repository(tmp_path)
    with pytest.raises(TagAuditError):
        build_audit(repo, "v9.9.9", tmp_path / "missing")
