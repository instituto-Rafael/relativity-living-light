#!/usr/bin/env python3
"""Rx validation pipeline: stdlib-only H(z)+DESI DR2 BAO RLL/LCDM fit.

Run from repository root:
    python3 -m validacao_real.run_rx_pipeline

No third-party Python packages are required.
"""

from __future__ import annotations

import hashlib
import math
import os
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from rx import (
    bounded_coordinate_search,
    dump_json,
    invert_matrix,
    load_json,
    quad_form,
    read_csv,
    simpson,
    write_csv,
    write_svg_chart,
)

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "validacao_real"
FETCHED = HERE / "fetched_rx"
RESULTS = HERE / "results_rx"
FIGS = RESULTS / "figures"
SOURCES = HERE / "sources_rx.json"
DESI_COV = ROOT / "data" / "real" / "desi_dr2_bao_covariance.csv"

C_KMS = 299792.458
OMEGA_R = 9.0e-5
CLAIM_ALLOWED = False

FETCHED.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

source_registry = load_json(SOURCES)
manifest = {
    "schema": "rll.validacao_real.rx.manifest.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "claim_boundary": source_registry["claim_boundary"],
    "sources": [],
}

for source in source_registry["sources"]:
    portal = source.get("portal", "")
    reachable = False
    remote_bytes = 0
    remote_error = "TOKEN_VAZIO"
    if portal:
        try:
            req = urllib.request.Request(
                portal,
                headers={"User-Agent": "RLL-Rx/1.0"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                chunk = response.read(128)
                remote_bytes = len(chunk)
                reachable = True
                remote_error = ""
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            remote_error = exc.__class__.__name__

    fallback = HERE / source["embedded_fallback"]
    payload = load_json(fallback)
    out_path = FETCHED / (source["id"] + ".json")
    dump_json(out_path, payload)
    manifest["sources"].append(
        {
            "source_id": source["id"],
            "portal": portal,
            "remote_reachable": reachable,
            "remote_probe_bytes": remote_bytes,
            "remote_error": remote_error or "NONE",
            "used": "committed_rx_json_fallback",
            "fallback_state": "committed_local_payload_not_fresh_remote_download",
            "fallback_path": str(fallback.relative_to(ROOT)),
            "n_points": len(payload.get("points", [])),
            "claim_boundary": source_registry["claim_boundary"],
        }
    )

dump_json(FETCHED / "manifest.json", manifest)

hz = load_json(FETCHED / "hz_cosmic_chronometers.json")["points"]
bao = load_json(FETCHED / "desi_dr2_bao.json")["points"]

cov_rows = read_csv(DESI_COV)
cov = []
for row in cov_rows:
    numeric_keys = sorted((k for k in row if k != ""), key=lambda x: int(x))
    cov.append([float(row[k]) for k in numeric_keys])
if len(cov) != len(bao) or any(len(row) != len(bao) for row in cov):
    raise SystemExit("Rx covariance shape mismatch")
cov_inv = invert_matrix(cov)

simpson_steps = max(32, int(os.environ.get("RX_SIMPSON_STEPS", "128")))
maxiter = max(1, int(os.environ.get("RX_MAXITER", "16")))
seed = int(os.environ.get("RX_SEED", "1"))

def evaluate(model, vector):
    if model == "LCDM":
        h0, om, ob_h2 = vector
        os0, zt, wt = 0.0, 1.0, 0.3
    else:
        h0, om, os0, zt, wt, ob_h2 = vector

    ol = 1.0 - OMEGA_R - om - os0
    if h0 <= 0.0 or om <= 0.0 or ol <= 0.0 or ob_h2 <= 0.0 or wt <= 0.0:
        return float("inf"), None

    om_h2 = om * (h0 / 100.0) ** 2
    if om_h2 <= 0.0:
        return float("inf"), None
    rd = 147.78 * (om_h2 / 0.1432) ** (-0.255) * (ob_h2 / 0.02236) ** (-0.134)

    def e2(z):
        zp1 = 1.0 + z
        base = om * zp1**3 + OMEGA_R * zp1**4 + ol
        if model == "RLL" and os0 != 0.0:
            arg = max(-500.0, min(500.0, (z - zt) / wt))
            fz = 1.0 / (1.0 + math.exp(arg))
            base += os0 * (fz + (1.0 - fz) * zp1**3)
        return base

    chi_hz = 0.0
    for point in hz:
        value = e2(float(point["z"]))
        if value <= 0.0:
            return float("inf"), None
        pred = h0 * math.sqrt(value)
        chi_hz += ((pred - float(point["H"])) / float(point["sigma"])) ** 2

    distance_cache = {}
    residual = []
    predictions = []
    for point in bao:
        z = float(point["z_eff"])
        if z not in distance_cache:
            dc = (C_KMS / h0) * simpson(
                lambda zz: 1.0 / math.sqrt(max(e2(zz), 1.0e-300)),
                0.0,
                z,
                simpson_steps,
            )
            distance_cache[z] = dc
        dc = distance_cache[z]
        hz_model = h0 * math.sqrt(max(e2(z), 1.0e-300))
        observable = point["observable"]
        if observable == "DM_over_rd":
            pred = dc / rd
        elif observable == "DH_over_rd":
            pred = (C_KMS / hz_model) / rd
        elif observable == "DV_over_rd":
            pred = (z * C_KMS * dc * dc / hz_model) ** (1.0 / 3.0) / rd
        else:
            return float("inf"), None
        residual.append(float(point["value"]) - pred)
        predictions.append(pred)

    chi_bao = quad_form(residual, cov_inv)
    total = chi_hz + chi_bao
    return total, {
        "Hz": chi_hz,
        "DESI_DR2_BAO": chi_bao,
        "rd_mpc": rd,
        "OL": ol,
        "bao_predictions": predictions,
    }

lcdm_bounds = [(55.0, 85.0), (0.10, 0.60), (0.018, 0.026)]
lcdm_start = [67.4, 0.315, 0.02236]
lcdm_fit = bounded_coordinate_search(
    lambda x: evaluate("LCDM", x)[0],
    lcdm_start,
    lcdm_bounds,
    maxiter=maxiter,
    seed=seed,
    random_probes=2,
)

rll_bounds = [
    (55.0, 85.0),
    (0.10, 0.60),
    (0.0, 0.25),
    (0.1, 10.0),
    (0.05, 2.0),
    (0.018, 0.026),
]
rll_start = [
    lcdm_fit["x"][0],
    lcdm_fit["x"][1],
    0.0,
    1.0,
    0.3,
    lcdm_fit["x"][2],
]
rll_fit = bounded_coordinate_search(
    lambda x: evaluate("RLL", x)[0],
    rll_start,
    rll_bounds,
    maxiter=maxiter,
    seed=seed + 1,
    random_probes=2,
)

fits = {"LCDM": lcdm_fit, "RLL": rll_fit}
param_names = {
    "LCDM": ["H0", "Om", "Ob_h2"],
    "RLL": ["H0", "Om", "Os0", "zt", "wt", "Ob_h2"],
}
rows = []
n_obs = len(hz) + len(bao)

for model in ("LCDM", "RLL"):
    chi2, detail = evaluate(model, fits[model]["x"])
    k = len(param_names[model])
    aic = chi2 + 2.0 * k
    aicc = aic + (2.0 * k * (k + 1.0)) / (n_obs - k - 1.0)
    bic = chi2 + k * math.log(n_obs)
    row = {
        "model": model,
        "chi2": chi2,
        "chi2_Hz": detail["Hz"],
        "chi2_DESI_DR2_BAO": detail["DESI_DR2_BAO"],
        "N": n_obs,
        "k": k,
        "dof": n_obs - k,
        "AIC": aic,
        "AICc": aicc,
        "BIC": bic,
        "rd_mpc": detail["rd_mpc"],
        "OL": detail["OL"],
        "optimizer_evaluations": fits[model]["evaluations"],
    }
    for name, value in zip(param_names[model], fits[model]["x"]):
        row[name] = value
    rows.append(row)

nested_limit_pass = rows[1]["chi2"] <= rows[0]["chi2"] + 1.0e-9

hashes = {}
for path in (
    SOURCES,
    HERE / "data" / "desi_dr2_bao_rx.json",
    HERE / "data" / "hz_cosmic_chronometers_rx.json",
    DESI_COV,
):
    hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

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
    "schema": "rll.validacao_real.rx.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "runtime": {
        "engine": "Rx",
        "third_party_python_dependencies": [],
        "python_stdlib_only": True,
        "optimizer": "rx_bounded_coordinate_search_v1",
        "seed": seed,
        "maxiter": maxiter,
        "simpson_steps": simpson_steps,
    },
    "datasets": {
        "Hz_points": len(hz),
        "DESI_DR2_BAO_points": len(bao),
        "N": n_obs,
        "DESI_covariance": str(DESI_COV.relative_to(ROOT)),
    },
    "rows": rows,
    "nested_limit": {
        "relation": "RLL(Os0=0) -> LCDM-like flat background",
        "pass": nested_limit_pass,
    },
    "input_sha256": hashes,
    "git_commit": git_sha,
    "claim_allowed": CLAIM_ALLOWED,
    "model_selection_claim_allowed": False,
    "claim_boundary": [
        source_registry["claim_boundary"],
        "Rx removes third-party runtime dependencies; that engineering property is not scientific evidence for RLL.",
        "The fit is bounded coordinate search, not a posterior or proof of global convergence.",
        "This Rx route covers H(z)+DESI DR2 BAO with committed DESI covariance; broader multiprobe gates remain separate.",
    ],
}

