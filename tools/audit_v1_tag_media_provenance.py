#!/usr/bin/env python3
"""Build an immutable image/CSV provenance inventory from a Git tag.

The audit reads Git objects directly. It does not validate scientific claims and
it does not infer DOI custody. Missing DOI comparison remains TOKEN_VAZIO.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".bmp",
    ".tif",
    ".tiff",
}
TABLE_EXTENSIONS = {".csv"}
CLAIM_BOUNDARY = (
    "Git tag inventory and blob hashes establish repository provenance only; "
    "they do not establish DOI equivalence, scientific validity, or physical truth."
)


class TagAuditError(RuntimeError):
    """Raised when the immutable tag audit cannot be completed."""


def _git(root: Path, *args: str, text: bool = True) -> str | bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args],
            text=text,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            detail = (
                exc.stderr
                if isinstance(exc.stderr, str)
                else exc.stderr.decode("utf-8", "replace")
            )
        raise TagAuditError(f"git {' '.join(args)} failed: {detail.strip()}") from exc


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _category(path: str) -> str | None:
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in TABLE_EXTENSIONS:
        return "csv"
    return None


def iter_tag_tree(root: Path, ref: str) -> Iterable[dict[str, object]]:
    raw = _git(root, "ls-tree", "-r", "-z", "--full-tree", ref, text=False)
    assert isinstance(raw, bytes)
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            meta, path_raw = record.split(b"\t", 1)
            mode_raw, type_raw, object_raw = meta.split(b" ", 2)
        except ValueError as exc:
            raise TagAuditError("unexpected git ls-tree record shape") from exc
        path = path_raw.decode("utf-8", "surrogateescape")
        category = _category(path)
        if category is None:
            continue
        object_id = object_raw.decode("ascii")
        blob = _git(root, "cat-file", "blob", object_id, text=False)
        assert isinstance(blob, bytes)
        yield {
            "category": category,
            "path": path,
            "git_mode": mode_raw.decode("ascii"),
            "git_type": type_raw.decode("ascii"),
            "git_object_id": object_id,
            "size_bytes": len(blob),
            "sha256": _sha256_bytes(blob),
        }


def build_audit(
    root: Path,
    ref: str,
    output: Path,
    *,
    source_repository: str = "local_repository",
    source_tag: str | None = None,
) -> dict[str, object]:
    root = root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    declared_tag = source_tag or ref

    commit_sha = str(_git(root, "rev-parse", f"{ref}^{{commit}}")).strip()
    tree_sha = str(_git(root, "rev-parse", f"{ref}^{{tree}}")).strip()
    commit_time = str(
        _git(root, "show", "-s", "--format=%cI", commit_sha)
    ).strip()
    records = sorted(iter_tag_tree(root, ref), key=lambda item: str(item["path"]))

    inventory_path = output / "V1_IMAGE_CSV_INVENTORY.csv"
    columns = [
        "category",
        "path",
        "git_mode",
        "git_type",
        "git_object_id",
        "size_bytes",
        "sha256",
    ]
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)

    counts = {
        "images": sum(1 for item in records if item["category"] == "image"),
        "csv": sum(1 for item in records if item["category"] == "csv"),
        "selected_total": len(records),
    }
    receipt = {
        "schema": "rll.v1_tag_media_provenance.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_repository": source_repository,
        "source_tag": declared_tag,
        "resolved_ref": ref,
        "tag_commit_sha": commit_sha,
        "tag_tree_sha": tree_sha,
        "tag_commit_time": commit_time,
        "counts": counts,
        "inventory": inventory_path.name,
        "doi_snapshot_state": "TOKEN_VAZIO",
        "claim_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(output / "TAG_RECEIPT.json", receipt)

    report = [
        "# RLL v1.0.0 — Image and CSV Provenance",
        "",
        f"- Source repository: `{source_repository}`",
        f"- Source tag: `{declared_tag}`",
        f"- Resolved local ref: `{ref}`",
        f"- Commit: `{commit_sha}`",
        f"- Tree: `{tree_sha}`",
        f"- Commit time: `{commit_time}`",
        f"- Images inventoried: `{counts['images']}`",
        f"- CSV files inventoried: `{counts['csv']}`",
        "- DOI snapshot comparison: `TOKEN_VAZIO`",
        "- `claim_allowed=false`",
        "",
        "## Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## F_ok",
        "",
        "- canonical source repository and source tag declared",
        "- immutable tag commit and tree resolved",
        "- selected Git blobs hashed with SHA-256",
        "- image/CSV paths preserved without checkout-time modification",
        "",
        "## F_gap",
        "",
        "- DOI/Zenodo snapshot has not been materialized and compared",
        "- identical filenames do not establish identical custody without hash comparison",
        "",
        "## F_next",
        "",
        "- obtain the DOI/Zenodo package through an official snapshot",
        "- hash its files and compare by path, content hash and role",
        "- preserve unmatched files as TOKEN_VAZIO or CONTRADICTION",
        "",
    ]
    (output / "RLL_V1_IMAGE_CSV_PROVENANCE.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    manifest = {
        "schema": "rll.v1_tag_media_provenance_manifest.v1",
        "source_repository": source_repository,
        "source_tag": declared_tag,
        "resolved_ref": ref,
        "claim_allowed": False,
        "files": [],
    }
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name not in {"MANIFEST.json", "CHECKSUMS.sha256"}:
            manifest["files"].append(
                {
                    "path": path.name,
                    "sha256": _sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    _write_json(output / "MANIFEST.json", manifest)

    checksum_lines = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "CHECKSUMS.sha256":
            checksum_lines.append(f"{_sha256_file(path)}  {path.name}")
    (output / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--ref", "--tag", dest="ref", default="v1.0.0")
    parser.add_argument("--source-repository", default="local_repository")
    parser.add_argument("--source-tag")
    parser.add_argument("--output", default="artifacts/rll-v1-tag-provenance")
    args = parser.parse_args()
    try:
        receipt = build_audit(
            Path(args.root),
            args.ref,
            Path(args.output),
            source_repository=args.source_repository,
            source_tag=args.source_tag,
        )
    except TagAuditError as exc:
        print(f"TAG_AUDIT_ERROR: {exc}")
        return 2
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
