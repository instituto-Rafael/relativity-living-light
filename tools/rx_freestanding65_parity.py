#!/usr/bin/env python3
"""Exact Rx mirror of the canonical freestanding joint65 Q16 receipt.

No fitting, no training, no AI runtime. This gate mirrors:
- rll_canonical_real_inputs.c Q16 parsing/evidence accumulation
- rll_canonical_real.c freestanding model math
- rll_canonical_real_models.c fixed FASE18E profiles
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.freestanding_math import (
    Q16,
    chi_diag_q16,
    cmb_chi_q16,
    predict,
    q16_from_float,
    q16_from_text,
    q16_to_float,
)
from rx.kernel import load_json, read_csv

HZ_PATH = ROOT / "data" / "real" / "Hz_data_real.csv"
BAO_PATH = ROOT / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
GROWTH_PATH = ROOT / "data" / "real" / "cosmology" / "fsigma8_growth_real.csv"
CMB_PATH = ROOT / "data" / "real" / "CMB_shift_real.json"

hz = read_csv(HZ_PATH)
bao = read_csv(BAO_PATH)
growth = read_csv(GROWTH_PATH)
cmb = load_json(CMB_PATH)

profiles = {
    "LCDM": {
        "params": {
            "H0": 67.66725167785673,
            "Om": 0.3162598585368923,
            "Ob": 0.04900975504762562,
            "Or": 9.18e-5,
            "Os0": 0.0,
            "zt": 1.0,
            "wt": 0.3,
            "sigma8": 0.811,
            "gamma": 0.55,
            "rd": 149.8314329013423,
            "rs_star": 143.67973843293154,
            "steps": 1024,
        },
        "reference_q16": 4641555,
    },
    "RLL": {
        "params": {
            "H0": 66.99367300987414,
            "Om": 0.32475606452625294,
            "Ob": 0.04993606066218619,
            "Or": 9.18e-5,
            "Os0": 0.011594905594391598,
            "zt": 11.452558895186602,
            "wt": 0.22656819958262459,
            "sigma8": 0.811,
            "gamma": 0.55,
            "rd": 148.98654354573253,
            "rs_star": 142.91992714632195,
            "steps": 1024,
        },
        "reference_q16": 4261420,
    },
}

def diagonal_block(rows, model, params, observable_of, z_key, value_key, sigma_key):
    total = 0
    count = 0
    for row in rows:
        zq = q16_from_text(row[z_key])
        z = q16_to_float(zq)
        obsq = q16_from_text(row[value_key])
        sigq = q16_from_text(row[sigma_key])
        prediction = predict(observable_of(row), z, params, model)
        modelq = q16_from_float(prediction)
        total += chi_diag_q16(obsq, modelq, sigq)
        count += 1
    return total, count

def cmb_block(model, params):
    zq = q16_from_text(str(cmb["z_CMB"]))
    z = q16_to_float(zq)
    obs = [
        q16_from_text(str(cmb["R_obs"])),
        q16_from_text(str(cmb["la_obs"])),
        q16_from_text(str(cmb["ob_h2_obs"])),
    ]
    sigma = [
        q16_from_text(str(cmb["R_sig"])),
        q16_from_text(str(cmb["la_sig"])),
        q16_from_text(str(cmb["ob_h2_sig"])),
    ]
    modelq = [
        q16_from_float(predict("CMB_R", z, params, model)),
        q16_from_float(predict("CMB_LA", z, params, model)),
        q16_from_float(predict("OBH2", z, params, model)),
    ]
    corr = [q16_from_text(str(value)) for row in cmb["correlation_matrix"] for value in row]
    return cmb_chi_q16(obs, modelq, sigma, corr), modelq

def bao_observable(row):
    value = row["observable"]
    if value == "DV_over_rd":
        return "DV"
    if value == "DM_over_rd":
        return "DM"
    if value == "DH_over_rd":
        return "DH"
    raise ValueError(value)

rows_out = {}
failures = []

for model, profile in profiles.items():
    params = profile["params"]
    hz_q16, n_hz = diagonal_block(
        hz, model, params, lambda row: "HZ", "z", "H_obs", "sigma_H"
    )
    growth_q16, n_growth = diagonal_block(
        growth, model, params, lambda row: "FS8", "z", "fs8", "sigma"
    )
    bao_q16, n_bao = diagonal_block(
        bao, model, params, bao_observable, "z_eff", "value", "sigma"
    )
    cmb_q16, cmb_model_q16 = cmb_block(model, params)
    total_q16 = hz_q16 + growth_q16 + bao_q16 + cmb_q16
    reference_q16 = int(profile["reference_q16"])
    delta_q16 = total_q16 - reference_q16
    passed = delta_q16 == 0

    rows_out[model] = {
        "components_q16": {
            "Hz": hz_q16,
            "fsigma8": growth_q16,
            "DESI_DR2_BAO": bao_q16,
            "CMB_shift": cmb_q16,
            "total": total_q16,
        },
        "components_decoded": {
            "Hz": hz_q16 / Q16,
            "fsigma8": growth_q16 / Q16,
            "DESI_DR2_BAO": bao_q16 / Q16,
            "CMB_shift": cmb_q16 / Q16,
            "total": total_q16 / Q16,
        },
        "cmb_model_q16": cmb_model_q16,
        "reference_q16": reference_q16,
        "reference_decoded": reference_q16 / Q16,
        "delta_q16": delta_q16,
        "delta_decoded": delta_q16 / Q16,
        "pass": passed,
    }

    print(
        ("PASS" if passed else "FAIL"),
        model,
        "q16=%d" % total_q16,
        "reference=%d" % reference_q16,
        "delta=%d" % delta_q16,
        "decoded=%.9f" % (total_q16 / Q16),
    )
    print(
        " components",
        "Hz=%d" % hz_q16,
        "growth=%d" % growth_q16,
        "BAO=%d" % bao_q16,
        "CMB=%d" % cmb_q16,
    )
    if not passed:
        failures.append(model)

payload = {
    "schema": "rll.rx.freestanding65_parity.v2",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "surface": {
        "Hz": len(hz),
        "BAO": len(bao),
        "fsigma8": len(growth),
        "CMB": 3,
        "N": len(hz) + len(bao) + len(growth) + 3,
    },
    "mechanics": {
        "observation_quantization": "Q16.16",
        "model_quantization": "Q16.16",
        "axis_quantization": "Q16.16",
        "Hz_growth_BAO_metric": "diagonal_Q16_chi2",
        "CMB_metric": "Q16_correlation_matrix_chi2",
        "freestanding_math_mirror": True,
    },
    "reference_receipt": "artifacts/canonical-coupling/joint-real-model-v2.json",
    "rows": rows_out,
    "pass": not failures,
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
    "boundary": (
        "Exact receipt parity is an implementation/reproduction gate. "
        "It is not a new fit or scientific model-selection claim."
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