dump_json(RESULTS / "validation_summary_rx.json", payload)
write_csv(RESULTS / "model_comparison_rx.csv", rows)

curve_z = [i * 2.4 / 120.0 for i in range(121)]
curve_series = []
for model in ("LCDM", "RLL"):
    x = fits[model]["x"]
    points = []
    for z in curve_z:
        if model == "LCDM":
            h0, om, ob_h2 = x
            os0, zt, wt = 0.0, 1.0, 0.3
        else:
            h0, om, os0, zt, wt, ob_h2 = x
        ol = 1.0 - OMEGA_R - om - os0
        zp1 = 1.0 + z
        e2v = om * zp1**3 + OMEGA_R * zp1**4 + ol
        if model == "RLL" and os0 != 0.0:
            arg = max(-500.0, min(500.0, (z - zt) / wt))
            fz = 1.0 / (1.0 + math.exp(arg))
            e2v += os0 * (fz + (1.0 - fz) * zp1**3)
        points.append((z, h0 * math.sqrt(max(e2v, 1.0e-300))))
    curve_series.append({"label": model, "points": points})

curve_series.append(
    {
        "label": "H(z) observations",
        "points": [(float(p["z"]), float(p["H"])) for p in hz],
    }
)
write_svg_chart(FIGS / "hubble_rx.svg", "Rx: H(z) real-data fit", curve_series)

