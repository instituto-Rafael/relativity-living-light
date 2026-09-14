#!/usr/bin/env python3
from __future__ import annotations

"""Custody receipt for Cobaya's official DESI DR2 all-tracer BAO likelihood data.

This proves that the released likelihood/data dependency is materially present
and hashed. It does not reproduce a published posterior, joint cross-block
cosmology fit, or authorize an RLL evidence claim.
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "rll.desi_dr2_cobaya_custody.v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(packages_root: Path) -> dict[str, Any]:
    if not packages_root.is_dir():
        raise ValueError("Cobaya packages root missing")
    files = sorted(path for path in packages_root.rglob("*") if path.is_file())
    desi_files = [path for path in files if "desi" in str(path.relative_to(packages_root)).lower()]
    if not desi_files:
        raise ValueError("no DESI files found under Cobaya packages root")
    manifest = [
        {
            "path": str(path.relative_to(packages_root)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in desi_files
    ]
    return {
        "schema": SCHEMA,
        "state": "DESI_DR2_COBAYA_ALL_TRACER_DATA_CUSTODY_MATERIALIZED",
        "claim_allowed": False,
        "publication_ready": False,
        "token": "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
        "component": {
            "cobaya_likelihood": "bao.desi_dr2.desi_bao_all",
            "alias": "bao.desi_dr2",
            "cobaya_version": importlib.metadata.version("cobaya"),
            "scope": "DESI DR2 BAO all tracers; BAO-only",
        },
        "custody": {
            "packages_root": str(packages_root),
            "desi_file_count": len(desi_files),
            "total_desi_bytes": sum(path.stat().st_size for path in desi_files),
            "files": manifest,
        },
        "resolved_token": None,
        "reduces_token": "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
        "remaining_close_conditions": [
            "evaluate the installed all-tracer likelihood at frozen reference cosmologies",
            "materialize the exact measurement/covariance convention mapping used by the likelihood",
            "reproduce the intended official joint/cross-block analysis rather than treating package installation as a posterior result",
            "audit overlap/covariance before combining DESI with other probes in a Bayes factor",
        ],
        "scientific_boundary": (
            "Public Cobaya likelihood/data custody closes the availability ambiguity only. "
            "It is not a joint posterior reproduction and cannot authorize model-evidence claims."
        ),
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packages-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = build(args.packages_root)
    atomic_json(args.output, payload)
    print(json.dumps({
        "state": payload["state"],
        "desi_file_count": payload["custody"]["desi_file_count"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
