#!/usr/bin/env python3
from __future__ import annotations

"""Build an immutable custody receipt for the official ACT DR6.02 actlite LCDM chain.

The official chain is reference evidence. Materializing it does not reproduce a
posterior locally and therefore cannot close the posterior-chain token by itself.
"""

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "rll.act_dr6_reference_chain_custody.v1"
CHAIN_RE = re.compile(r"\.\d+\.txt$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def chain_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                count += 1
    return count


def compact_config(path: Path) -> dict[str, Any]:
    import yaml

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: mapping required")
    params = raw.get("params") or {}
    sampler = raw.get("sampler") or {}
    theory = raw.get("theory") or {}
    likelihood = raw.get("likelihood") or {}
    return {
        "parameter_names": sorted(map(str, params.keys())) if isinstance(params, dict) else [],
        "sampler_names": sorted(map(str, sampler.keys())) if isinstance(sampler, dict) else [],
        "theory_names": sorted(map(str, theory.keys())) if isinstance(theory, dict) else [],
        "likelihood_names": sorted(map(str, likelihood.keys())) if isinstance(likelihood, dict) else [],
        "output": str(raw.get("output", "")),
    }


def build(archive: Path, extracted: Path, source_url: str) -> dict[str, Any]:
    if not archive.is_file():
        raise ValueError("reference archive missing")
    if not extracted.is_dir():
        raise ValueError("reference extraction directory missing")

    files = sorted(path for path in extracted.rglob("*") if path.is_file())
    chain_files = [path for path in files if CHAIN_RE.search(path.name)]
    updated_files = [path for path in files if path.name.endswith(".updated.yaml")]
    progress_files = [path for path in files if path.name.endswith(".progress")]
    if not chain_files:
        raise ValueError("official archive contains no Cobaya chain .N.txt files")
    if not updated_files:
        raise ValueError("official archive contains no Cobaya updated.yaml")

    manifests = [
        {
            "path": str(path.relative_to(extracted)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in files
    ]
    configs = [
        {
            "path": str(path.relative_to(extracted)),
            "sha256": sha256_file(path),
            "summary": compact_config(path),
        }
        for path in updated_files
    ]
    chains = [
        {
            "path": str(path.relative_to(extracted)),
            "sha256": sha256_file(path),
            "rows": chain_rows(path),
            "size_bytes": path.stat().st_size,
        }
        for path in chain_files
    ]
    total_rows = sum(row["rows"] for row in chains)
    return {
        "schema": SCHEMA,
        "state": "OFFICIAL_ACT_DR6_02_ACTLITE_LCDM_REFERENCE_CHAIN_CUSTODY_MATERIALIZED",
        "claim_allowed": False,
        "publication_ready": False,
        "token": "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION",
        "authority": {
            "provider": "NASA/GSFC LAMBDA",
            "product": "ACT DR6.02 MCMC Chains: LCDM / actlite_lcdm_camb",
            "source_url": source_url,
            "delivery_date": "2025-03-18",
            "archive_name": archive.name,
            "archive_size_bytes": archive.stat().st_size,
            "archive_sha256": sha256_file(archive),
        },
        "custody": {
            "file_count": len(files),
            "chain_file_count": len(chain_files),
            "updated_yaml_count": len(updated_files),
            "progress_file_count": len(progress_files),
            "total_noncomment_chain_rows": total_rows,
            "files": manifests,
            "chains": chains,
            "configs": configs,
            "progress": [
                {"path": str(path.relative_to(extracted)), "sha256": sha256_file(path)}
                for path in progress_files
            ],
        },
        "reference_role": {
            "official_reference_posterior_available": True,
            "locally_reproduced_from_frozen_config": False,
            "local_chain_convergence_proven": False,
        },
        "resolved_token": None,
        "reduces_token": "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION",
        "next_required_actions": [
            "map the official updated.yaml parameter and likelihood conventions to the pinned ACT materialization authority",
            "freeze the local sampler seed/chains/stopping policy before execution",
            "execute a local posterior with raw-chain custody",
            "require local convergence and compare marginals against this official reference chain",
        ],
        "scientific_boundary": (
            "Official reference-chain custody gives a comparison authority but is not local posterior reproduction. "
            "RLL CMB perturbations remain outside this LCDM control scope."
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
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--extracted", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = build(args.archive, args.extracted, args.source_url)
    atomic_json(args.output, payload)
    print(json.dumps({
        "state": payload["state"],
        "chain_file_count": payload["custody"]["chain_file_count"],
        "total_rows": payload["custody"]["total_noncomment_chain_rows"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
