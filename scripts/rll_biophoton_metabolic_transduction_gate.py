#!/usr/bin/env python3
"""
RLL_BIOPHOTON_METABOLIC_TRANSDUCTION_GATE

Governed proxy gate for metabolic/radiative/triboluminescent transduction.

Boundary:
- validates a bookkeeping model for photon/radiation-associated biological energy proxies;
- does not claim that biophotons are dark energy;
- does not claim that melanin is an organelle;
- does not claim that triboluminescent X-rays are a biological mechanism by default.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from statistics import mean
from typing import Dict, List

EPS = 1.0e-12

REQUIRED = [
    "sample_id",
    "time",
    "glucose",
    "fructose",
    "oxygen",
    "co2",
    "co",
    "chlorophyll_proxy",
    "mitochondria_proxy",
    "melanin_proxy",
    "radiation_proxy",
    "tribo_proxy",
    "stress_proxy",
    "macro_micro_proxy"
]


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def f(row: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except Exception:
        return default


def synthetic_rows(n: int = 360, samples: int = 4) -> List[dict]:
    rows: List[dict] = []
    for s in range(samples):
        phase = 0.41 * s
        for t in range(n):
            u = t / max(n - 1, 1)
            light = clamp01(0.50 + 0.35 * math.sin(t / 34.0 + phase))
            glucose = clamp01(0.55 + 0.25 * math.sin(t / 43.0 + phase) - 0.10 * u)
            fructose = clamp01(0.45 + 0.20 * math.cos(t / 39.0 + phase))
            oxygen = clamp01(0.60 + 0.20 * math.sin(t / 51.0 + phase))
            co2 = clamp01(0.25 + 0.35 * (1.0 - oxygen) + 0.05 * math.sin(t / 17.0))
            co = clamp01(0.03 + 0.04 * math.sin(t / 23.0 + phase))
            chlorophyll = light
            mitochondria = clamp01(0.45 * glucose + 0.25 * fructose + 0.30 * oxygen)
            melanin = clamp01(0.35 + 0.30 * math.sin(t / 77.0 + phase))
            radiation = clamp01(0.08 + 0.12 * math.sin(t / 61.0 + phase))
            tribo = clamp01(0.03 + (0.30 if t % 89 == 0 else 0.0))
            stress = clamp01(0.22 + 0.18 * radiation + 0.16 * co + 0.08 * math.sin(t / 29.0))
            macro_micro = clamp01(0.75 - 0.25 * stress + 0.05 * math.sin(t / 37.0))
            rows.append({
                "sample_id": f"BIO{s:02d}",
                "time": str(t),
                "glucose": f"{glucose:.8f}",
                "fructose": f"{fructose:.8f}",
                "oxygen": f"{oxygen:.8f}",
                "co2": f"{co2:.8f}",
                "co": f"{co:.8f}",
                "chlorophyll_proxy": f"{chlorophyll:.8f}",
                "mitochondria_proxy": f"{mitochondria:.8f}",
                "melanin_proxy": f"{melanin:.8f}",
                "radiation_proxy": f"{radiation:.8f}",
                "tribo_proxy": f"{tribo:.8f}",
                "stress_proxy": f"{stress:.8f}",
                "macro_micro_proxy": f"{macro_micro:.8f}",
            })
    return rows


def load_csv(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"missing required columns: {missing}")
        return list(reader)


def transduction_proxy(row: dict) -> float:
    sugar = 0.55 * f(row, "glucose") + 0.45 * f(row, "fructose")
    gas_balance = clamp01(0.55 * f(row, "oxygen") + 0.25 * (1.0 - f(row, "co2")) + 0.20 * (1.0 - f(row, "co")))
    organelle = 0.38 * f(row, "mitochondria_proxy") + 0.32 * f(row, "chlorophyll_proxy") + 0.30 * f(row, "melanin_proxy")
    radiation_channel = 0.55 * f(row, "radiation_proxy") + 0.45 * f(row, "tribo_proxy")
    nutrition = f(row, "macro_micro_proxy")
    stress = f(row, "stress_proxy")
    return clamp01(0.28 * sugar + 0.25 * gas_balance + 0.22 * organelle + 0.10 * radiation_channel + 0.20 * nutrition - 0.16 * stress)


def passive_metabolic_baseline(row: dict) -> float:
    sugar = 0.50 * f(row, "glucose") + 0.50 * f(row, "fructose")
    oxygen = f(row, "oxygen")
    stress = f(row, "stress_proxy")
    return clamp01(0.45 * sugar + 0.35 * oxygen + 0.20 * (1.0 - stress))


def corr(xs: List[float], ys: List[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= EPS or vy <= EPS:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def analyze(rows: List[dict]) -> Dict[str, object]:
    trans = [transduction_proxy(r) for r in rows]
    base = [passive_metabolic_baseline(r) for r in rows]
    radiation = [0.55 * f(r, "radiation_proxy") + 0.45 * f(r, "tribo_proxy") for r in rows]
    organelle = [0.38 * f(r, "mitochondria_proxy") + 0.32 * f(r, "chlorophyll_proxy") + 0.30 * f(r, "melanin_proxy") for r in rows]

    residual_vs_upper = mean(abs(1.0 - x) for x in trans) if trans else 1.0
    improvement_vs_passive = (mean(trans) - mean(base)) / (abs(mean(base)) + EPS) if base else 0.0
    rad_corr = corr(trans, radiation)
    organelle_corr = corr(trans, organelle)

    if mean(trans) >= 0.62 and improvement_vs_passive >= 0.04 and organelle_corr >= 0.45:
        status = "FORTE_PROXY_ONLY"
    elif mean(trans) >= 0.52 and organelle_corr >= 0.25:
        status = "NEUTRO_ALTO_PROXY_ONLY"
    elif mean(trans) >= 0.40:
        status = "NEUTRO_PROXY_ONLY"
    else:
        status = "FRACO_PROXY_ONLY"

    return {
        "gate": "RLL_BIOPHOTON_METABOLIC_TRANSDUCTION_GATE",
        "claim_allowed_biophoton_dark_energy_literal": False,
        "claim_allowed_melanin_organelle_literal": False,
        "claim_allowed_tribo_xray_biological_default": False,
        "evidence_class": "synthetic_or_supplied_biometabolic_proxy",
        "status": status,
        "global": {
            "rows": len(rows),
            "transduction_mean": mean(trans) if trans else 0.0,
            "passive_mean": mean(base) if base else 0.0,
            "improvement_vs_passive": improvement_vs_passive,
            "residual_vs_upper": residual_vs_upper,
            "radiation_channel_corr": rad_corr,
            "organelle_channel_corr": organelle_corr,
        },
        "criteria": {
            "FORTE_PROXY_ONLY": "transduction_mean >= 0.62 and improvement_vs_passive >= 0.04 and organelle_channel_corr >= 0.45",
            "NEUTRO_ALTO_PROXY_ONLY": "transduction_mean >= 0.52 and organelle_channel_corr >= 0.25",
            "physical_claim": "BLOCKED until lab/cosmological data and adversarial baselines pass",
        },
        "invariants": [
            "biophoton != dark_energy_literal",
            "melanin != organelle_literal",
            "chloroplast/mitochondria/melanin are treated as transduction analogues only",
            "triboluminescent_xray != biological_default_mechanism",
            "macronutrients/micronutrients/gases are bookkeeping channels, not proof of new physics",
            "TOKEN_VAZIO is mandatory for unmeasured biochemical provenance",
        ],
    }


def write_outputs(result: dict, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "rll_biophoton_metabolic_transduction_gate_results.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--outdir", default="artifacts/biophoton_metabolic_transduction_gate")
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
        "claim_allowed_biophoton_dark_energy_literal": result["claim_allowed_biophoton_dark_energy_literal"],
    }, indent=2, sort_keys=True))
    if args.fail_on_fraco and result["status"].startswith("FRACO"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
