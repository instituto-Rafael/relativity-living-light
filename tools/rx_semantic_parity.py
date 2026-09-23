#!/usr/bin/env python3
"""Rx semantic parity ledger.

Measures the currently intentional semantic differences between the historical
Structure-D approximation layer and the canonical freestanding evaluator.

No third-party packages. No training. No AI runtime.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.cosmology import (
    C_KMS,
    bao_prediction,
    chi2_covariance,
    cmb_prediction,
    comoving_distance_mpc,
    fsigma8_prediction,
    hubble,
    rd_drag_mpc,
)
from rx.kernel import dump_json, invert_matrix, load_json, read_csv
OUT_JSON = ROOT / "results" / "rx_semantic_parity.json"
OUT_MD = ROOT / "results" / "rx_semantic_parity.md"

hz = read_csv(ROOT / "data" / "real" / "cosmology" / "Hz_cosmic_chronometers_independent.csv")
bao = read_csv(ROOT / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv")
growth = read_csv(ROOT / "data" / "real" / "cosmology" / "fsigma8_growth_real.csv")
cmb = load_json(ROOT / "data" / "real" / "CMB_shift_real.json")

cov_rows = read_csv(ROOT / "data" / "real" / "desi_dr2_bao_covariance.csv")
bao_cov = []
for row in cov_rows:
    keys = sorted((key for key in row if key != ""), key=lambda value: int(value))
    bao_cov.append([float(row[key]) for key in keys])
bao_inv = invert_matrix(bao_cov)
cmb_inv = invert_matrix(cmb["covariance"])

profiles = {
    "LCDM": {
        "vector": [
            67.66725167785673,
            0.3162598585368923,
            0.04900975504762562 * (67.66725167785673 / 100.0) ** 2,
            0.811,
        ],
        "rd_freestanding": 149.8314329013423,
        "rs_star_freestanding": 143.67973843293154,
    },
    "RLL": {
        "vector": [
            66.99367300987414,
            0.32475606452625294,
            0.011594905594391598,
            11.452558895186602,
            0.22656819958262459,
            0.04993606066218619 * (66.99367300987414 / 100.0) ** 2,
            0.811,
        ],
        "rd_freestanding": 148.98654354573253,
        "rs_star_freestanding": 142.91992714632195,
    },
}

def component_chi2(model, profile, semantics):
    vector = profile["vector"]

    chi_hz = 0.0
    for row in hz:
        pred = hubble(model, float(row["z"]), vector)
        chi_hz += ((float(row["H_obs"]) - pred) / float(row["sigma_H"])) ** 2

    if semantics == "structure_d":
        rd = rd_drag_mpc(model, vector)
    else:
        rd = float(profile["rd_freestanding"])

    bao_predictions = []
    cache = {}
    for row in bao:
        z = float(row["z_eff"])
        if z not in cache:
            cache[z] = comoving_distance_mpc(model, z, vector, steps=512, integration_mode="log1p")
        dm = cache[z]
        hz_model = hubble(model, z, vector)
        obs = row["observable"]
        if obs == "DM_over_rd":
            pred = dm / rd
        elif obs == "DH_over_rd":
            pred = (C_KMS / hz_model) / rd
        elif obs == "DV_over_rd":
            pred = (z * C_KMS * dm * dm / hz_model) ** (1.0 / 3.0) / rd
        else:
            raise ValueError(obs)
        bao_predictions.append(pred)
    chi_bao = chi2_covariance(
        [float(row["value"]) for row in bao],
        bao_predictions,
        bao_inv,
    )

    growth_mode = "structure_d_proxy" if semantics == "structure_d" else "freestanding_growth"
    chi_growth = 0.0
    for row in growth:
        pred = fsigma8_prediction(
            model,
            float(row["z"]),
            vector,
            mode=growth_mode,
            steps=512,
        )
        chi_growth += ((float(row["fs8"]) - pred) / float(row["sigma"])) ** 2

    if semantics == "structure_d":
        cmb_pred = cmb_prediction(
            model,
            vector,
            z_cmb=float(cmb["z_CMB"]),
            steps=2048,
            acoustic_mode="structure_d_rd",
        )
    else:
        cmb_pred = cmb_prediction(
            model,
            vector,
            z_cmb=float(cmb["z_CMB"]),
            steps=2048,
            acoustic_mode="freestanding_rs_star",
            rs_star_mpc=float(profile["rs_star_freestanding"]),
        )
    cmb_obs = [float(cmb["R_obs"]), float(cmb["la_obs"]), float(cmb["ob_h2_obs"])]
    chi_cmb = chi2_covariance(cmb_obs, cmb_pred, cmb_inv)

    return {
        "Hz": chi_hz,
        "DESI_DR2_BAO": chi_bao,
        "fsigma8": chi_growth,
        "CMB_shift": chi_cmb,
        "total": chi_hz + chi_bao + chi_growth + chi_cmb,
        "rd_used_mpc": rd,
        "cmb_prediction": cmb_pred,
    }

rows = {}
for model, profile in profiles.items():
    structure_d = component_chi2(model, profile, "structure_d")
    freestanding = component_chi2(model, profile, "freestanding")
    rows[model] = {
        "structure_d_semantics": structure_d,
        "freestanding_projection": freestanding,
        "delta_freestanding_minus_structure_d": {
            key: freestanding[key] - structure_d[key]
            for key in ("Hz", "DESI_DR2_BAO", "fsigma8", "CMB_shift", "total")
        },
        "rd_formula_minus_freestanding_mpc": (
            rd_drag_mpc(model, profile["vector"]) - float(profile["rd_freestanding"])
        ),
    }

payload = {
    "schema": "rll.rx.semantic_parity.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "training": False,
    "ai_runtime": False,
    "third_party_python_dependencies": [],
    "common_surface": {
        "Hz": len(hz),
        "DESI_DR2_BAO": len(bao),
        "fsigma8": len(growth),
        "CMB_parameters": 3,
    },
    "profiles": rows,
    "gates": {
        "background_model_equations_shared": "PASS_BY_CONTRACT",
        "growth_semantics_equal": False,
        "growth_semantics_state": "CONTRACT_DIVERGENCE",
        "cmb_acoustic_semantics_equal": False,
        "cmb_acoustic_semantics_state": "CONTRACT_DIVERGENCE",
        "rd_semantics_equal": False,
        "rd_semantics_state": "CONTRACT_DIVERGENCE",
        "radiation_density_semantics_equal": False,
        "radiation_density_semantics_state": "CONTRACT_DIVERGENCE",
        "claim_allowed": False,
    },
    "interpretation": (
        "A parity delta here is not evidence for or against RLL. It identifies "
        "differences in runtime semantics that must be reconciled before numerical "
        "results from Structure-D and freestanding routes are compared as equivalent. "
        "The freestanding projection here does not claim binary parity because Rx currently "
        "uses Omega_r=9.0e-5 while FASE18E/freestanding profiles use 9.18e-5."
    ),
}

dump_json(OUT_JSON, payload)

lines = [
    "# Rx semantic parity ledger",
    "",
    "No training. No AI runtime. No third-party Python dependencies.",
    "",
    "| model | component | Structure-D semantics | freestanding semantics | delta |",
    "|---|---|---:|---:|---:|",
]
for model, record in rows.items():
    for key in ("Hz", "DESI_DR2_BAO", "fsigma8", "CMB_shift", "total"):
        a = record["structure_d_semantics"][key]
        b = record["freestanding_projection"][key]
        lines.append("| %s | %s | %.8f | %.8f | %.8f |" % (model, key, a, b, b - a))
    lines.append(
        "| %s | rd_formula - rd_freestanding [Mpc] | %.8f | — | — |"
        % (model, record["rd_formula_minus_freestanding_mpc"])
    )

lines += [
    "",
    "## Gates",
    "",
    "- background model equations: PASS_BY_CONTRACT",
    "- growth semantics: CONTRACT_DIVERGENCE",
    "- CMB acoustic-scale semantics: CONTRACT_DIVERGENCE",
    "- r_d semantics: CONTRACT_DIVERGENCE",
    "- radiation density Ωr: CONTRACT_DIVERGENCE (9.0e-5 vs 9.18e-5)",
    "- claim_allowed: false",
    "",
    "These divergences must be resolved explicitly before cross-runtime chi2 values are treated as parity evidence.",
]
OUT_MD.parent.mkdir(parents=True, exist_ok=True)
OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("RX_SEMANTIC_PARITY=PASS_LEDGER")
print("growth=CONTRACT_DIVERGENCE cmb=CONTRACT_DIVERGENCE rd=CONTRACT_DIVERGENCE radiation=CONTRACT_DIVERGENCE")
print("claim_allowed=False")
print("wrote", OUT_JSON.relative_to(ROOT))
print("wrote", OUT_MD.relative_to(ROOT))
