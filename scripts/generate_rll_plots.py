#!/usr/bin/env python3
"""Generate RLL real-run plots with project-local Rx SVG primitives.

Zero third-party Python dependencies. This script consumes already-produced
tables; it does not change scientific calculations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx import read_csv, write_svg_bars, write_svg_chart, write_svg_message


def _points(rows, x_key, y_key):
    return [(float(row[x_key]), float(row[y_key])) for row in rows]


def main():
    root = Path("artifacts/rll-real-run")
    plots = root / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    tables = root / "tables"

    hz = tables / "Hz_processed.csv"
    bao = tables / "BAO_processed.csv"
    mc = tables / "model_comparison.csv"
    comp = tables / "rll_components.csv"
    src = root / "raw" / "SOURCES.json"

    generated = {}

    if hz.exists():
        rows = read_csv(hz)
        write_svg_chart(
            plots / "Hz_curve.svg",
            "Hz curve",
            [{"label": "H(z)", "points": _points(rows, "z", "H_z")}],
        )
        generated["Hz_curve.png"] = "Hz_curve.svg"
    else:
        write_svg_message(plots / "Hz_curve.svg", "Hz curve", "pending_data")
        generated["Hz_curve.png"] = "Hz_curve.svg"

    if bao.exists():
        rows = read_csv(bao)
        write_svg_chart(
            plots / "BAO_comparison.svg",
            "BAO comparison",
            [
                {"label": "obs", "points": _points(rows, "z", "bao_obs")},
                {"label": "rll", "points": _points(rows, "z", "bao_rll")},
            ],
        )
        generated["BAO_comparison.png"] = "BAO_comparison.svg"

    if mc.exists():
        rows = read_csv(mc)
        write_svg_bars(
            plots / "chi2_barplot.svg",
            "chi2 by model",
            [row["model"] for row in rows],
            [float(row["chi2"]) for row in rows],
        )
        generated["chi2_barplot.png"] = "chi2_barplot.svg"

    if comp.exists():
        rows = read_csv(comp)
        write_svg_chart(
            plots / "rll_components.svg",
            "RLL components",
            [
                {"label": "matter", "points": _points(rows, "a", "E2_matter")},
                {"label": "de", "points": _points(rows, "a", "E2_de")},
            ],
        )
        generated["rll_components.png"] = "rll_components.svg"

    if src.exists():
        sources = json.loads(src.read_text(encoding="utf-8"))
        status_counts = {}
        for item in sources:
            key = str(item.get("status", "TOKEN_VAZIO"))
            status_counts[key] = status_counts.get(key, 0) + 1
        labels = sorted(status_counts)
        write_svg_bars(
            plots / "data_sources_status.svg",
            "Data source status",
            labels,
            [status_counts[label] for label in labels],
        )
        generated["data_sources_status.png"] = "data_sources_status.svg"

    manifest = {
        "schema": "rll.real_run.plots.rx_svg.v1",
        "renderer": "rx.kernel",
        "third_party_python_dependencies": [],
        "scientific_calculation_performed": False,
        "legacy_png_to_svg": generated,
        "claim_allowed": False,
        "boundary": (
            "Presentation migration only. SVG generation does not change source "
            "tables, model calculations, evidence state, or scientific claims."
        ),
    }
    (plots / "plots_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("RLL_PLOTS_RX_SVG=PASS")
    print("generated=", len(generated))
    print("manifest=", plots / "plots_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
