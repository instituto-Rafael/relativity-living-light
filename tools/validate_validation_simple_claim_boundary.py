#!/usr/bin/env python3
"""Validate claim boundary of validation/check_falsification.py."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"validation/check_falsification.py"

module_name="rll_simple_falsification_gate_target"
spec=importlib.util.spec_from_file_location(module_name,TARGET)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

checks={}

higher=mod.evaluate({"chi2_lcdm":10.0,"chi2_rll":12.0})
lower=mod.evaluate({"chi2_lcdm":10.0,"chi2_rll":8.0})
equal=mod.evaluate({"chi2_lcdm":10.0,"chi2_rll":10.0})

checks["higher_diagnostic"]=higher["diagnostic_state"]=="RLL_HIGHER_CHI2_IN_THIS_RUN"
checks["lower_diagnostic"]=lower["diagnostic_state"]=="RLL_LOWER_CHI2_IN_THIS_RUN"
checks["equal_diagnostic"]=equal["diagnostic_state"]=="CHI2_EQUAL_IN_THIS_RUN"
checks["claim_closed"]=all(
    row.get("claim_allowed") is False
    and row.get("model_selection_claim_allowed") is False
    and row.get("falsification_claim_allowed") is False
    for row in (higher,lower,equal)
)
checks["no_winner_field"]=all("winner" not in row for row in (higher,lower,equal))
checks["boundary_explicit"]=all(
    "does not declare a winner" in row.get("boundary","")
    and "falsify" in row.get("boundary","").lower()
    for row in (higher,lower,equal)
)
checks["promotion_requirements_present"]=all(
    len(row.get("required_for_promotion",[]))>=5 for row in (higher,lower,equal)
)

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.validation.simple_claim_boundary_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "claim_allowed":False,
    "boundary":"This test checks language/state promotion rules only; it does not validate any cosmological model."
}
out=ROOT/"results/validation_simple_claim_boundary.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
