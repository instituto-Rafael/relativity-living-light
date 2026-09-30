#!/usr/bin/env python3
"""Validate the dependency-free RLL real-run plot migration.

Stdlib/project-local only. Uses temporary fixture tables; no scientific claim.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"scripts/generate_rll_plots.py"

def imported_roots(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    roots=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots

def load_target():
    spec=importlib.util.spec_from_file_location("rll_generate_plots_gate",TARGET)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

roots=imported_roots(TARGET)
checks={
    "no_pandas_import":"pandas" not in roots,
    "no_matplotlib_import":"matplotlib" not in roots,
    "uses_rx":"rx" in roots,
}

module=load_target()
previous=os.getcwd()
try:
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        base=Path("artifacts/rll-real-run")
        tables=base/"tables"; raw=base/"raw"
        tables.mkdir(parents=True); raw.mkdir(parents=True)
        (tables/"Hz_processed.csv").write_text("z,H_z\n0.1,70\n0.2,75\n",encoding="utf-8")
        (tables/"BAO_processed.csv").write_text("z,bao_obs,bao_rll\n0.3,8.0,7.9\n0.7,17.0,16.8\n",encoding="utf-8")
        (tables/"model_comparison.csv").write_text("model,chi2\nLCDM,40.0\nRLL,42.0\n",encoding="utf-8")
        (tables/"rll_components.csv").write_text("a,E2_matter,E2_de\n0.5,2.0,0.7\n1.0,0.3,0.7\n",encoding="utf-8")
        (raw/"SOURCES.json").write_text(json.dumps([
            {"status":"materialized"},
            {"status":"materialized"},
            {"status":"TOKEN_VAZIO"},
        ])+"\n",encoding="utf-8")

        rc=module.main()
        checks["main_return_zero"]=rc==0
        expected=[
            "Hz_curve.svg",
            "BAO_comparison.svg",
            "chi2_barplot.svg",
            "rll_components.svg",
            "data_sources_status.svg",
            "plots_manifest.json",
        ]
        plots=base/"plots"
        checks["all_expected_outputs"]=all((plots/name).is_file() for name in expected)
        checks["no_new_png_outputs"]=not list(plots.glob("*.png"))
        manifest=json.loads((plots/"plots_manifest.json").read_text(encoding="utf-8"))
        checks["manifest_schema"]=manifest.get("schema")=="rll.real_run.plots.rx_svg.v1"
        checks["manifest_zero_third_party"]=manifest.get("third_party_python_dependencies")==[]
        checks["manifest_five_legacy_mappings"]=len(manifest.get("legacy_png_to_svg",{}))==5
        checks["claim_closed"]=manifest.get("claim_allowed") is False
finally:
    os.chdir(previous)

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.rx.plot_migration_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "third_party_python_dependencies":[],
    "scientific_semantics_changed":False,
    "claim_allowed":False,
    "boundary":"Fixture validates presentation migration only; it does not validate source data, models, or scientific conclusions."
}
out=ROOT/"results/rx_plot_migration_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
