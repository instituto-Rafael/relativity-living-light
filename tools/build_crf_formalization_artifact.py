#!/usr/bin/env python3
"""Build the RLL CRF formalization artifact using Python stdlib only.

The builder:
- fetches a pinned cross-repository registry;
- verifies its Git blob SHA-1;
- validates stable CRF ids/counts/readiness;
- emits deterministic JSON/Markdown/page payloads;
- emits SHA-256 checksums and a manifest.

It validates formalization metadata. It does not prove novelty or physical claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import Counter
from typing import Any

GENERATOR = "tools/build_crf_formalization_artifact.py"
OUTPUT_ORDER = [
    "SUMMARY.json",
    "FORMALIZATION_REGISTRY.json",
    "FORMALIZATION_INDEX.md",
    "PAGE_DATA.json",
]


def read_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_source(snapshot_path: str, source_file: str | None) -> bytes:
    path = pathlib.Path(source_file) if source_file else pathlib.Path(snapshot_path)
    if not path.is_file():
        raise SystemExit(f"source snapshot not found: {path}")
    return path.read_bytes()


def validate(contract: dict[str, Any], source: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    expected = contract["expected"]
    errors: list[str] = []

    if source.get("schema") != expected["schema"]:
        errors.append(f"schema={source.get('schema')!r} expected={expected['schema']!r}")
    if source.get("claim_allowed") is not expected["claim_allowed"]:
        errors.append("claim_allowed must remain false")

    items = source.get("items")
    if not isinstance(items, list):
        errors.append("items must be a list")
        items = []

    if len(items) != expected["item_count"]:
        errors.append(f"item_count={len(items)} expected={expected['item_count']}")

    id_cfg = expected["ids"]
    expected_ids = [
        f"{id_cfg['prefix']}{i:0{id_cfg['width']}d}"
        for i in range(id_cfg["first"], id_cfg["last"] + 1)
    ]
    ids = [item.get("id") for item in items]
    if ids != expected_ids:
        errors.append("CRF ids are missing, duplicated, reordered or non-contiguous")
    if len(set(ids)) != len(ids):
        errors.append("duplicate CRF ids")

    required = {
        "id", "title", "expression", "kind", "readiness",
        "source", "code", "test", "evidence", "prior_art", "gaps",
    }
    for idx, item in enumerate(items):
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"item[{idx}] missing={missing}")
        if item.get("readiness") not in {"A", "B", "C"}:
            errors.append(f"{item.get('id')}: invalid readiness={item.get('readiness')!r}")
        if not isinstance(item.get("gaps"), list):
            errors.append(f"{item.get('id')}: gaps must be list")

    counts = Counter(str(item.get("readiness")) for item in items)
    actual_counts = {key: counts.get(key, 0) for key in ("A", "B", "C")}
    if actual_counts != expected["readiness_counts"]:
        errors.append(
            f"readiness_counts={actual_counts} expected={expected['readiness_counts']}"
        )

    if errors:
        raise SystemExit("CRF contract validation failed:\n- " + "\n- ".join(errors))
    return items, actual_counts


def write_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        default="data/contracts/rll_crf_formalization_artifact.v1.json",
    )
    parser.add_argument(
        "--outdir",
        default="artifacts/crf-formalization-v1",
    )
    parser.add_argument(
        "--source-file",
        default=None,
        help="Optional local source registry for offline/replay verification.",
    )
    args = parser.parse_args()

    contract_path = pathlib.Path(args.contract)
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    contract = read_json(contract_path)

    source_bytes = load_source(contract["source"]["snapshot_path"], args.source_file)
    observed_blob = git_blob_sha1(source_bytes)
    expected_blob = contract["source"]["origin_git_blob_sha1"]
    if observed_blob != expected_blob:
        raise SystemExit(
            f"source blob mismatch: observed={observed_blob} expected={expected_blob}"
        )

    source = json.loads(source_bytes.decode("utf-8"))
    items, readiness_counts = validate(contract, source)

    normalized_items = []
    for item in items:
        normalized_items.append({
            "id": item["id"],
            "title": item["title"],
            "kind": item["kind"],
            "expression": item["expression"],
            "readiness": item["readiness"],
            "source": item["source"],
            "code": item["code"],
            "test": item["test"],
            "evidence": item["evidence"],
            "prior_art": item["prior_art"],
            "gaps": item["gaps"],
        })

    registry = {
        "schema": "rll.crf_formalization_registry.v1",
        "claim_allowed": False,
        "source": {
            "repository": contract["source"]["origin_repository"],
            "ref": contract["source"]["origin_ref"],
            "path": contract["source"]["origin_path"],
            "git_blob_sha1": observed_blob,
        },
        "items": normalized_items,
    }

    groups = {
        key: [item["id"] for item in normalized_items if item["readiness"] == key]
        for key in ("A", "B", "C")
    }

    summary = {
        "schema": "rll.crf_formalization_summary.v1",
        "status": "PASS",
        "claim_allowed": False,
        "artifact": contract["artifact_name"],
        "item_count": len(normalized_items),
        "readiness_counts": readiness_counts,
        "groups": groups,
        "source_blob_sha1": observed_blob,
        "generator": GENERATOR,
        "dependency_policy": "PYTHON_STDLIB_ONLY",
        "boundaries": contract["boundaries"],
    }

    page_data = {
        "schema": "rll.crf_page_data.v1",
        "artifact": contract["artifact_name"],
        "source": registry["source"],
        "counts": {
            "total": len(normalized_items),
            "A": readiness_counts["A"],
            "B": readiness_counts["B"],
            "C": readiness_counts["C"],
        },
        "groups": groups,
        "items": normalized_items,
        "claim_allowed": False,
        "page_rule": contract["page_contract"]["rule"],
    }

    table_lines = [
        "# RLL CRF Formalization Index V1",
        "",
        f"Source lock: `{contract['source']['origin_repository']}@{contract['source']['origin_ref']}`",
        "",
        f"Total: **{len(normalized_items)}** · A: **{readiness_counts['A']}** · B: **{readiness_counts['B']}** · C: **{readiness_counts['C']}**",
        "",
        "| ID | Kind | Ready | Formula / object | Gaps |",
        "|---|---|---:|---|---|",
    ]
    for item in normalized_items:
        expr = str(item["expression"]).replace("|", "\\|").replace("\n", " ")
        title = str(item["title"]).replace("|", "\\|")
        gaps = ", ".join(item["gaps"]) if item["gaps"] else "—"
        gaps = gaps.replace("|", "\\|")
        table_lines.append(
            f"| {item['id']} | {item['kind']} | {item['readiness']} | "
            f"`{expr}` — {title} | {gaps} |"
        )
    table_lines += [
        "",
        "## Boundary",
        "",
        "- Artifact PASS validates schema, source lock and routing metadata.",
        "- It does not prove novelty, physics or universal mathematical claims.",
        "- TOKEN_VAZIO remains explicit.",
        "",
    ]

    outputs = {
        "SUMMARY.json": canonical_bytes(summary),
        "FORMALIZATION_REGISTRY.json": canonical_bytes(registry),
        "PAGE_DATA.json": canonical_bytes(page_data),
        "FORMALIZATION_INDEX.md": ("\n".join(table_lines)).encode("utf-8"),
    }

    for name, payload in outputs.items():
        (outdir / name).write_bytes(payload)

    checksums = {
        name: {
            "sha256": sha256_file(outdir / name),
            "bytes": (outdir / name).stat().st_size,
        }
        for name in OUTPUT_ORDER
    }

    manifest = {
        "schema": "rll.crf_formalization_artifact_manifest.v1",
        "artifact_name": contract["artifact_name"],
        "status": "PASS",
        "claim_allowed": False,
        "generator": GENERATOR,
        "dependency_policy": "PYTHON_STDLIB_ONLY",
        "source_lock": registry["source"],
        "item_count": len(normalized_items),
        "readiness_counts": readiness_counts,
        "files": checksums,
        "page_entrypoint": "PAGE_DATA.json",
        "boundaries": contract["boundaries"],
    }
    (outdir / "MANIFEST.json").write_bytes(canonical_bytes(manifest))

    checksum_names = ["MANIFEST.json"] + OUTPUT_ORDER
    checksum_lines = [
        f"{sha256_file(outdir / name)}  {name}"
        for name in checksum_names
    ]
    write_text(outdir / "CHECKSUMS.sha256", "\n".join(checksum_lines) + "\n")

    expected_outputs = set(contract["outputs"])
    actual_outputs = {path.name for path in outdir.iterdir() if path.is_file()}
    if actual_outputs != expected_outputs:
        raise SystemExit(
            f"output set mismatch: actual={sorted(actual_outputs)} expected={sorted(expected_outputs)}"
        )

    print(json.dumps({
        "status": "PASS",
        "artifact": contract["artifact_name"],
        "items": len(normalized_items),
        "readiness": readiness_counts,
        "source_blob_sha1": observed_blob,
        "outdir": str(outdir),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
