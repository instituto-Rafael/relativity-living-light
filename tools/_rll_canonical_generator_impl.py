#!/usr/bin/env python3
"""Materialize the versioned RLL project-source corpus as freestanding C.

Python is build-time only. The generated C needs no JSON parser, filesystem,
SQLite, libc, heap, GC, or hidden runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FNV_OFFSET = 14695981039346656037
FNV_PRIME = 1099511628211
ABI = 0x00010000

RELATIONS = {
    "METHODOLOGY": 1,
    "MATHEMATICAL_CONTEXT": 2,
    "FEDERATED_GOVERNANCE": 3,
    "RLL_DIRECT_AND_METHODOLOGY": 4,
    "COMPUTATIONAL_CONTEXT": 5,
    "INDEQ_POINTER": 6,
    "OUT_OF_SCOPE_PERSONAL": 7,
    "SOURCE_INVENTORY": 8,
    "OPERATIONAL_EVIDENCE": 9,
    "RLL_DIRECT_AND_BIBLIOGRAPHIC": 10,
}
VISIBILITIES = {
    "PUBLIC_SAFE_METADATA_AND_LOCAL_BODY": 1,
    "PUBLIC_SAFE_METADATA_ONLY": 2,
    "PRIVATE_POINTER_ONLY": 3,
}
POLICIES = {"ingest": 1, "metadata_only": 2, "pointer_only": 3}

FLAG_VERIFIED = 1 << 0
FLAG_METADATA_ONLY = 1 << 1
FLAG_PRIVATE_POINTER = 1 << 2
FLAG_NOT_COSMOLOGY = 1 << 3
FLAG_NOT_PHYSICAL = 1 << 4
FLAG_NOT_BIOLOGY = 1 << 5

CUSTODY_COMPILED_MANIFEST_HASHED = 1 << 0
CUSTODY_RECEIPT_DIGEST_MATCH = 1 << 1
CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED = 1 << 2


def u32(value: int) -> bytes:
    return int(value).to_bytes(4, "little", signed=False)


def u64(value: int) -> bytes:
    return int(value).to_bytes(8, "little", signed=False)


def fnv_update(state: int, data: bytes) -> int:
    for octet in data:
        state ^= octet
        state = (state * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    return state


def fold_span(state: int, text: str | None) -> int:
    data = b"" if text is None else text.encode("utf-8")
    return fnv_update(fnv_update(state, u32(len(data))), data)


def source_flags(item: dict[str, Any]) -> int:
    flags = {
        "ingest": FLAG_VERIFIED,
        "metadata_only": FLAG_METADATA_ONLY,
        "pointer_only": FLAG_PRIVATE_POINTER,
    }[item["ingestion_policy"]]
    blocked = set(item.get("not_evidence_for", []))
    if "COSMOLOGICAL_CLAIM" in blocked:
        flags |= FLAG_NOT_COSMOLOGY
    if "PHYSICAL_LAW" in blocked:
        flags |= FLAG_NOT_PHYSICAL
    if "BIOLOGICAL_OR_PHYSIOLOGICAL_CLAIM" in blocked:
        flags |= FLAG_NOT_BIOLOGY
    return flags


def source_id_hash(item: dict[str, Any]) -> int:
    return fnv_update(FNV_OFFSET, item["source_id"].encode("utf-8"))


def custody_flags(receipt_digest: bytes, compiled_digest: bytes) -> int:
    flags = CUSTODY_COMPILED_MANIFEST_HASHED
    if receipt_digest == compiled_digest:
        flags |= CUSTODY_RECEIPT_DIGEST_MATCH
    else:
        flags |= CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED
    return flags


def fingerprint(
    manifest: dict[str, Any],
    receipt: dict[str, Any],
    compiled_manifest_digest: bytes,
) -> int:
    receipt_digest = bytes.fromhex(receipt["manifest_sha256"])
    state = fnv_update(FNV_OFFSET, b"RLL_CANONICAL_REGION_V1")
    for value in (
        ABI,
        receipt["source_count"],
        receipt["verified_local_hash_count"],
        receipt["metadata_only_count"],
        receipt["private_pointer_only_count"],
        receipt["chunk_count"],
        receipt["missing_count"],
        receipt["hash_mismatch_count"],
        receipt["vector_dimensions"],
    ):
        state = fnv_update(state, u32(value))
    state = fold_span(state, receipt["vector_model"])
    for value in (
        int(receipt["raw_bodies_committed"]),
        int(receipt["database_committed"]),
        int(receipt["claim_allowed"]),
        custody_flags(receipt_digest, compiled_manifest_digest),
    ):
        state = fnv_update(state, u32(value))
    state = fnv_update(state, receipt_digest)
    state = fnv_update(state, compiled_manifest_digest)

    for item in manifest["sources"]:
        state = fold_span(state, item["source_id"])
        state = fold_span(state, item["display_name"])
        state = fold_span(state, item.get("local_filename"))
        state = fnv_update(state, bytes.fromhex(item["content_sha256"]))
        state = fnv_update(state, u64(item["size_bytes"]))
        state = fnv_update(state, u32(item["line_count"]))
        state = fold_span(state, item["temporal_state"])
        state = fnv_update(state, u32(RELATIONS[item["rll_relation"]]))
        state = fnv_update(state, u32(VISIBILITIES[item["visibility"]]))
        state = fnv_update(state, u32(POLICIES[item["ingestion_policy"]]))
        state = fold_span(state, item["summary"])
        state = fold_span(state, item["next_gate"])
        state = fnv_update(state, u32(source_flags(item)))
        state = fnv_update(state, u64(source_id_hash(item)))
    return state


def c_bytes(data: bytes) -> str:
    return ",".join(f"0x{octet:02x}" for octet in data)


def c_string_bytes(data: bytes, width: int = 88) -> str:
    """Emit byte-exact C literals using fixed-width octal escapes."""
    tokens: list[str] = []
    for octet in data:
        if octet == 0x22:
            tokens.append(r'\"')
        elif octet == 0x5C:
            tokens.append(r'\\')
        elif 0x20 <= octet <= 0x7E:
            tokens.append(chr(octet))
        else:
            tokens.append(f"\\{octet:03o}")
    lines: list[str] = []
    current = ""
    for token in tokens:
        if current and len(current) + len(token) > width:
            lines.append(current)
            current = token
        else:
            current += token
    if current:
        lines.append(current)
    return "\n".join(f'    "{line}"' for line in lines)


def validate(manifest: dict[str, Any], receipt: dict[str, Any]) -> None:
    if manifest.get("schema") != "rll.project_sources_manifest.v1":
        raise ValueError("invalid manifest schema")
    if receipt.get("schema") != "rll.project_sources_local_receipt.v1":
        raise ValueError("invalid receipt schema")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or len(sources) != manifest.get("source_count"):
        raise ValueError("manifest source_count mismatch")
    if manifest["source_count"] != receipt["source_count"]:
        raise ValueError("manifest/receipt source_count mismatch")
    if manifest.get("claim_allowed") is not False or manifest.get("raw_bodies_committed") is not False:
        raise ValueError("manifest boundary violation")
    if receipt.get("claim_allowed") is not False:
        raise ValueError("receipt claim boundary violation")
    if receipt.get("raw_bodies_committed") is not False or receipt.get("database_committed") is not False:
        raise ValueError("receipt persistence boundary violation")

    receipt_digest = bytes.fromhex(receipt["manifest_sha256"])
    if len(receipt_digest) != 32:
        raise ValueError("invalid receipt manifest SHA-256")

    ids = [item["source_id"] for item in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source_id")
    counts = {
        "ingest": sum(item["ingestion_policy"] == "ingest" for item in sources),
        "metadata_only": sum(item["ingestion_policy"] == "metadata_only" for item in sources),
        "pointer_only": sum(item["ingestion_policy"] == "pointer_only" for item in sources),
    }
    if counts["ingest"] != receipt["verified_local_hash_count"]:
        raise ValueError("verified count mismatch")
    if counts["metadata_only"] != receipt["metadata_only_count"]:
        raise ValueError("metadata-only count mismatch")
    if counts["pointer_only"] != receipt["private_pointer_only_count"]:
        raise ValueError("pointer-only count mismatch")
    if receipt["missing_count"] != 0 or receipt["hash_mismatch_count"] != 0:
        raise ValueError("receipt contains unresolved source failures")

    for item in sources:
        digest = bytes.fromhex(item["content_sha256"])
        if len(digest) != 32:
            raise ValueError(f"invalid SHA-256 for {item['source_id']}")
        if item.get("claim_allowed") is not False:
            raise ValueError(f"claim boundary violation for {item['source_id']}")
        if item["rll_relation"] not in RELATIONS:
            raise ValueError(f"unknown relation for {item['source_id']}")
        if item["visibility"] not in VISIBILITIES:
            raise ValueError(f"unknown visibility for {item['source_id']}")
        if item["ingestion_policy"] not in POLICIES:
            raise ValueError(f"unknown policy for {item['source_id']}")
        if item["ingestion_policy"] == "pointer_only" and item.get("local_filename") is not None:
            raise ValueError(f"private pointer exposes a filename for {item['source_id']}")
        if item["ingestion_policy"] == "ingest" and item["visibility"] != "PUBLIC_SAFE_METADATA_AND_LOCAL_BODY":
            raise ValueError(f"ingest visibility mismatch for {item['source_id']}")
        if item["ingestion_policy"] == "metadata_only" and item["visibility"] != "PUBLIC_SAFE_METADATA_ONLY":
            raise ValueError(f"metadata visibility mismatch for {item['source_id']}")
        if item["ingestion_policy"] == "pointer_only" and item["visibility"] != "PRIVATE_POINTER_ONLY":
            raise ValueError(f"pointer visibility mismatch for {item['source_id']}")


def generate(
    manifest: dict[str, Any],
    receipt: dict[str, Any],
    compiled_manifest_digest: bytes,
) -> str:
    records: list[str] = []
    pool = bytearray()
    spans: dict[str, tuple[int, int]] = {}

    def intern(text: str | None) -> tuple[int, int] | None:
        if text is None:
            return None
        if text not in spans:
            raw = text.encode("utf-8")
            spans[text] = (len(pool), len(raw))
            pool.extend(raw)
        return spans[text]

    vector_span = intern(receipt["vector_model"])
    assert vector_span is not None
    source_spans: list[dict[str, tuple[int, int] | None]] = []
    for item in manifest["sources"]:
        source_spans.append(
            {
                "source_id": intern(item["source_id"]),
                "display_name": intern(item["display_name"]),
                "local_filename": intern(item.get("local_filename")),
                "temporal_state": intern(item["temporal_state"]),
                "summary": intern(item["summary"]),
                "next_gate": intern(item["next_gate"]),
            }
        )

    def c_span(value: tuple[int, int] | None) -> str:
        if value is None:
            return "{(const rll_u8 *)0,0u}"
        offset, length = value
        return f"{{rll_canonical_string_pool+{offset}u,{length}u}}"

    for item, fields in zip(manifest["sources"], source_spans):
        records.append(
            "    {\n"
            f"        {c_span(fields['source_id'])},\n"
            f"        {c_span(fields['display_name'])},\n"
            f"        {c_span(fields['local_filename'])},\n"
            f"        {{{c_bytes(bytes.fromhex(item['content_sha256']))}}},\n"
            f"        {item['size_bytes']}ull,\n"
            f"        {item['line_count']}u,\n"
            f"        {c_span(fields['temporal_state'])},\n"
            f"        {RELATIONS[item['rll_relation']]}u,\n"
            f"        {VISIBILITIES[item['visibility']]}u,\n"
            f"        {POLICIES[item['ingestion_policy']]}u,\n"
            f"        {c_span(fields['summary'])},\n"
            f"        {c_span(fields['next_gate'])},\n"
            f"        0x{source_flags(item):08x}u,\n"
            f"        0x{source_id_hash(item):016x}ull\n"
            "    }"
        )

    receipt_digest = bytes.fromhex(receipt["manifest_sha256"])
    flags = custody_flags(receipt_digest, compiled_manifest_digest)
    fp = fingerprint(manifest, receipt, compiled_manifest_digest)
    return (
        "/* AUTO-GENERATED by tools/generate_rll_canonical_region.py. DO NOT EDIT. */\n"
        f"#define RLL_CANONICAL_GENERATED_SOURCE_COUNT {manifest['source_count']}u\n\n"
        + "static const rll_u8 rll_canonical_string_pool[] =\n"
        + c_string_bytes(bytes(pool))
        + ";\n\n"
        + "static const rll_canonical_source rll_canonical_sources[RLL_CANONICAL_GENERATED_SOURCE_COUNT] = {\n"
        + ",\n".join(records)
        + "\n};\n\n"
        + "static const rll_canonical_receipt rll_canonical_receipt_v1 = {\n"
        + f"    0x{ABI:08x}u,\n"
        + f"    {receipt['source_count']}u,\n"
        + f"    {receipt['verified_local_hash_count']}u,\n"
        + f"    {receipt['metadata_only_count']}u,\n"
        + f"    {receipt['private_pointer_only_count']}u,\n"
        + f"    {receipt['chunk_count']}u,\n"
        + f"    {receipt['missing_count']}u,\n"
        + f"    {receipt['hash_mismatch_count']}u,\n"
        + f"    {receipt['vector_dimensions']}u,\n"
        + f"    {c_span(vector_span)},\n"
        + f"    {int(receipt['raw_bodies_committed'])}u,\n"
        + f"    {int(receipt['database_committed'])}u,\n"
        + f"    {int(receipt['claim_allowed'])}u,\n"
        + f"    0x{flags:08x}u,\n"
        + f"    {{{c_bytes(receipt_digest)}}},\n"
        + f"    {{{c_bytes(compiled_manifest_digest)}}},\n"
        + f"    0x{fp:016x}ull\n"
        + "};\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("configs/project_sources_manifest.v1.json"))
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("data/receipts/project_sources_local_receipt_20260726.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("core/lowlevel_runtime/generated/rll_canonical_project_sources.inc"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    validate(manifest, receipt)
    output = generate(manifest, receipt, hashlib.sha256(manifest_bytes).digest())

    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != output:
            raise SystemExit("generated canonical region is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
