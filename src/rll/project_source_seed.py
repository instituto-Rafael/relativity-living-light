from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from rll.project_sources import ProjectCorpus

SCHEMA = "rll.project_sources_seed.v1"
DEFAULT_MANIFEST = Path("configs/project_sources_seed.v1.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def line_count(text: str) -> int:
    return len(text.splitlines())


def safe_filename(source_id: str) -> str:
    return source_id.lower().replace("_", "-") + ".txt"


def load_seed_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("schema de seed inválido")
    required_false = ("claim_allowed", "private_bodies_committed")
    if any(data.get(key) is not False for key in required_false):
        raise ValueError("seed viola fronteira de claim/privacidade")
    if data.get("execution_ready") is not True:
        raise ValueError("seed ainda não está marcado como execution_ready")
    if data.get("public_body_scope") != "PUBLIC_SAFE_ONLY":
        raise ValueError("escopo público inválido")
    prefix_parts = data.get("base64_prefix_parts")
    tail_parts = data.get("binary_tail_parts")
    if not isinstance(prefix_parts, list) or not prefix_parts:
        raise ValueError("base64_prefix_parts ausente")
    if not isinstance(tail_parts, list) or not tail_parts:
        raise ValueError("binary_tail_parts ausente")
    names = [part.get("name") for part in [*prefix_parts, *tail_parts]]
    if len(names) != len(set(names)):
        raise ValueError("bundle part duplicado")
    sources = data.get("sources")
    if not isinstance(sources, list) or data.get("source_count") != len(sources):
        raise ValueError("source_count inconsistente")
    ids = [item.get("source_id") for item in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("source_id duplicado")
    if any(item.get("claim_allowed") is not False for item in sources):
        raise ValueError("fonte tentou promover claim")
    committed = sum(item.get("ingestion_policy") == "ingest" for item in sources)
    pointers = sum(item.get("ingestion_policy") == "pointer_only" for item in sources)
    if committed != data.get("committed_body_count"):
        raise ValueError("committed_body_count inconsistente")
    if pointers != data.get("pointer_only_count"):
        raise ValueError("pointer_only_count inconsistente")
    for item in sources:
        policy = item.get("ingestion_policy")
        if policy == "ingest":
            if item.get("visibility") != "PUBLIC_SAFE_COMMITTED_BODY":
                raise ValueError(f"visibilidade pública inválida: {item.get('source_id')}")
            if not item.get("bundle_record_id"):
                raise ValueError(f"bundle_record_id ausente: {item.get('source_id')}")
        elif policy == "pointer_only":
            if item.get("visibility") != "PRIVATE_POINTER_ONLY":
                raise ValueError(f"ponteiro privado inválido: {item.get('source_id')}")
            if item.get("bundle_record_id") is not None:
                raise ValueError(f"fonte privada não pode apontar para corpo público: {item.get('source_id')}")
        else:
            raise ValueError(f"ingestion_policy não suportada: {policy}")
    return data


def load_bundle(root: Path, manifest: Mapping[str, Any]) -> tuple[dict[str, dict[str, Any]], str]:
    prefix_chunks: list[bytes] = []
    for part in manifest["base64_prefix_parts"]:
        part_path = root / part["name"]
        raw_part = part_path.read_bytes()
        if len(raw_part) != part["size_bytes"] or sha256_bytes(raw_part) != part["sha256"]:
            raise ValueError(f"base64 prefix part divergente: {part['name']}")
        prefix_chunks.append(raw_part)
    prefix_transport = b"".join(prefix_chunks)
    try:
        compressed_prefix = base64.b64decode(prefix_transport, validate=True)
    except ValueError as error:
        raise ValueError("prefixo base64 inválido") from error
    if len(compressed_prefix) != manifest["base64_prefix_decoded_bytes"]:
        raise ValueError("base64_prefix_decoded_bytes divergente")

    tail_chunks: list[bytes] = []
    for part in manifest["binary_tail_parts"]:
        part_path = root / part["name"]
        raw_part = part_path.read_bytes()
        if len(raw_part) != part["size_bytes"] or sha256_bytes(raw_part) != part["sha256"]:
            raise ValueError(f"binary tail divergente: {part['name']}")
        tail_chunks.append(raw_part)

    compressed = compressed_prefix + b"".join(tail_chunks)
    if len(compressed) != manifest["bundle_gzip_size_bytes"]:
        raise ValueError("bundle_gzip_size_bytes divergente")
    if sha256_bytes(compressed) != manifest["bundle_gzip_sha256"]:
        raise ValueError("bundle_gzip_sha256 divergente")
    if sha256_bytes(base64.b64encode(compressed)) != manifest["bundle_transport_sha256"]:
        raise ValueError("bundle_transport_sha256 divergente")
    try:
        raw = gzip.decompress(compressed)
    except OSError as error:
        raise ValueError("bundle gzip inválido") from error
    records: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"source_id inválido na linha {number}")
        if source_id in records:
            raise ValueError(f"registro duplicado no bundle: {source_id}")
        if not isinstance(record.get("body"), str):
            raise ValueError(f"body inválido no bundle: {source_id}")
        records[source_id] = record
    return records, sha256_bytes(raw)


def verify_seed(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    manifest = load_seed_manifest(manifest_path)
    bundle_root = repo_root / manifest["bundle_root"]
    records, bundle_sha = load_bundle(bundle_root, manifest)
    if bundle_sha != manifest["bundle_sha256"]:
        raise ValueError("bundle_sha256 divergente")
    if len(records) != manifest["bundle_record_count"]:
        raise ValueError("bundle_record_count inconsistente")

    verified = 0
    public_bytes = 0
    public_lines = 0
    detail: list[dict[str, Any]] = []
    for item in manifest["sources"]:
        source_id = item["source_id"]
        if item["ingestion_policy"] == "pointer_only":
            detail.append({"source_id": source_id, "state": "PRIVATE_POINTER_ONLY"})
            continue
        record = records.get(item["bundle_record_id"])
        if record is None:
            raise ValueError(f"registro ausente no bundle: {source_id}")
        body = record["body"]
        raw = body.encode("utf-8")
        checks = {
            "filename": record.get("filename") == item["display_name"],
            "sha256": sha256_bytes(raw) == item["content_sha256"],
            "size_bytes": len(raw) == item["size_bytes"],
            "line_count": line_count(body) == item["line_count"],
        }
        if not all(checks.values()):
            raise ValueError(f"verificação falhou para {source_id}: {checks}")
        verified += 1
        public_bytes += len(raw)
        public_lines += line_count(body)
        detail.append({"source_id": source_id, "state": "VERIFIED_COMMITTED_SEED", **checks})

    if verified != manifest["committed_body_count"]:
        raise ValueError("quantidade verificada divergente")
    if public_bytes != manifest["total_public_bytes"]:
        raise ValueError("total_public_bytes divergente")
    if public_lines != manifest["total_public_lines"]:
        raise ValueError("total_public_lines divergente")

    return {
        "schema": SCHEMA,
        "state": "PASS",
        "bundle_sha256": bundle_sha,
        "sources": manifest["source_count"],
        "verified_committed_bodies": verified,
        "private_pointer_only": manifest["pointer_only_count"],
        "public_bytes": public_bytes,
        "public_lines": public_lines,
        "claim_allowed": False,
        "detail": detail,
    }


def compatibility_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    sources = []
    for item in manifest["sources"]:
        copy = dict(item)
        copy["local_filename"] = safe_filename(copy["source_id"]) if copy["ingestion_policy"] == "ingest" else None
        sources.append(copy)
    return {
        "schema": "rll.project_sources_manifest.v1",
        "claim_allowed": False,
        "raw_bodies_committed": False,
        "source_count": len(sources),
        "sources": sources,
    }


def bootstrap(manifest_path: Path, repo_root: Path, db: Path) -> dict[str, Any]:
    verification = verify_seed(manifest_path, repo_root)
    manifest = load_seed_manifest(manifest_path)
    records, _ = load_bundle(repo_root / manifest["bundle_root"], manifest)
    with tempfile.TemporaryDirectory(prefix="rll-project-seed-") as temporary:
        root = Path(temporary)
        for item in manifest["sources"]:
            if item["ingestion_policy"] != "ingest":
                continue
            body = records[item["bundle_record_id"]]["body"]
            (root / safe_filename(item["source_id"])).write_text(body, encoding="utf-8")
        with ProjectCorpus(db) as corpus:
            ingest_receipt = corpus.ingest(compatibility_manifest(manifest), root)
            status = corpus.status()
    return {"verification": verification, "ingest": ingest_receipt, "status": status}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="rll-project-source-seed")
    root.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    root.add_argument("--repo-root", type=Path, default=Path("."))
    commands = root.add_subparsers(dest="cmd", required=True)
    commands.add_parser("verify")
    boot = commands.add_parser("bootstrap")
    boot.add_argument("--db", type=Path, default=Path("artifacts/orcid_rll/project_sources_seed.sqlite3"))
    status = commands.add_parser("status")
    status.add_argument("--db", type=Path, default=Path("artifacts/orcid_rll/project_sources_seed.sqlite3"))
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--relation")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--db", type=Path, default=Path("artifacts/orcid_rll/project_sources_seed.sqlite3"))
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.cmd == "verify":
            output: Any = verify_seed(args.manifest, args.repo_root)
        elif args.cmd == "bootstrap":
            output = bootstrap(args.manifest, args.repo_root, args.db)
        else:
            with ProjectCorpus(args.db) as corpus:
                output = corpus.status() if args.cmd == "status" else corpus.search(args.query, args.limit, args.relation)
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, sqlite3.Error, json.JSONDecodeError) as error:
        print(f"rll-project-source-seed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
