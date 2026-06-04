#!/usr/bin/env python3
"""Generate publication figures from the validation artifacts.

Uses matplotlib (one pip install in the Action). If matplotlib is absent the
script degrades to a pure-stdlib SVG fallback so the pipeline never hard-fails.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FETCHED = HERE / "fetched"
RESULTS = HERE / "results"
FIGS = RESULTS / "figures"

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

C_KM_S = 299792.458
RD_MPC = 147.09


def load(path: Path) -> dict:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _model_curves():
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("cv", HERE / "compute_validation.py")
    cv = importlib.util.module_from_spec(spec)
    sys.modules["cv"] = cv
    spec.loader.exec_module(cv)
    lcdm = cv.Cosmo(name="LCDM", H0=67.4, Om=0.315, Or=9.2e-5, k_params=3)
    rll = cv.Cosmo(name="RLL", H0=67.4, Om=0.315, Or=9.2e-5, Os=0.02, zt=1.0, wt=0.3, k_params=5)
    zs = [i * 2.4 / 200 for i in range(1, 201)]
    return cv, lcdm, rll, zs


def fig_hubble():
    cv, lcdm, rll, zs = _model_curves()
    hz = load(FETCHED / "hz_cosmic_chronometers.yml")["points"]
    plt.figure(figsize=(8, 5))
    plt.errorbar([p["z"] for p in hz], [p["H"] for p in hz], yerr=[p["sigma"] for p in hz],
                 fmt="o", ms=4, capsize=2, color="#222", label="H(z) cosmic chronometers", zorder=3)
    plt.plot(zs, [cv.H(lcdm, z) for z in zs], "-", color="#1f6feb", lw=2, label="LCDM")
    plt.plot(zs, [cv.H(rll, z) for z in zs], "--", color="#d1242f", lw=2, label="RLL")
    plt.xlabel("redshift z"); plt.ylabel("H(z) [km/s/Mpc]")
    plt.title("Expansion rate: models vs real H(z)")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(FIGS / "hubble_diagram.png", dpi=140); plt.close()


def fig_bao():
    cv, lcdm, rll, zs = _model_curves()
    bao = load(FETCHED / "desi_dr2_bao.yml")["points"]
    plt.figure(figsize=(8, 5))
    for obs, mk in [("DM_over_rd", "o"), ("DH_over_rd", "s"), ("DV_over_rd", "^")]:
        pts = [p for p in bao if p["observable"] == obs]
        if pts:
            plt.errorbar([p["z_eff"] for p in pts], [p["value"] for p in pts],
                         yerr=[p["sigma"] for p in pts], fmt=mk, ms=6, capsize=2,
                         label=f"DESI {obs}", zorder=3)
    plt.plot(zs, [cv.DM_over_rd(lcdm, z) for z in zs], "-", color="#1f6feb", lw=1.5, alpha=0.8)
    plt.plot(zs, [cv.DH_over_rd(lcdm, z) for z in zs], "-", color="#1f6feb", lw=1.5, alpha=0.8)
    plt.plot(zs, [cv.DM_over_rd(rll, z) for z in zs], "--", color="#d1242f", lw=1.5, alpha=0.8)
    plt.plot(zs, [cv.DH_over_rd(rll, z) for z in zs], "--", color="#d1242f", lw=1.5, alpha=0.8)
    plt.xlabel("redshift z"); plt.ylabel("distance / r_d")
    plt.title("BAO distances: DESI DR2 vs models (solid=LCDM, dashed=RLL)")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(FIGS / "bao_distances.png", dpi=140); plt.close()


def fig_pulls():
    summary = load(RESULTS / "validation_summary.json")["summary"]
    import csv
    rows = list(csv.DictReader((RESULTS / "per_point_predictions.csv").open(encoding="utf-8")))
    plt.figure(figsize=(8, 5))
    for m, color in [("LCDM", "#1f6feb"), ("RLL", "#d1242f")]:
        zs = [float(r["z"]) for r in rows]
        pulls = [float(r[f"pull_{m}"]) for r in rows]
        plt.scatter(zs, pulls, s=28, color=color, alpha=0.7, label=m)
    for y in (-1, 1):
        plt.axhline(y, color="#888", lw=0.8, ls=":")
    plt.axhline(0, color="#000", lw=1)
    plt.xlabel("redshift z"); plt.ylabel("pull = (model - obs)/sigma")
    plt.title("Residual pulls per data point")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(FIGS / "residual_pulls.png", dpi=140); plt.close()


def fig_bars():
    summary = load(RESULTS / "validation_summary.json")["summary"]
    models = list(summary)
    metrics = ["chi2_total", "aic", "bic"]
    x = range(len(metrics))
    w = 0.38
    plt.figure(figsize=(8, 5))
    for i, m in enumerate(models):
        vals = [summary[m][k] for k in metrics]
        plt.bar([xi + (i - 0.5) * w for xi in x], vals, width=w, label=m,
                color=["#1f6feb", "#d1242f"][i % 2])
    plt.xticks(list(x), [k.upper() for k in metrics])
    plt.ylabel("value (lower = better)")
    plt.title("Model comparison: chi2 / AIC / BIC")
    plt.legend(); plt.grid(alpha=0.3, axis="y"); plt.tight_layout()
    plt.savefig(FIGS / "model_comparison_bars.png", dpi=140); plt.close()


def svg_fallback():
    summary = load(RESULTS / "validation_summary.json")["summary"]
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360">',
             '<rect width="640" height="360" fill="white"/>',
             '<text x="20" y="30" font-size="18" font-family="monospace">RLL vs LCDM (SVG fallback)</text>']
    y = 70
    for m, s in summary.items():
        lines.append(f'<text x="20" y="{y}" font-size="14" font-family="monospace">'
                     f'{m}: chi2={s["chi2_total"]} AIC={s["aic"]} BIC={s["bic"]}</text>')
        y += 30
    lines.append("</svg>")
    (FIGS / "model_comparison.svg").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    FIGS.mkdir(parents=True, exist_ok=True)
    if HAVE_MPL:
        fig_hubble(); fig_bao(); fig_pulls(); fig_bars()
        print(f"figures (PNG) -> {FIGS.relative_to(HERE)}/")
    else:
        svg_fallback()
        print(f"matplotlib absent; SVG fallback -> {FIGS.relative_to(HERE)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
