#!/usr/bin/env python3
"""RLL Rx multiprobe real-data pipeline.

Stdlib-only / no AI runtime / no model training.
Current data surface is derived from files at runtime; no hard-coded N.
"""

from __future__ import annotations

import hashlib
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from rx.kernel import (
    bounded_coordinate_search,
    dump_json,
    invert_matrix,
    load_json,
    read_csv,
    write_csv,
    write_svg_chart,
)
from rx.cosmology import (
    BOUNDS,
    MODEL_ORDER,
    PARAM_NAMES,
    bao_prediction,
    chi2_covariance,
    cmb_prediction,
    e2,
    fsigma8_prediction,
    hubble,
    omega_lambda,
    unpack,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "validacao_real" / "results_rx"
FIGS = RESULTS / "figures"
HZ_PATH = ROOT / "data" / "real" / "cosmology" / "Hz_cosmic_chronometers_independent.csv"
BAO_PATH = ROOT / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
BAO_COV_PATH = ROOT / "data" / "real" / "desi_dr2_bao_covariance.csv"
FS8_PATH = ROOT / "data" / "real" / "cosmology" / "fsigma8_growth_real.csv"
CMB_PATH = ROOT / "data" / "real" / "CMB_shift_real.json"

RESULTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

hz = read_csv(HZ_PATH)
bao = read_csv(BAO_PATH)
growth = read_csv(FS8_PATH)
cmb = load_json(CMB_PATH)

cov_rows = read_csv(BAO_COV_PATH)
bao_cov = []
for row in cov_rows:
    keys = sorted((key for key in row if key != ""), key=lambda value: int(value))
    bao_cov.append([float(row[key]) for key in keys])
bao_cov_inv = invert_matrix(bao_cov)

cmb_cov = [[float(x) for x in row] for row in cmb["covariance"]]
cmb_cov_inv = invert_matrix(cmb_cov)

seed = int(os.environ.get("RX_SEED", "1"))
maxiter = max(1, int(os.environ.get("RX_MULTIPROBE_MAXITER", "12")))
distance_steps = max(64, int(os.environ.get("RX_DISTANCE_STEPS", "256")))
cmb_steps = max(256, int(os.environ.get("RX_CMB_STEPS", "1024")))
growth_steps = max(64, int(os.environ.get("RX_GROWTH_STEPS", "256")))
growth_mode = os.environ.get("RX_GROWTH_MODE", "structure_d_proxy")
cmb_mode = os.environ.get("RX_CMB_MODE", "structure_d_rd")

def evaluate(model, vector):
    ol = omega_lambda(model, vector)
    p = unpack(model, vector)
    if ol <= 0.0 or p["H0"] <= 0.0 or p["Om"] <= 0.0 or p["Ob_h2"] <= 0.0 or p["sigma8"] <= 0.0:
        return float("inf"), None
    for z in (0.0, 2.5, float(cmb.get("z_CMB", 1089.92))):
        value = e2(model, z, vector)
        if value <= 0.0 or not math.isfinite(value):
            return float("inf"), None

    chi_hz = 0.0
    for row in hz:
        pred = hubble(model, float(row["z"]), vector)
        sig = float(row["sigma_H"])
        chi_hz += ((float(row["H_obs"]) - pred) / sig) ** 2

    cache = {}
    bao_pred = [
        bao_prediction(
            model,
            row,
            vector,
            steps=distance_steps,
            integration_mode="log1p",
            cache=cache,
        )
        for row in bao
    ]
    chi_bao = chi2_covariance(
        [float(row["value"]) for row in bao],
        bao_pred,
        bao_cov_inv,
    )

    chi_growth = 0.0
    for row in growth:
        pred = fsigma8_prediction(
            model,
            float(row["z"]),
            vector,
            mode=growth_mode,
            steps=growth_steps,
        )
        chi_growth += ((float(row["fs8"]) - pred) / float(row["sigma"])) ** 2

    cmb_pred = cmb_prediction(
        model,
        vector,
        z_cmb=float(cmb.get("z_CMB", 1089.92)),
        steps=cmb_steps,
        acoustic_mode=cmb_mode,
    )
    cmb_obs = [float(cmb["R_obs"]), float(cmb["la_obs"]), float(cmb["ob_h2_obs"])]
    chi_cmb = chi2_covariance(cmb_obs, cmb_pred, cmb_cov_inv)

    total = chi_hz + chi_bao + chi_growth + chi_cmb
    return total, {
        "Hz": chi_hz,
        "DESI_DR2_BAO": chi_bao,
        "fsigma8": chi_growth,
        "CMB_shift": chi_cmb,
        "CMB_prediction": cmb_pred,
    }

starts = {
    "LCDM": [67.4, 0.315, 0.02236, 0.811],
    "wCDM": [67.4, 0.315, -1.0, 0.02236, 0.811],
    "CPL": [67.4, 0.315, -1.0, 0.0, 0.02236, 0.811],
    "RLL": [67.4, 0.315, 0.0, 1.0, 0.3, 0.02236, 0.811],
}

fits = {}
for offset, model in enumerate(MODEL_ORDER):
    if model != "LCDM" and "LCDM" in fits:
        lcdm = fits["LCDM"]["x"]
        if model == "wCDM":
            starts[model] = [lcdm[0], lcdm[1], -1.0, lcdm[2], lcdm[3]]
        elif model == "CPL":
            starts[model] = [lcdm[0], lcdm[1], -1.0, 0.0, lcdm[2], lcdm[3]]
        elif model == "RLL":
            starts[model] = [lcdm[0], lcdm[1], 0.0, 1.0, 0.3, lcdm[2], lcdm[3]]
    fits[model] = bounded_coordinate_search(
        lambda values, model=model: evaluate(model, values)[0],
        starts[model],
        BOUNDS[model],
        maxiter=maxiter,
        seed=seed + offset,
        random_probes=1,
    )

n_hz = len(hz)
n_bao = len(bao)
n_growth = len(growth)
n_cmb = 3
n_obs = n_hz + n_bao + n_growth + n_cmb

rows = []
for model in MODEL_ORDER:
    chi2, components = evaluate(model, fits[model]["x"])
    k = len(PARAM_NAMES[model])
    aic = chi2 + 2.0 * k
    aicc = aic + (2.0 * k * (k + 1.0)) / (n_obs - k - 1.0)
    bic = chi2 + k * math.log(n_obs)
    row = {
        "model": model,
        "chi2": chi2,
        "AIC": aic,
        "AICc": aicc,
        "BIC": bic,
        "N": n_obs,
        "k": k,
        "dof": n_obs - k,
        "chi2_Hz": components["Hz"],
        "chi2_DESI_DR2_BAO": components["DESI_DR2_BAO"],
        "chi2_fsigma8": components["fsigma8"],
        "chi2_CMB_shift": components["CMB_shift"],
        "OL": omega_lambda(model, fits[model]["x"]),
        "optimizer_evaluations": fits[model]["evaluations"],
    }
    for name, value in zip(PARAM_NAMES[model], fits[model]["x"]):
        row[name] = value
    rows.append(row)

lcdm_x = fits["LCDM"]["x"]
nested_vectors = {
    "wCDM": [lcdm_x[0], lcdm_x[1], -1.0, lcdm_x[2], lcdm_x[3]],
    "CPL": [lcdm_x[0], lcdm_x[1], -1.0, 0.0, lcdm_x[2], lcdm_x[3]],
    "RLL": [lcdm_x[0], lcdm_x[1], 0.0, 1.0, 0.3, lcdm_x[2], lcdm_x[3]],
}
lcdm_nested_value = evaluate("LCDM", lcdm_x)[0]
nested = {}
for model, vector in nested_vectors.items():
    value = evaluate(model, vector)[0]
    nested[model] = {
        "lcdm_chi2": lcdm_nested_value,
        "nested_chi2": value,
        "abs_delta": abs(value - lcdm_nested_value),
        "pass": abs(value - lcdm_nested_value) <= 1.0e-8,
    }

input_hashes = {}
for path in (HZ_PATH, BAO_PATH, BAO_COV_PATH, FS8_PATH, CMB_PATH):
    input_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

try:
    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
except Exception:
    git_sha = "TOKEN_VAZIO"

payload = {
    "schema": "rll.rx.multiprobe.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "runtime": {
        "engine": "Rx",
        "third_party_python_dependencies": [],
        "training": False,
        "ai_runtime": False,
        "optimizer": "rx_bounded_coordinate_search_v1",
        "seed": seed,
        "maxiter": maxiter,
        "distance_steps": distance_steps,
        "cmb_steps": cmb_steps,
        "growth_steps": growth_steps,
    },
    "data_surface": {
        "Hz": n_hz,
        "DESI_DR2_BAO": n_bao,
        "fsigma8": n_growth,
        "CMB_compressed_parameters": n_cmb,
        "N": n_obs,
    },
    "semantics": {
        "growth_mode": growth_mode,
        "cmb_acoustic_mode": cmb_mode,
        "distance_integration": "log1p_simpson",
        "flat_closure": True,
    },
    "rows": rows,
    "nested_invariants": nested,
    "input_sha256": input_hashes,
    "git_commit": git_sha,
    "claim_allowed": False,
    "model_selection_claim_allowed": False,
    "known_semantic_divergence": {
        "growth": (
            "Structure-D current proxy uses sigma8*Omega_m(z)^0.55; "
            "freestanding canonical evaluator multiplies additionally by D(z)."
        ),
        "cmb_acoustic_scale": (
            "Structure-D current compressed CMB path uses r_d in l_A; "
            "freestanding canonical evaluator uses r_s(z_star)."
        ),
    },
}