metric_series = []
for row in rows:
    metric_series.append(
        {
            "label": row["model"],
            "points": [
                (0.0, row["chi2"]),
                (1.0, row["AIC"]),
                (2.0, row["BIC"]),
            ],
        }
    )
write_svg_chart(FIGS / "model_comparison_rx.svg", "Rx: chi2 / AIC / BIC", metric_series)

report = [
    "# RLL Rx — validação real stdlib-only",
    "",
    "Gerado: " + payload["generated_utc"],
    "",
    "**Runtime:** Rx / Python standard library only.",
    "**Dependências Python de terceiros:** 0.",
    "**Claim allowed:** false.",
    "",
    "| modelo | chi2 | chi2/dof | AIC | AICc | BIC |",
    "|---|---:|---:|---:|---:|---:|",
]
for row in rows:
    report.append(
        "| %s | %.6f | %.6f | %.6f | %.6f | %.6f |"
        % (
            row["model"],
            row["chi2"],
            row["chi2"] / max(row["dof"], 1),
            row["AIC"],
            row["AICc"],
            row["BIC"],
        )
    )
report += [
    "",
    "Nested limit RLL(Os0=0) -> LCDM-like: **%s**."
    % ("PASS" if nested_limit_pass else "FAIL"),
    "",
    "## Boundary",
    "",
    "- Zero dependências externas é uma propriedade de engenharia/reprodutibilidade.",
    "- Não promove confirmação física, superioridade estatística ou posterior.",
    "- Escopo deste gate: H(z) + DESI DR2 BAO com covariância DESI commitada.",
    "",
    "## Artefatos",
    "",
    "- results_rx/validation_summary_rx.json",
    "- results_rx/model_comparison_rx.csv",
    "- results_rx/figures/hubble_rx.svg",
    "- results_rx/figures/model_comparison_rx.svg",
]
(RESULTS / "RELATORIO_VALIDACAO_RX.md").write_text(
    "\n".join(report) + "\n",
    encoding="utf-8",
)

print("=== RLL Rx — stdlib-only real-data validation ===")
print("third_party_python_dependencies=0")
for row in rows:
    print(
        row["model"],
        "chi2=%.6f" % row["chi2"],
        "AIC=%.6f" % row["AIC"],
        "BIC=%.6f" % row["BIC"],
    )
print("nested_limit_pass=", nested_limit_pass)
print("claim_allowed=False")
print("artifacts=", RESULTS.relative_to(ROOT))
