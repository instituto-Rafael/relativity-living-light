#!/usr/bin/env python3
"""
RLL_OBSERVER_MIRROR_PHOTON_GATE

Governed proxy gate for the observer/mirror/photon ledger.

Boundary:
- photon is treated as an energy/momentum information carrier, not literal dark energy.
- mirror/reflection/camera/observer are modeled as transformations of a measured signal.
- this script validates path-dependent accounting and referential consistency only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from statistics import mean
from typing import List, Dict

EPS = 1.0e-12
C = 299_792_458.0

REQUIRED = [
    "source_id", "t_emit", "luminosity", "distance", "redshift",
    "mirror_velocity", "mirror_angle_deg", "camera_gain", "observer_velocity"
]


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def f(row: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except Exception:
        return default


def synthetic_rows(n: int = 128) -> List[dict]:
    rows = []
    for i in range(n):
        z = 0.01 + 0.9 * (i / max(n - 1, 1))
        angle = (i * 7) % 80
        mv = 10_000.0 * math.sin(i / 11.0)
        ov = 7_000.0 * math.cos(i / 13.0)
        dist = 1.0e16 * (1.0 + 100.0 * z)
        lum = 1.0e26 * (1.0 + 0.1 * math.sin(i / 5.0))
        rows.append({
            "source_id": f"SYN{i:03d}",
            "t_emit": str(i),
            "luminosity": f"{lum:.8e}",
            "distance": f"{dist:.8e}",
            "redshift": f"{z:.8f}",
            "mirror_velocity": f"{mv:.8f}",
            "mirror_angle_deg": f"{angle:.8f}",
            "camera_gain": "1.0",
            "observer_velocity": f"{ov:.8f}",
        })
    return rows


def load_csv(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"missing required columns: {missing}")
        return list(reader)


def photon_flux_received(row: dict) -> float:
    lum = max(f(row, "luminosity"), 0.0)
    distance = max(f(row, "distance"), 1.0)
    z = max(f(row, "redshift"), 0.0)
    return lum / (4.0 * math.pi * distance * distance * (1.0 + z) * (1.0 + z))


def mirror_transform(row: dict) -> float:
    angle = math.radians(f(row, "mirror_angle_deg"))
    mv = f(row, "mirror_velocity")
    ov = f(row, "observer_velocity")
    relative_beta = (mv - ov) / C
    doppler_proxy = max(0.0, 1.0 + 2.0 * relative_beta * math.cos(angle))
    reflection_geometry = abs(math.cos(angle))
    gain = max(f(row, "camera_gain", 1.0), 0.0)
    return gain * doppler_proxy * reflection_geometry


def analyze(rows: List[dict]) -> Dict[str, object]:
    observed = []
    emitted = []
    transform = []
    ledger_loss = []

    for row in rows:
        rec = photon_flux_received(row)
        tr = mirror_transform(row)
        obs = rec * tr
        emit = max(f(row, "luminosity"), 0.0)
        observed.append(obs)
        emitted.append(emit)
        transform.append(tr)
        # Dimensionless ledger compression from emitted source scale into observer channel.
        ledger_loss.append(1.0 - min(obs / (emit + EPS), 1.0))

    mean_transform = mean(transform) if transform else 0.0
    mean_loss = mean(ledger_loss) if ledger_loss else 1.0
    nonzero_observed_fraction = sum(1 for x in observed if x > 0.0) / max(len(observed), 1)

    # The gate is not trying to prove dark energy. It checks that observer measurement
    # is transformed/attenuated rather than identical to emitted source luminosity.
    separation = mean_loss
    if nonzero_observed_fraction >= 0.95 and separation >= 0.95:
        status = "FORTE_PROXY_ONLY"
    elif nonzero_observed_fraction >= 0.80 and separation >= 0.80:
        status = "NEUTRO_ALTO_PROXY_ONLY"
    elif nonzero_observed_fraction >= 0.50:
        status = "NEUTRO_PROXY_ONLY"
    else:
        status = "FRACO_PROXY_ONLY"

    return {
        "gate": "RLL_OBSERVER_MIRROR_PHOTON_GATE",
        "claim_allowed_dark_energy_photon_literal": False,
        "claim_allowed_dark_matter_unseen_matter_default": False,
        "evidence_class": "synthetic_or_supplied_optical_ledger_proxy",
        "status": status,
        "global": {
            "rows": len(rows),
            "mean_transform": mean_transform,
            "mean_ledger_separation": separation,
            "nonzero_observed_fraction": nonzero_observed_fraction,
            "mean_observed_flux": mean(observed) if observed else 0.0,
        },
        "criteria": {
            "FORTE_PROXY_ONLY": "nonzero_observed_fraction >= 0.95 and mean_ledger_separation >= 0.95",
            "NEUTRO_ALTO_PROXY_ONLY": "nonzero_observed_fraction >= 0.80 and mean_ledger_separation >= 0.80",
            "physical_claim": "BLOCKED until real optical/cosmological data and adversarial baselines pass",
        },
        "invariants": [
            "observed_light != emitted_light_at_source_time",
            "photon != dark_energy_literal",
            "unseen_source_matter != dark_matter_by_default",
            "camera_register != external_observer_frame",
            "TOKEN_VAZIO is mandatory for unobserved source/remnant paths",
        ],
    }


def write_outputs(result: dict, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "rll_observer_mirror_photon_gate_results.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--outdir", default="artifacts/observer_mirror_photon_gate")
    parser.add_argument("--fail-on-fraco", action="store_true")
    args = parser.parse_args()

    rows = load_csv(args.input) if args.input else synthetic_rows()
    result = analyze(rows)
    result["source"] = args.input or "synthetic_self_test"
    write_outputs(result, args.outdir)
    print(json.dumps({
        "gate": result["gate"],
        "source": result["source"],
        "status": result["status"],
        "global": result["global"],
        "claim_allowed_dark_energy_photon_literal": result["claim_allowed_dark_energy_photon_literal"],
    }, indent=2, sort_keys=True))
    if args.fail_on_fraco and result["status"].startswith("FRACO"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