dump_json(RESULTS / "multiprobe_rx.json", payload)
write_csv(RESULTS / "multiprobe_rx.csv", rows)

series = []
for row in rows:
    series.append({
        "label": row["model"],
        "points": [
            (0.0, row["chi2_Hz"]),
            (1.0, row["chi2_DESI_DR2_BAO"]),
            (2.0, row["chi2_fsigma8"]),
            (3.0, row["chi2_CMB_shift"]),
        ],
    })
write_svg_chart(
    FIGS / "multiprobe_components_rx.svg",
    "Rx multiprobe component chi2: Hz / BAO / growth / CMB",
    series,
)

report = [
    "# RLL Rx multiprobe",
    "",
    "Runtime: Python stdlib + project-local Rx only.",
    "Training: false. AI runtime: false.",
    "Claim allowed: false.",
    "",
    "## Data surface",
    "",
    "- H(z): %d" % n_hz,
    "- DESI DR2 BAO: %d" % n_bao,
    "- fσ8: %d" % n_growth,
    "- CMB compressed parameters: %d" % n_cmb,
    "- Total N: %d" % n_obs,
    "",
    "## Results",
    "",
    "| model | chi2 | AIC | AICc | BIC |",
    "|---|---:|---:|---:|---:|",
]
for row in rows:
    report.append(
        "| %s | %.6f | %.6f | %.6f | %.6f |"
        % (row["model"], row["chi2"], row["AIC"], row["AICc"], row["BIC"])
    )
