#!/usr/bin/env python3
"""Rx parity gate against the canonical freestanding 65-observation profiles.

No fitting, no training, no AI runtime. The goal is implementation parity.
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

from rx.cosmology import C_KMS, unpack
from rx.kernel import invert_matrix, load_json, quad_form, read_csv, simpson
from rx.sound_horizon import e2_with_omega_r

OMEGA_R = 9.18e-5
STEPS = 1024

HZ_PATH = ROOT / "data" / "real" / "Hz_data_real.csv"
BAO_PATH = ROOT / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
GROWTH_PATH = ROOT / "data" / "real" / "cosmology" / "fsigma8_growth_real.csv"
CMB_PATH = ROOT / "data" / "real" / "CMB_shift_real.json"

hz = read_csv(HZ_PATH)
bao = read_csv(BAO_PATH)
growth = read_csv(GROWTH_PATH)
cmb = load_json(CMB_PATH)
cmb_inv = invert_matrix(cmb["covariance"])

profiles = {
    "LCDM": {
        "vector": [67.66725167785673, 0.3162598585368923, 0.022440865749970035, 0.811],
        "rd_mpc": 149.8314329013423,
        "rs_star_mpc": 143.67973843293154,
        "reference_chi2": 70.82450866699219,
    },
    "RLL": {
        "vector": [
            66.99367300987414,
            0.32475606452625294,
            0.011594905594391598,
            11.452558895186602,
            0.22656819958262459,
            0.022412064168652816,
            0.811,
        ],
        "rd_mpc": 148.98654354573253,
        "rs_star_mpc": 142.91992714632195,
        "reference_chi2": 65.02410888671875,
    },
}

def hubble(model, z, vector):
    p = unpack(model, vector)
    return p["H0"] * math.sqrt(max(e2_with_omega_r(model, z, vector, OMEGA_R), 1.0e-300))

def comoving(model, z, vector):
    p = unpack(model, vector)
    xmax = math.log1p(float(z))
    return (C_KMS / p["H0"]) * simpson(
        lambda x: math.exp(x)
        / math.sqrt(
            max(
                e2_with_omega_r(model, math.exp(x) - 1.0, vector, OMEGA_R),
                1.0e-300,
            )
        ),
        0.0,
        xmax,
        STEPS,
    )

def omega_m_z(model, z, vector):
    p = unpack(model, vector)
    e2 = e2_with_omega_r(model, z, vector, OMEGA_R)
    return p["Om"] * (1.0 + float(z)) ** 3 / max(e2, 1.0e-300)

def growth_factor(model, z, vector):
    xmax = math.log1p(float(z))
    integral = simpson(
        lambda x: max(
            omega_m_z(model, math.exp(x) - 1.0, vector),
            1.0e-300,
        ) ** 0.55,
        0.0,
        xmax,
        STEPS,
    )
    return math.exp(-integral)

def fsigma8(model, z, vector):
    p = unpack(model, vector)
    f = max(omega_m_z(model, z, vector), 1.0e-300) ** 0.55
    return f * p["sigma8"] * growth_factor(model, z, vector)

def bao_chi2(model, profile):
    vector = profile["vector"]
    rd = profile["rd_mpc"]
    total = 0.0
    i = 0
    cache = {}
    while i < len(bao):
        a = bao[i]
        z = float(a["z_eff"])
        if z not in cache:
            cache[z] = comoving(model, z, vector)
        dm = cache[z]
        hzv = hubble(model, z, vector)
        if a["observable"] == "DM_over_rd":
            pa = dm / rd
        elif a["observable"] == "DH_over_rd":
            pa = (C_KMS / hzv) / rd
        elif a["observable"] == "DV_over_rd":
            pa = (z * C_KMS * dm * dm / hzv) ** (1.0 / 3.0) / rd
        else:
            raise ValueError(a["observable"])

        if (
            a.get("correlation_coefficient", "") not in ("", None)
            and i + 1 < len(bao)
            and bao[i + 1]["covariance_block"] == a["covariance_block"]
        ):
            b = bao[i + 1]
            zb = float(b["z_eff"])
            if zb not in cache:
                cache[zb] = comoving(model, zb, vector)
            dmb = cache[zb]
            hzb = hubble(model, zb, vector)
            if b["observable"] == "DM_over_rd":
                pb = dmb / rd
            elif b["observable"] == "DH_over_rd":
                pb = (C_KMS / hzb) / rd
            elif b["observable"] == "DV_over_rd":
                pb = (zb * C_KMS * dmb * dmb / hzb) ** (1.0 / 3.0) / rd
            else:
                raise ValueError(b["observable"])
            rho = float(a["correlation_coefficient"])
            xa = (float(a["value"]) - pa) / float(a["sigma"])
            xb = (float(b["value"]) - pb) / float(b["sigma"])
            total += (xa * xa - 2.0 * rho * xa * xb + xb * xb) / (1.0 - rho * rho)
            i += 2
        else:
            x = (float(a["value"]) - pa) / float(a["sigma"])
            total += x * x
            i += 1
    return total

def cmb_chi2(model, profile):
    vector = profile["vector"]
    p = unpack(model, vector)
    z = float(cmb["z_CMB"])
    dc = comoving(model, z, vector)
    pred = [
        math.sqrt(p["Om"]) * p["H0"] * dc / C_KMS,
        math.pi * dc / profile["rs_star_mpc"],
        p["Ob_h2"],
    ]
    obs = [float(cmb["R_obs"]), float(cmb["la_obs"]), float(cmb["ob_h2_obs"])]
    return quad_form([o - q for o, q in zip(obs, pred)], cmb_inv), pred

rows = {}
failures = []
tolerance_total = 0.08

for model, profile in profiles.items():
    vector = profile["vector"]
    chi_hz = 0.0
    for row in hz:
        pred = hubble(model, float(row["z"]), vector)
        chi_hz += ((float(row["H_obs"]) - pred) / float(row["sigma_H"])) ** 2

    chi_growth = 0.0
    for row in growth:
        pred = fsigma8(model, float(row["z"]), vector)
        chi_growth += ((float(row["fs8"]) - pred) / float(row["sigma"])) ** 2

    chi_bao = bao_chi2(model, profile)
    chi_cmb, cmb_pred = cmb_chi2(model, profile)
    total = chi_hz + chi_growth + chi_bao + chi_cmb
    delta = total - profile["reference_chi2"]
    passed = abs(delta) <= tolerance_total
    rows[model] = {
        "chi2": {
            "Hz": chi_hz,
            "fsigma8": chi_growth,
            "DESI_DR2_BAO": chi_bao,
            "CMB_shift": chi_cmb,
            "total": total,
        },
        "cmb_prediction": cmb_pred,
        "reference_chi2": profile["reference_chi2"],
        "delta_total": delta,
        "pass": passed,
    }
    print(
        ("PASS" if passed else "FAIL"),
        model,
        "chi2=%.9f" % total,
        "reference=%.9f" % profile["reference_chi2"],
        "delta=%.9f" % delta,
    )
    if not passed:
        failures.append(model)

payload = {
    "schema": "rll.rx.freestanding65_parity.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "surface": {"Hz": len(hz), "BAO": len(bao), "fsigma8": len(growth), "CMB": 3, "N": len(hz)+len(bao)+len(growth)+3},
    "omega_r": OMEGA_R,
    "integration_steps": STEPS,
    "reference_receipt": "artifacts/canonical-coupling/joint-real-model-v2.json",
    "tolerance_total_chi2": tolerance_total,
    "rows": rows,
    "pass": not failures,
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
    "boundary": (
        "This gate tests numerical implementation parity against fixed freestanding "
        "profiles. It is not a parameter refit or a scientific model-selection claim."
    ),
}

out = ROOT / "results" / "rx_freestanding65_parity.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if failures:
    print("RX_FREESTANDING65_PARITY=FAIL", failures)
    raise SystemExit(1)

print("RX_FREESTANDING65_PARITY=PASS")
print("claim_allowed=False training=False ai_runtime=False")
print("wrote", out.relative_to(ROOT))
