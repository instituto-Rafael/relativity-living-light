#!/usr/bin/env python3
"""Gate the stdlib-only migration of CI scientific Tier-1 diagnostics.

No network. No model training. No AI runtime. This validates engineering parity
for deterministic diagnostics only.
"""
from __future__ import annotations

import ast
import csv
import json
import math
import tempfile
from pathlib import Path

from tools.ci_scientific_skills import (
    anomaly_diagnostic,
    bayes_proxy_diagnostic,
    fourier_torus_diagnostic,
    robust_anomaly_scores,
    run,
)

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/"tools/ci_scientific_skills.py"
TEST=ROOT/"tests/test_ci_scientific_skills.py"
WORKFLOW=ROOT/".github/workflows/ci-scientific-skills.yml"

STDLIB={
    "__future__","argparse","csv","hashlib","json","math","statistics",
    "pathlib","typing","tempfile","unittest",
}

def roots(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    out=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            out.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out

tool_imports=roots(TOOL)
test_imports=roots(TEST)
checks={}
details={}

tool_external=sorted(tool_imports-STDLIB)
test_external=sorted(test_imports-STDLIB-{"tools"})
checks["tool_zero_third_party"]=not tool_external
checks["test_zero_third_party"]=not test_external
details["tool_external"]=tool_external
details["test_external"]=test_external

scores=robust_anomaly_scores([1.0,1.1,0.9,1.05,40.0])
outlier=max(range(len(scores)),key=lambda i:abs(scores[i]))
checks["mad_outlier_parity"]=outlier==4 and abs(scores[4])>3.5

fourier=fourier_torus_diagnostic(samples=2048,max_mode=32)
checks["fourier_verified"]=fourier["status"]=="VERIFIED_METHOD"
checks["fourier_rmse_gate"]=fourier["rmse"]<1e-12
checks["fourier_tail_gate"]=fourier["tail_energy_after_mode_5"]<1e-24

with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)
    anomaly_path=base/"observations.csv"
    with anomaly_path.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=["value"])
        writer.writeheader()
        for value in [1.0,1.1,0.9,1.05,40.0]:
            writer.writerow({"value":value})
    anomaly=anomaly_diagnostic(anomaly_path)
    checks["anomaly_fixture"]=(
        anomaly["status"]=="EVIDENCED_ON_REPOSITORY_DATA"
        and anomaly["anomaly_indices"]==[4]
        and len(anomaly["input_sha256"])==64
    )

    bic_path=base/"comparison.csv"
    with bic_path.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=["model","BIC"])
        writer.writeheader()
        writer.writerows([
            {"model":"lcdm","BIC":110.0},
            {"model":"rll","BIC":116.0},
        ])
    bic=bayes_proxy_diagnostic(bic_path)
    checks["bic_proxy_fixture"]=(
        bic["preferred_by_bic"]=="lcdm"
        and abs(bic["delta_bic_alternative_minus_preferred"]-6.0)<1e-15
        and abs(bic["log_bayes_proxy_preferred_vs_alternative"]-3.0)<1e-15
    )

    report=base/"artifact/report.json"
    missing=run(base,report,strict=False)
    checks["token_vazio_preserved"]=(
        missing["overall_status"]=="TOKEN_VAZIO"
        and missing["skills"]["C1_anomaly_diagnostic"]["status"]=="TOKEN_VAZIO"
        and missing["skills"]["D1_bayes_proxy"]["status"]=="TOKEN_VAZIO"
    )

workflow=WORKFLOW.read_text(encoding="utf-8")
checks["workflow_no_pip_install"]="pip install" not in workflow
checks["workflow_no_pytest"]="pytest" not in workflow
checks["workflow_uses_unittest"]="python -m unittest" in workflow

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.ci_scientific_skills.stdlib_migration.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "details":details,
    "fourier":{
        "samples":fourier["samples"],
        "max_mode":fourier["max_mode"],
        "rmse":fourier["rmse"],
        "tail_energy_after_mode_5":fourier["tail_energy_after_mode_5"],
    },
    "third_party_python_dependencies":[],
    "network_requests_performed":0,
    "training":False,
    "ai_runtime":False,
    "scientific_semantics_changed":False,
    "claim_allowed":False,
    "boundary":"This gate proves stdlib implementation parity for Tier-1 diagnostics only. BIC remains a proxy, T^1 does not prove T^7 behavior, anomaly flags are diagnostics, and no physical claim is promoted."
}
out=ROOT/"results/ci_scientific_skills_stdlib_migration.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
