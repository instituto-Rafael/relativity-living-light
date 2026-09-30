#!/usr/bin/env python3
"""Verify or materialize the pinned small DESI DR2 BAO Cobaya likelihood files.

This is the safe extraction of the useful data-materialization part of PR #385.
It never mutates workflows and never treats successful materialization as a
scientific RLL claim. Network downloads are opt-in and must match the pinned
upstream byte count and SHA-256 before an atomic write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "real" / "cosmology" / "desi_bao_dr2_cobaya"
MANIFEST = DATA_DIR / "MANIFEST.json"
BASE_RAW = "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != "rll.real_data.desi_dr2_cobaya_manifest.v2":
        raise ValueError("unexpected DESI DR2 Cobaya manifest schema")
    if doc.get("claim_boundary", {}).get("claim_allowed") is not False:
        raise ValueError("claim boundary must remain fail-closed")
    return doc


def verify_local_entry(entry: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / entry["local_file"]
    if not path.is_file():
        return {"file": entry["local_file"], "ok": False, "reason": "missing"}
    payload = path.read_bytes()
    digest = sha256_bytes(payload)
    ok = len(payload) == entry["local_bytes"] and digest == entry["local_sha256"]
    return {
        "file": entry["local_file"],
        "ok": ok,
        "bytes": len(payload),
        "sha256": digest,
        "reason": "ok" if ok else "local_custody_mismatch",
    }


def upstream_url(entry: dict[str, Any]) -> str:
    return BASE_RAW + urllib.parse.quote(entry["upstream_file"], safe="+._-/")


def fetch_pinned(entry: dict[str, Any], timeout: int) -> bytes:
    request = urllib.request.Request(
        upstream_url(entry), headers={"User-Agent": "RLL-DESI-DR2-custody/2.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
    if len(payload) != entry["upstream_bytes"]:
        raise ValueError(
            f"upstream byte mismatch for {entry['upstream_file']}: "
            f"{len(payload)} != {entry['upstream_bytes']}"
        )
    digest = sha256_bytes(payload)
    if digest != entry["upstream_sha256"]:
        raise ValueError(
            f"upstream SHA-256 mismatch for {entry['upstream_file']}: "
            f"{digest} != {entry['upstream_sha256']}"
        )
    return payload


def materialize_missing(entry: dict[str, Any], timeout: int, refresh: bool) -> dict[str, Any]:
    path = ROOT / entry["local_file"]
    current = verify_local_entry(entry)
    if current["ok"] and not refresh:
        return current

    # The ALL pair was normalized to canonical TSV earlier. Reconstructing that
    # transformation from a mutable remote is deliberately outside this tool.
    if entry.get("normalized_local_tsv"):
        return {
            "file": entry["local_file"],
            "ok": False,
            "reason": "TOKEN_VAZIO_NORMALIZED_CORE_REQUIRES_LOCAL_RECOVERY",
        }

    payload = fetch_pinned(entry, timeout)
    # Non-normalized subset files must preserve upstream bytes exactly.
    if sha256_bytes(payload) != entry["local_sha256"] or len(payload) != entry["local_bytes"]:
        raise ValueError(f"local/upstream custody contract diverged for {entry['upstream_file']}")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)
    return verify_local_entry(entry)


def run(download_missing: bool, refresh: bool, timeout: int) -> dict[str, Any]:
    manifest = load_manifest()
    rows: list[dict[str, Any]] = []
    for entry in manifest["files"]:
        if download_missing or refresh:
            rows.append(materialize_missing(entry, timeout, refresh))
        else:
            rows.append(verify_local_entry(entry))

    failures = [row for row in rows if not row["ok"]]
    return {
        "schema": "rll.real_data.desi_dr2_cobaya_materialization_receipt.v1",
        "state": "READY_COMMITTED_SMALL_LIKELIHOOD" if not failures else "TOKEN_VAZIO_OR_CUSTODY_FAILURE",
        "files_total": len(rows),
        "files_ok": len(rows) - len(failures),
        "files_failed": len(failures),
        "failures": failures,
        "claim_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true", help="verify committed bytes; no network")
    parser.add_argument("--download-missing", action="store_true", help="download only missing/corrupt non-normalized subset files")
    parser.add_argument("--refresh", action="store_true", help="re-download all non-normalized subset files after hash verification")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.verify_only and (args.download_missing or args.refresh):
        parser.error("--verify-only cannot be combined with network materialization flags")

    receipt = run(args.download_missing, args.refresh, args.timeout)
    text = json.dumps(receipt, indent=2, sort_keys=True)
    print(text if args.json else text)
    return 0 if receipt["files_failed"] == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
