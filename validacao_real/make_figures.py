#!/usr/bin/env python3
"""Generate legacy validation figures with project-local Rx SVG output.

No matplotlib/PyYAML/third-party Python packages. Scientific predictions are
still produced by compute_validation.py; this file changes presentation only.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from rx.kernel import write_svg_chart

FETCHED=HERE/"fetched"
RESULTS=HERE/"results"
FIGS=RESULTS/"figures"

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def model_module():
    spec=importlib.util.spec_from_file_location("rll_legacy_compute_validation",HERE/"compute_validation.py")
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

def main():
    FIGS.mkdir(parents=True,exist_ok=True)
    cv=model_module()
    lcdm=cv.Cosmo(name="LCDM",H0=67.4,Om=0.315,Or=9.2e-5,k_params=3)
    rll=cv.Cosmo(name="RLL",H0=67.4,Om=0.315,Or=9.2e-5,Os=0.02,zt=1.0,wt=0.3,k_params=5)
    zs=[i*2.4/200.0 for i in range(1,201)]

    hz=load(FETCHED/"hz_cosmic_chronometers.json")["points"]
    write_svg_chart(
        FIGS/"hubble_diagram.svg",
        "Expansion rate: models vs real H(z)",
        [
            {"label":"LCDM","points":[(z,cv.H(lcdm,z)) for z in zs]},
            {"label":"RLL","points":[(z,cv.H(rll,z)) for z in zs]},
            {"label":"H(z) observations","points":[(float(p["z"]),float(p["H"])) for p in hz]},
        ],
    )

    bao=load(FETCHED/"desi_dr2_bao.json")["points"]
    bao_series=[]
    for obs in ("DM_over_rd","DH_over_rd","DV_over_rd"):
        pts=[p for p in bao if p["observable"]==obs]
        if pts:
            bao_series.append({"label":"DESI "+obs,"points":[(float(p["z_eff"]),float(p["value"])) for p in pts]})
    bao_series.extend([
        {"label":"LCDM DM/rd","points":[(z,cv.DM_over_rd(lcdm,z)) for z in zs]},
        {"label":"LCDM DH/rd","points":[(z,cv.DH_over_rd(lcdm,z)) for z in zs]},
        {"label":"RLL DM/rd","points":[(z,cv.DM_over_rd(rll,z)) for z in zs]},
        {"label":"RLL DH/rd","points":[(z,cv.DH_over_rd(rll,z)) for z in zs]},
    ])
    write_svg_chart(FIGS/"bao_distances.svg","BAO distances: DESI DR2 vs models",bao_series)

    rows=list(csv.DictReader((RESULTS/"per_point_predictions.csv").open(encoding="utf-8")))
    pull_series=[]
    for model in ("LCDM","RLL"):
        pull_series.append({
            "label":model,
            "points":[(float(row["z"]),float(row["pull_"+model])) for row in rows],
        })
    write_svg_chart(FIGS/"residual_pulls.svg","Residual pulls per data point",pull_series)

    summary=load(RESULTS/"validation_summary.json")["summary"]
    metric_series=[]
    for model,data in summary.items():
        metric_series.append({
            "label":model,
            "points":[(0.0,float(data["chi2_total"])),(1.0,float(data["aic"])),(2.0,float(data["bic"]))],
        })
    write_svg_chart(FIGS/"model_comparison.svg","Model comparison: chi2 / AIC / BIC",metric_series)

    print("figures (Rx SVG, zero third-party) -> "+str(FIGS.relative_to(HERE))+"/")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
