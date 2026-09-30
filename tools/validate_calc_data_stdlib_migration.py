#!/usr/bin/env python3
"""Validate stdlib migration of scripts/calc_data.py.

Uses local fixtures plus a committed real-data smoke input. No external network.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import math
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"scripts/calc_data.py"

tree=ast.parse(TARGET.read_text(encoding="utf-8"))
imports=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Import):
        imports.update(alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node,ast.ImportFrom) and node.module:
        imports.add(node.module.split(".")[0])

module_name="rll_calc_data_stdlib_gate_target"
spec=importlib.util.spec_from_file_location(module_name,TARGET)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

checks={
    "no_numpy_import":"numpy" not in imports,
    "no_pandas_import":"pandas" not in imports,
}

with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)
    csv_path=base/"fixture.csv"
    csv_path.write_text(
        "x,y,label\n1,10,a\n2,20,b\n3,30,c\n",
        encoding="utf-8",
    )
    csv_stats=mod.summarize(mod.load(str(csv_path)))
    checks["csv_counts"]=csv_stats["n_records"]==3 and csv_stats["n_columns"]==3
    checks["csv_numeric_columns"]=csv_stats["numeric_columns"]==["x","y"]
    checks["csv_mean"]=abs(csv_stats["columns"]["x"]["mean"]-2.0)<1e-12
    checks["csv_median"]=abs(csv_stats["columns"]["y"]["median"]-20.0)<1e-12
    checks["csv_sample_std_ddof1"]=abs(csv_stats["columns"]["x"]["std"]-1.0)<1e-12
    checks["csv_minmax"]=(
        csv_stats["columns"]["y"]["min"]==10.0
        and csv_stats["columns"]["y"]["max"]==30.0
    )
    checks["csv_samples_preserved"]=(
        csv_stats["sample_head"][0]=={"x":1,"y":10,"label":"a"}
        and csv_stats["sample_tail"][-1]=={"x":3,"y":30,"label":"c"}
    )

    json_path=base/"fixture.json"
    json_path.write_text(
        json.dumps({"records":[{"a":1.0,"name":"x"},{"a":3.0,"name":"y"}]})+"\n",
        encoding="utf-8",
    )
    json_stats=mod.summarize(mod.load(str(json_path)))
    checks["json_records_shape"]=json_stats["n_records"]==2
    checks["json_numeric_detection"]=json_stats["numeric_columns"]==["a"]
    checks["json_stats"]=(
        abs(json_stats["columns"]["a"]["mean"]-2.0)<1e-12
        and abs(json_stats["columns"]["a"]["std"]-math.sqrt(2.0))<1e-12
    )

real_path=ROOT/"data/real/Hz_data_real.csv"
if real_path.exists():
    real_stats=mod.summarize(mod.load(str(real_path)))
    checks["committed_real_smoke"]=(
        real_stats["n_records"]>0
        and "z" in real_stats["numeric_columns"]
        and "H_obs" in real_stats["numeric_columns"]
        and "sigma_H" in real_stats["numeric_columns"]
    )
else:
    checks["committed_real_smoke"]=False

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.calc_data.stdlib_migration_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "third_party_python_dependencies":[],
    "network_requests_performed":0,
    "claim_allowed":False,
    "boundary":"This gate preserves the audit-statistics contract for controlled fixtures and a committed-data smoke input. It does not validate cosmology or replace domain-specific uncertainty analysis."
}
out=ROOT/"results/calc_data_stdlib_migration.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
