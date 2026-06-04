#!/usr/bin/env python3
"""Fetch/materialize real cosmology data for the RLL proof.

Strategy: use committed public real-data products first, then remote metadata, then
embedded fallback. DESI DR2 BAO is materialized from the public Cobaya/DESI DR2
mean and covariance files committed under data/real/cosmology/desi_bao_dr2_cobaya.

No heavy dependencies: standard library + PyYAML only.
"""

from __future__ import annotations

import json
import math
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DATA = HERE / "data"
OUT = HERE / "fetched"
DESI_COBAYA = REPO / "data" / "real" / "cosmology" / "desi_bao_dr2_cobaya"
TIMEOUT = 20

TRACER_BY_Z = {
    "0.295": "BGS",
    "0.510": "LRG1",
    "0.706": "LRG2",
    "0.934": "LRG3_PLUS_ELG1",
    "1.321": "ELG2",
    "1.484": "QSO",
    "2.330": "Lya",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def try_download(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RLL-validacao/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  remote unreachable ({exc.__class__.__name__}); using committed/fallback data")
        return None


def z_key(z: float) -> str:
    return f"{z:.3f}"


def as_rll_observable(quantity: str) -> str:
    return quantity.replace("_rs", "_rd")


def load_cobaya_mean(path: Path) -> list[dict]:
    points: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        z_raw, value_raw, quantity = line.split()
        z = float(z_raw)
        observable = as_rll_observable(quantity)
        points.append({
            "tracer": TRACER_BY_Z[z_key(z)],
            "z_eff": z,
            "observable": observable,
            "value": float(value_raw),
        })
    return points


def load_cobaya_covariance(path: Path) -> list[list[float]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append([float(item) for item in line.split()])
    return rows


def attach_covariance(points: list[dict], covariance: list[list[float]]) -> None:
    if len(points) != len(covariance) or any(len(row) != len(points) for row in covariance):
        raise ValueError("DESI covariance matrix shape does not match mean vector")

    for idx, point in enumerate(points):
        point["sigma"] = math.sqrt(covariance[idx][idx])

    for i, point in enumerate(points):
        for j, other in enumerate(points):
            if i == j:
                continue
            if point["tracer"] != other["tracer"] or abs(point["z_eff"] - other["z_eff"]) > 1e-9:
                continue
            cov = covariance[i][j]
            if cov == 0.0:
                continue
            corr = cov / (point["sigma"] * other["sigma"])
            point["paired_observable"] = other["observable"]
            point["correlation_coefficient"] = round(corr, 12)
            point["covariance"] = cov
            break


def load_committed_desi_dr2() -> dict | None:
    mean_path = DESI_COBAYA / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
    cov_path = DESI_COBAYA / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
    manifest_path = DESI_COBAYA / "MANIFEST.json"
    if not (mean_path.exists() and cov_path.exists() and manifest_path.exists()):
        return None

    points = load_cobaya_mean(mean_path)
    attach_covariance(points, load_cobaya_covariance(cov_path))
    return {
        "meta": {
            "schema": "rll.validacao_real.desi_dr2_bao.v2",
            "release": "desi_dr2_bao_2025",
            "source_table": "DESI DR2 Results II public BAO likelihood mean/covariance",
            "source_url": "https://github.com/CobayaSampler/bao_data/tree/master/desi_bao_dr2",
            "zenodo_record": "https://zenodo.org/records/16644577",
            "unit_note": "DM_over_rd, DH_over_rd, DV_over_rd are dimensionless (distance / r_d). Cobaya file names use rs; RLL normalizes labels to rd.",
            "status": "real_committed_public_likelihood",
            "purpose": "Canonical real DESI DR2 BAO anchor with covariance for offline proof.",
            "local_manifest": str(manifest_path.relative_to(REPO)),
        },
        "points": points,
    }


def materialize(source: dict) -> dict:
    sid = source["id"]
    fallback = DATA / Path(source["embedded_fallback"]).name
    portal = source.get("remote", {}).get("portal", "")
    print(f"[{sid}] portal: {portal or 'n/a'}")

    raw = try_download(portal) if portal else None
    payload = load_committed_desi_dr2() if sid == "desi_dr2_bao" else None
    used = "committed_public_desi_dr2_cobaya_likelihood" if payload else "embedded_fallback"
    if payload is None:
        payload = load_yaml(fallback)
        if raw:
            used = "remote_metadata_then_embedded_fallback"

    provenance = {
        "source_id": sid,
        "fetched_utc": utc_now(),
        "portal": portal,
        "remote_bytes": (len(raw) if raw else 0),
        "used": used,
        "n_points": len(payload.get("points", [])),
    }
    return {"payload": payload, "provenance": provenance}


def main() -> int:
    sources = load_yaml(HERE / "sources.yml")["sources"]
    OUT.mkdir(exist_ok=True)
    manifest = {"generated_utc": utc_now(), "sources": []}

    for source in sources:
        result = materialize(source)
        out_path = OUT / f"{source['id']}.yml"
        out_path.write_text(yaml.safe_dump(result["payload"], sort_keys=False, allow_unicode=True), encoding="utf-8")
        manifest["sources"].append(result["provenance"])
        print(f"  -> wrote {out_path.relative_to(HERE)} ({result['provenance']['n_points']} points)")

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {(OUT / 'manifest.json').relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
