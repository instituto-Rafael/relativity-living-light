#!/usr/bin/env python3
"""Download the small public DESI DR2 BAO likelihood files used by Cobaya.

This fetches the DESI DR2 BAO mean/covariance text files from the public
CobayaSampler/bao_data mirror plus Zenodo record metadata for DESI DR2 Results II.
It intentionally does not download the 1.3 GB Zenodo archive into git; the
manifest records the official archive so a heavy reproduction can fetch it when
needed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "data" / "real" / "cosmology" / "desi_bao_dr2_cobaya"
BASE_RAW = "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/"
ZENODO_API = "https://zenodo.org/api/records/16644577"

FILES = [
    "desi_gaussian_bao_ALL_GCcomb_mean.txt",
    "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    "desi_gaussian_bao_BGS_BRIGHT-21.35_GCcomb_mean.txt",
    "desi_gaussian_bao_BGS_BRIGHT-21.35_GCcomb_cov.txt",
    "desi_gaussian_bao_LRG_GCcomb_z0.4-0.6_mean.txt",
    "desi_gaussian_bao_LRG_GCcomb_z0.4-0.6_cov.txt",
    "desi_gaussian_bao_LRG_GCcomb_z0.6-0.8_mean.txt",
    "desi_gaussian_bao_LRG_GCcomb_z0.6-0.8_cov.txt",
    "desi_gaussian_bao_LRG+ELG_LOPnotqso_GCcomb_mean.txt",
    "desi_gaussian_bao_LRG+ELG_LOPnotqso_GCcomb_cov.txt",
    "desi_gaussian_bao_ELG_LOPnotqso_GCcomb_z1.1-1.6_mean.txt",
    "desi_gaussian_bao_ELG_LOPnotqso_GCcomb_z1.1-1.6_cov.txt",
    "desi_gaussian_bao_QSO_GCcomb_mean.txt",
    "desi_gaussian_bao_QSO_GCcomb_cov.txt",
    "desi_gaussian_bao_Lya_GCcomb_mean.txt",
    "desi_gaussian_bao_Lya_GCcomb_cov.txt",
]


def fetch(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "RLL-real-data/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_url(filename: str) -> str:
    return BASE_RAW + urllib.parse.quote(filename, safe="+._-/")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download DESI DR2 BAO Cobaya data files.")
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    entries = []

    for filename in FILES:
        url = raw_url(filename)
        payload = fetch(url, args.timeout)
        path = args.outdir / filename
        path.write_bytes(payload)
        entries.append({"file": filename, "url": url, "bytes": len(payload), "sha256": sha256(payload)})
        print(f"wrote {path.relative_to(REPO)} ({len(payload)} bytes)")

    zenodo_payload = fetch(ZENODO_API, args.timeout)
    zenodo_path = args.outdir / "zenodo_16644577_record.json"
    zenodo_path.write_bytes(zenodo_payload)
    entries.append({
        "file": zenodo_path.name,
        "url": ZENODO_API,
        "bytes": len(zenodo_payload),
        "sha256": sha256(zenodo_payload),
    })

    manifest = {
        "schema": "rll.real_data.desi_dr2_cobaya_manifest.v1",
        "generated_utc": utc_now(),
        "claim_boundary": "Real public DESI DR2 BAO likelihood files are materialized; no synthetic BAO rows or guessed covariance are generated.",
        "primary_paper": "https://arxiv.org/abs/2503.14738",
        "official_desi_papers_page": "https://data.desi.lbl.gov/doc/papers/dr2/",
        "zenodo_record": "https://zenodo.org/records/16644577",
        "cobaya_data_tree": "https://github.com/CobayaSampler/bao_data/tree/master/desi_bao_dr2",
        "files": entries,
    }
    (args.outdir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest -> {(args.outdir / 'MANIFEST.json').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
