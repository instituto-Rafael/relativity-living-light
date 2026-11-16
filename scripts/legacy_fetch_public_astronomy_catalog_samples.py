#!/usr/bin/env python3
"""
Fetch guarded public astronomy catalog samples.

This tool downloads and normalizes small public catalog samples that may be
useful for exploratory astronomy work. It does not create a cosmology likelihood
and must not be used to claim validation of RLL, dark matter, or dark energy.

Outputs by default:
- data/real/astronomy/sdss_galaxy_sample.json
- data/real/astronomy/open_supernova_catalog_sample.json
- data/provenance/public_astronomy_catalog_fetch_manifest.json

CMB handling:
- This script never writes a generated CMB template under data/real.
- If --include-cmb-template is used, the template is written only under
  data/examples/cmb_power_spectrum_template.json and marked SYNTHETIC_TEMPLATE.
- If --cmb-local-file is supplied, it is copied as a local external input and
  recorded as user-supplied provenance, not as an official Planck likelihood.

Example:
  python scripts/fetch_public_astronomy_catalog_samples.py --sdss-limit 200 --osc-limit 200
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


SDSS_SQL_TEMPLATE = (
    "SELECT TOP {limit} p.objid, p.ra, p.dec, s.z, p.dered_r AS mag_r "
    "FROM PhotoObj AS p JOIN SpecObj AS s ON s.bestobjid = p.objid "
    "WHERE s.class = 'GALAXY' AND s.z BETWEEN 0.001 AND 0.5 "
    "ORDER BY s.z ASC"
)

SDSS_ENDPOINT = "https://skyserver.sdss.org/dr16/SkyServerWS/SearchTools/SqlSearch"
OSC_URL = "https://sne.space/astrocats/astrocats/supernovae/output/json/supernovae.json"

CLAIM_BOUNDARY = (
    "Public astronomy catalog samples are not cosmology likelihoods and do not "
    "validate RLL, dark matter, dark energy, LCDM alternatives, or CMB claims."
)

BLOCKED_CLAIMS = [
    "RLL is validated",
    "dark matter is measured by this script",
    "dark energy is confirmed by this script",
    "CMB likelihood is reproduced",
    "SDSS/OSC samples validate cosmology",
]


class FetchError(RuntimeError):
    """Raised when an external catalog fetch fails."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(payload: Any, path: Path) -> dict[str, Any]:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def safe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def first_value(entry: dict[str, Any], key: str) -> Any:
    value = entry.get(key)
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, dict):
            return first.get("value")
        return first
    if isinstance(value, dict):
        return value.get("value")
    return value


def request_json(url: str, *, timeout: int = 60, params: dict[str, Any] | None = None) -> Any:
    try:
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={"User-Agent": "RLL-public-astronomy-fetcher/1.0"},
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # pragma: no cover - network-dependent
        raise FetchError(f"failed to fetch {url}: {exc}") from exc


def sdss_rows_from_payload(payload: Any) -> list[dict[str, Any]]:
    # SkyServer JSON has historically appeared either as a list of rows or as
    # wrapper objects containing table rows. Keep parsing intentionally tolerant.
    if isinstance(payload, list):
        source_rows = payload
    elif isinstance(payload, dict):
        if isinstance(payload.get("Rows"), list):
            source_rows = payload["Rows"]
        elif isinstance(payload.get("Table"), list):
            source_rows = payload["Table"]
        else:
            # Fall back to the first list value in the payload.
            source_rows = next((value for value in payload.values() if isinstance(value, list)), [])
    else:
        source_rows = []

    rows: list[dict[str, Any]] = []
    for row in source_rows:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "objid": safe_int(row.get("objid") or row.get("objID") or row.get("ObjID")),
                "ra": safe_float(row.get("ra") or row.get("RA")),
                "dec": safe_float(row.get("dec") or row.get("DEC")),
                "z": safe_float(row.get("z") or row.get("redshift")),
                "mag_r": safe_float(row.get("mag_r") or row.get("dered_r")),
                "dataset_state": "REAL_CATALOG_SAMPLE",
                "claim_boundary": "SDSS catalog row only; not dark-matter or dark-energy validation.",
            }
        )
    return rows