report += [
    "",
    "## Nested invariants",
    "",
]
for model, state in nested.items():
    report.append(
        "- %s -> LCDM-like: %s (abs delta chi2 %.3e)"
        % (model, "PASS" if state["pass"] else "FAIL", state["abs_delta"])
    )
report += [
    "",
    "## Semantic divergence gate",
    "",
    "- Growth: Structure-D proxy and freestanding D(z) route are intentionally distinguished.",
    "- CMB l_A: Structure-D r_d route and freestanding r_s(z_star) route are intentionally distinguished.",
    "- These differences are not hidden under one parity label.",
]
(RESULTS / "MULTIPROBE_RX.md").write_text("\n".join(report) + "\n", encoding="utf-8")

print("=== RLL Rx multiprobe ===")
print("training=False ai_runtime=False third_party_python_dependencies=0")
print("N=", n_obs, "Hz=", n_hz, "BAO=", n_bao, "fsigma8=", n_growth, "CMB=", n_cmb)
for row in rows:
    print(
        row["model"],
        "chi2=%.6f" % row["chi2"],
        "AIC=%.6f" % row["AIC"],
        "BIC=%.6f" % row["BIC"],
    )
for model, state in nested.items():
    print("nested", model, "PASS" if state["pass"] else "FAIL", "delta=%.3e" % state["abs_delta"])
print("claim_allowed=False")
print("wrote", (RESULTS / "multiprobe_rx.json").relative_to(ROOT))
