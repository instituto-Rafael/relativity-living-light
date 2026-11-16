#!/usr/bin/env python3
"""Validate stdlib migration of the deterministic validation route.

The Bayesian/emcee route is intentionally preserved behind
validation/load_data_numpy_legacy.py and is not declared migrated here.
"""
from __future__ import annotations

import ast
import importlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

TARGETS=[
    ROOT/"validation/load_data.py",
    ROOT/"validation/run_lcdm.py",
    ROOT/"validation/run_rll.py",
    ROOT/"validation/compare_models.py",
]

stdlib=set(getattr(sys,"stdlib_module_names",()))
stdlib.add("__future__")
local_roots={"validation"}

def external_imports(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    roots=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return sorted(root for root in roots if root not in stdlib and root not in local_roots)

checks={}
details={}
for path in TARGETS:
    external=external_imports(path)
    checks[path.name+"_zero_third_party"]=not external
    details[path.name+"_external"]=external

load_data=importlib.import_module("validation.load_data")
run_lcdm=importlib.import_module("validation.run_lcdm")
run_rll=importlib.import_module("validation.run_rll")
compare_models=importlib.import_module("validation.compare_models")

z,y,yerr=load_data.load_real_data(ROOT/"data/real/Hz_data_real.csv")
checks["canonical_vectors_nonempty"]=len(z)>0 and len(z)==len(y)==len(yerr)
checks["canonical_values_finite"]=all(
    math.isfinite(value)
    for vector in (z,y,yerr)
    for value in vector
)
checks["canonical_sigma_positive"]=all(value>0.0 for value in yerr)

lcdm=run_lcdm.lcdm(z)
rll=run_rll.rll(z)
reference_lcdm=[
    70.0*math.sqrt(0.3*(1.0+value)**3+0.7)
    for value in z
]
reference_rll=[
    70.0*math.sqrt(0.3*(1.0+value)**3+0.7)+0.1*math.log(1.0+value)
    for value in z
]
checks["lcdm_formula_vector_parity"]=max(abs(a-b) for a,b in zip(lcdm,reference_lcdm))<=1e-12
checks["rll_formula_vector_parity"]=max(abs(a-b) for a,b in zip(rll,reference_rll))<=1e-12

comparison=compare_models.compare(y,yerr,lcdm,rll)
ref_lcdm=sum(((pred-obs)/(sig+1e-8))**2 for pred,obs,sig in zip(lcdm,y,yerr))
ref_rll=sum(((pred-obs)/(sig+1e-8))**2 for pred,obs,sig in zip(rll,y,yerr))
checks["chi2_scalar_parity"]=(
    abs(comparison["chi2_lcdm"]-ref_lcdm)<=1e-12
    and abs(comparison["chi2_rll"]-ref_rll)<=1e-12
)

for name in ("bayes_rll.py","bayes_compare.py"):
    text=(ROOT/"validation"/name).read_text(encoding="utf-8")
    checks[name+"_uses_explicit_legacy_loader"]=(
        "from validation.load_data_numpy_legacy import load_real_data" in text
    )

legacy=ROOT/"validation/load_data_numpy_legacy.py"
checks["legacy_loader_preserved"]=legacy.exists()
legacy_imports=external_imports(legacy)
checks["legacy_loader_still_explicit_external"]=(
    "numpy" in legacy_imports and "pandas" in legacy_imports
)

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.validation.deterministic_stdlib_migration.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "details":details,
    "surface":{"N":len(z),"dataset":"data/real/Hz_data_real.csv"},
    "third_party_python_dependencies":[],
    "bayesian_legacy_migrated":False,
    "scientific_semantics_changed":False,
    "claim_allowed":False,
    "boundary":"This gate proves deterministic implementation parity for the simple validation route only. It does not migrate emcee/Bayesian inference and does not authorize model-selection or physical claims."
}
out=ROOT/"results/validation_deterministic_stdlib_migration.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
