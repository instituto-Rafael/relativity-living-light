#!/usr/bin/env python3
"""
RLL_HOMEOSTATIC_FIELD_GATE

Evidence boundary:
- This is a governance/test gate for the RLL homeostatic-field hypothesis.
- It does not prove new gravity, dark energy, dark matter, or biological causality.
- It measures whether a supplied time series is compatible with a bounded
  field+substrate+resistance+homeostasis saturation pattern better than a
  passive baseline.

Inputs:
  CSV with columns similar to the RAFAELIA cosmo-bio proxy series:
  planet_id, day, BioDriver, BioStressIndex, risk_resp, risk_cardio,
  risk_neuro, risk_infect, Kymaya_heat, T_mod

If no CSV is supplied, the script runs a deterministic synthetic self-test so
GitHub Actions can validate the implementation without external data.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import defaultdict
from statistics import mean
from typing import Dict, Iterable, List

EPS = 1.0e-12

REQUIRED = [
    "planet_id",
    "day",
    "BioDriver",
    "BioStressIndex",
    "risk_resp",
    "risk_cardio",
    "risk_neuro",
    "risk_infect",
    "Kymaya_heat",
    "T_mod",
]


def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def parse_float(row: dict, key: str) -> float:
    try:
        return float(row.get(key, 0.0))
    except Exception:
        return 0.0


def load_csv(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"missing required columns: {missing}")
        rows = []
        for row in reader:
            rows.append(row)
        return rows


def synthetic_rows(days: int = 720, n_planets: int = 4) -> List[dict]:
    rows: List[dict] = []
    for p in range(n_planets):
        pid = f"SYN{p:02d}"
        phase = p * 0.7
        for day in range(days):
            t = day / max(days - 1, 1)
            driver = clamp01(0.25 + 0.55 * (1.0 - math.exp(-4.0 * t)) + 0.04 * math.sin(day / 29.0 + phase))
            stress = clamp01(0.45 * math.exp(-2.2 * t) + 0.08 * math.sin(day / 17.0 + phase))
            heat = clamp01(0.30 + 0.25 * math.sin(day / 90.0 + phase) + 0.2 * driver)
            tmod = clamp01(0.20 + 0.65 * (1.0 - math.exp(-3.0 * t)))
            risks = [clamp01(stress + 0.02 * math.sin(day / (11.0 + i) + phase)) for i in range(4)]
            rows.append({
                "planet_id": pid,
                "day": str(day),
                "BioDriver": f"{driver:.8f}",
                "BioStressIndex": f"{stress:.8f}",
                "risk_resp": f"{risks[0]:.8f}",
                "risk_cardio": f"{risks[1]:.8f}",
                "risk_neuro": f"{risks[2]:.8f}",
                "risk_infect": f"{risks[3]:.8f}",
                "Kymaya_heat": f"{heat:.8f}",
                "T_mod": f"{tmod:.8f}",
            })
    return rows


def occupancy_proxy(row: dict) -> float:
    """Proxy for reorganized occupation under field+substrate+homeostasis.

    This is deliberately dimensionless and bounded. It is a gate variable,
    not a physical density claim.
    """
    phi = parse_float(row, "BioDriver")
    stress = parse_float(row, "BioStressIndex")
    risk = mean([
        parse_float(row, "risk_resp"),
        parse_float(row, "risk_cardio"),
        parse_float(row, "risk_neuro"),
        parse_float(row, "risk_infect"),
    ])
    heat = parse_float(row, "Kymaya_heat")
    tmod = parse_float(row, "T_mod")

    substrate = 1.0 - stress
    homeo = 1.0 - risk
    diss = 0.5 * stress + 0.5 * risk

    # Field + substrate + time modulation + heat support, penalized by dissipation.
    occ = (0.42 * phi * substrate) + (0.26 * homeo) + (0.20 * tmod) + (0.12 * heat) - (0.18 * diss)
    return clamp01(occ)


def passive_baseline(row: dict) -> float:
    """Passive baseline without homeostatic field coupling."""
    phi = parse_float(row, "BioDriver")
    stress = parse_float(row, "BioStressIndex")
    return clamp01(0.5 * phi + 0.5 * (1.0 - stress))


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


def analyze(rows: List[dict], tail_fraction: float = 0.20) -> dict:
    groups: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("planet_id", "UNKNOWN"))].append(row)

    planet_results = []
    all_occ: List[float] = []
    all_target: List[float] = []

    for pid, grows in sorted(groups.items()):
        grows = sorted(grows, key=lambda r: int(float(r.get("day", 0))))
        occ = [occupancy_proxy(r) for r in grows]
        base = [passive_baseline(r) for r in grows]
        if not occ:
            continue
        sorted_occ = sorted(occ)
        q_index = min(len(sorted_occ) - 1, max(0, int(0.95 * (len(sorted_occ) - 1))))
        buffer_target = sorted_occ[q_index]
        tail_n = max(10, int(len(occ) * tail_fraction)) if len(occ) >= 10 else len(occ)
        tail_occ = occ[-tail_n:]
        tail_base = base[-tail_n:]
        residual = mean(abs(buffer_target - x) / (buffer_target + EPS) for x in tail_occ)
        base_residual = mean(abs(buffer_target - x) / (buffer_target + EPS) for x in tail_base)
        improvement = (base_residual - residual) / (base_residual + EPS)
        trend = (mean(tail_occ) - mean(occ[:tail_n])) if tail_n < len(occ) else 0.0
        planet_results.append({
            "planet_id": pid,
            "n": len(occ),
            "buffer_target": buffer_target,
            "tail_mean_occupancy": mean(tail_occ),
            "residual": residual,
            "passive_residual": base_residual,
            "improvement_vs_passive": improvement,
            "early_to_tail_delta": trend,
        })
        all_occ.extend(tail_occ)
        all_target.extend([buffer_target] * len(tail_occ))

    residual_global = mean([p["residual"] for p in planet_results]) if planet_results else 1.0
    improvement_global = mean([p["improvement_vs_passive"] for p in planet_results]) if planet_results else 0.0
    corr_occ_target = corr(all_occ, all_target)

    if residual_global <= 0.10 and improvement_global >= 0.15:
        status = "FORTE_PROXY_ONLY"
    elif residual_global <= 0.18 and improvement_global >= 0.05:
        status = "NEUTRO_ALTO_PROXY_ONLY"
    elif residual_global <= 0.30:
        status = "NEUTRO_PROXY_ONLY"
    else:
        status = "FRACO_PROXY_ONLY"

    return {
        "gate": "RLL_HOMEOSTATIC_FIELD_GATE",
        "claim_allowed_physical_gravity": False,
        "evidence_class": "proxy_time_series_only",
        "status": status,
        "global": {
            "planets": len(planet_results),
            "residual_mean": residual_global,
            "improvement_vs_passive_mean": improvement_global,
            "tail_occ_target_corr": corr_occ_target,
        },
        "criteria": {
            "FORTE_PROXY_ONLY": "residual_mean <= 0.10 and improvement_vs_passive_mean >= 0.15",
            "NEUTRO_ALTO_PROXY_ONLY": "residual_mean <= 0.18 and improvement_vs_passive_mean >= 0.05",
            "physical_claim": "BLOCKED until cosmological/lab data and adversarial baselines pass",
        },
        "planet_results": planet_results,
    }


def write_outputs(result: dict, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    json_path = os.path.join(outdir, "rll_homeostatic_field_gate_results.json")
    csv_path = os.path.join(outdir, "rll_homeostatic_field_gate_results.csv")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, sort_keys=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "planet_id", "n", "buffer_target", "tail_mean_occupancy", "residual",
            "passive_residual", "improvement_vs_passive", "early_to_tail_delta"
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in result["planet_results"]:
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=None, help="CSV input path. If absent, deterministic synthetic self-test is used.")
    ap.add_argument("--outdir", default="artifacts/homeostatic_field_gate")
    ap.add_argument("--fail-on-fraco", action="store_true")
    args = ap.parse_args()

    if args.input:
        rows = load_csv(args.input)
        source = args.input
    else:
        rows = synthetic_rows()
        source = "synthetic_self_test"

    result = analyze(rows)
    result["source"] = source
    write_outputs(result, args.outdir)

    print(json.dumps({
        "gate": result["gate"],
        "source": result["source"],
        "status": result["status"],
        "global": result["global"],
        "claim_allowed_physical_gravity": result["claim_allowed_physical_gravity"],
    }, indent=2, sort_keys=True))

    if args.fail_on_fraco and result["status"].startswith("FRACO"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