def fetch_sdss(limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sql = SDSS_SQL_TEMPLATE.format(limit=limit)
    params = {"cmd": sql, "format": "json"}
    started = time.time()
    payload = request_json(SDSS_ENDPOINT, params=params, timeout=60)
    rows = sdss_rows_from_payload(payload)
    meta = {
        "dataset_id": "sdss_dr16_galaxy_catalog_sample",
        "dataset_state": "REAL_CATALOG_SAMPLE",
        "source_url": SDSS_ENDPOINT,
        "source_release": "SDSS SkyServer DR16",
        "sql_query": sql,
        "requested_limit": limit,
        "row_count": len(rows),
        "elapsed_seconds": round(time.time() - started, 3),
        "claim_boundary": "Catalog sample only; not a cosmology likelihood and not RLL validation.",
    }
    return rows, meta


def fetch_open_supernova_catalog(limit: int | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    started = time.time()
    payload = request_json(OSC_URL, timeout=120)
    if not isinstance(payload, dict):
        raise FetchError("Open Supernova Catalog payload was not a JSON object")

    rows: list[dict[str, Any]] = []
    for name, entry in payload.items():
        if not isinstance(entry, dict):
            continue
        rows.append(
            {
                "name": str(name),
                "ra": safe_float(first_value(entry, "ra")),
                "dec": safe_float(first_value(entry, "dec")),
                "redshift": safe_float(first_value(entry, "redshift")),
                "claimed_type": first_value(entry, "claimedtype"),
                "dataset_state": "REAL_AGGREGATED_CATALOG",
                "claim_boundary": (
                    "Aggregated supernova object metadata only; not Pantheon+, DES, "
                    "Union, SH0ES, or cosmology likelihood input."
                ),
            }
        )
        if limit is not None and len(rows) >= limit:
            break

    meta = {
        "dataset_id": "open_supernova_catalog_sample",
        "dataset_state": "REAL_AGGREGATED_CATALOG",
        "source_url": OSC_URL,
        "requested_limit": limit,
        "row_count": len(rows),
        "elapsed_seconds": round(time.time() - started, 3),
        "claim_boundary": "Object catalog only; not a calibrated supernova cosmology likelihood.",
    }
    return rows, meta


def generate_cmb_template() -> list[dict[str, Any]]:
    # Deliberately illustrative. This is never written under data/real.
    ell = [2, 50, 150, 220, 300, 500, 800, 1000, 1500, 2000]
    dl = [1000.0, 4500.0, 5100.0, 5400.0, 4300.0, 2500.0, 1200.0, 800.0, 300.0, 150.0]
    return [
        {
            "ell": e,
            "Dl": d,
            "dataset_state": "SYNTHETIC_TEMPLATE",
            "claim_boundary": "Illustrative template only; not real CMB data and not a Planck likelihood.",
        }
        for e, d in zip(ell, dl)
    ]


def copy_local_cmb_file(local_file: Path, out_dir: Path, source_url: str | None) -> dict[str, Any]:
    if not local_file.exists() or not local_file.is_file():
        raise FileNotFoundError(f"missing --cmb-local-file: {local_file}")
    target = out_dir / f"cmb_local_input{local_file.suffix or '.dat'}"
    ensure_dir(target.parent)
    shutil.copy2(local_file, target)
    return {
        "dataset_id": "user_supplied_cmb_local_input",
        "dataset_state": "USER_SUPPLIED_LOCAL_FILE_NOT_VERIFIED_BY_THIS_TOOL",
        "source_url": source_url or "SOURCE_REQUIRED",
        "path": str(target),
        "sha256": sha256_file(target),
        "bytes": target.stat().st_size,
        "claim_boundary": (
            "Copied local CMB input only. This tool does not verify Planck likelihood "
            "semantics, covariance, masks, beams, nuisance parameters, or official release version."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="data/real/astronomy", help="Directory for real catalog sample outputs")
    parser.add_argument("--manifest-dir", default="data/provenance", help="Directory for provenance manifest")
    parser.add_argument("--sdss-limit", type=int, default=200, help="Number of SDSS galaxy rows to request")
    parser.add_argument("--osc-limit", type=int, default=200, help="Open Supernova Catalog rows to extract; use -1 for all")
    parser.add_argument("--skip-sdss", action="store_true", help="Skip SDSS fetch")
    parser.add_argument("--skip-osc", action="store_true", help="Skip Open Supernova Catalog fetch")
    parser.add_argument("--include-cmb-template", action="store_true", help="Write illustrative CMB template under data/examples only")
    parser.add_argument("--examples-dir", default="data/examples", help="Directory for synthetic examples/templates")
    parser.add_argument("--cmb-local-file", default=None, help="Optional local CMB input to copy with provenance warning")
    parser.add_argument("--cmb-source-url", default=None, help="Optional provenance URL for --cmb-local-file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out_dir = Path(args.out_dir)
    manifest_dir = Path(args.manifest_dir)
    examples_dir = Path(args.examples_dir)
    ensure_dir(out_dir)
    ensure_dir(manifest_dir)

    manifest: dict[str, Any] = {
        "schema": "rll.public_astronomy_catalog_fetch_manifest.v1",
        "generated_utc": utc_now(),
        "claim_boundary": CLAIM_BOUNDARY,
        "blocked_claims": BLOCKED_CLAIMS,
        "outputs": [],
        "sources": [],
    }

    if not args.skip_sdss:
        rows, meta = fetch_sdss(args.sdss_limit)
        output = write_json(rows, out_dir / "sdss_galaxy_sample.json")
        manifest["outputs"].append(output | {"dataset_id": meta["dataset_id"], "dataset_state": meta["dataset_state"]})
        manifest["sources"].append(meta)

    if not args.skip_osc:
        osc_limit = None if args.osc_limit == -1 else args.osc_limit
        rows, meta = fetch_open_supernova_catalog(osc_limit)
        output = write_json(rows, out_dir / "open_supernova_catalog_sample.json")
        manifest["outputs"].append(output | {"dataset_id": meta["dataset_id"], "dataset_state": meta["dataset_state"]})
        manifest["sources"].append(meta)

    if args.cmb_local_file:
        manifest["outputs"].append(copy_local_cmb_file(Path(args.cmb_local_file), out_dir, args.cmb_source_url))

    if args.include_cmb_template:
        output = write_json(generate_cmb_template(), examples_dir / "cmb_power_spectrum_template.json")
        manifest["outputs"].append(
            output
            | {
                "dataset_id": "cmb_power_spectrum_template",
                "dataset_state": "SYNTHETIC_TEMPLATE",
                "claim_boundary": "Template written under data/examples only; never real data.",
            }
        )

    manifest_output = write_json(manifest, manifest_dir / "public_astronomy_catalog_fetch_manifest.json")
    print(f"Wrote manifest: {manifest_output['path']}")
    print("Claim boundary:", CLAIM_BOUNDARY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
