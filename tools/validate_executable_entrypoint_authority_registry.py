#!/usr/bin/env python3
"""Validate RLL executable entrypoint authority registry against governance contracts.

Stdlib only. Does not execute any registered entrypoint.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/governance/RLL_EXECUTABLE_ENTRYPOINT_AUTHORITY_REGISTRY_V1.json"
PURPOSE=ROOT/"data/governance/RLL_DATA_USE_PURPOSE_REGISTRY_V1.json"
POLICY=ROOT/"data/governance/RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    reg=load(REG); purpose=load(PURPOSE); policy=load(POLICY)
    errors=[]; warnings=[]
    if reg.get("schema")!="rll.executable_entrypoint_authority_registry.v1":
        errors.append("registry_schema")
    if reg.get("claim_allowed") is not False:
        errors.append("claim_allowed_must_be_false")

    valid_levels=set(reg.get("authority_levels",{}))
    valid_data=set(reg.get("data_classes",{}))
    route_ids=set()
    purpose_ids={r.get("route_id") for r in purpose.get("routes",[]) if r.get("route_id")}

    for row in reg.get("routes",[]):
        rid=row.get("route_id")
        if not rid:
            errors.append("route_missing_id"); continue
        if rid in route_ids:
            errors.append("duplicate_route:"+rid)
        route_ids.add(rid)

        level=row.get("max_authority_default")
        if level not in valid_levels:
            errors.append("invalid_level:"+rid)
        opt=row.get("max_authority_optional")
        if opt is not None and opt not in valid_levels:
            errors.append("invalid_optional_level:"+rid)

        for cls in row.get("data_classes",[]):
            if cls not in valid_data:
                errors.append("invalid_data_class:%s:%s"%(rid,cls))

        if level in {"A2","A3","A4","A5"} and row.get("human_gate_for_default") is not True:
            errors.append("human_gate_required:"+rid)
        if level=="A5" and row.get("default_decision")!="DENY":
            errors.append("a5_must_default_deny:"+rid)
        if row.get("secrets") is True:
            errors.append("raw_secret_permission_forbidden:"+rid)

        if rid in {"RLL_RX_REAL_VALIDATION_V1","RLL_RX_MULTIPROBE_V1","RLL_RX_CLI_DEVELOPMENT_V1","RLL_FREESTANDING_REAL_KERNEL","STRUCTURE_D_RX_SUCCESSOR","SECURITY_AUDIT","PUBLIC_SOURCE_FETCHERS_STDLIB","PUBLIC_DATA_IMPORT_AUDIT_STDLIB","CALC_DATA_AUDIT_STDLIB","CI_SCIENTIFIC_SKILLS_STDLIB"} and rid not in purpose_ids:
            errors.append("missing_from_purpose_registry:"+rid)

    if policy.get("human_authority",{}).get("self_authorization")!="FORBIDDEN":
        errors.append("policy_self_authorization_not_forbidden")
    if "network.write" not in set(policy.get("forbidden_capabilities",[])):
        errors.append("policy_network_write_not_forbidden")
    if "PERSONAL_DATA" not in set(policy.get("data_governance",{}).get("denied_by_default",[])):
        errors.append("personal_data_not_denied_by_default")

    if "STRUCTURE_D_RX_SUCCESSOR" not in purpose_ids:
        warnings.append("structure_d_rx_successor_not_yet_in_purpose_registry")

    result={
      "schema":"rll.executable_entrypoint_authority_registry_validation.v1",
      "pass":not errors,
      "errors":errors,
      "warnings":warnings,
      "route_count":len(reg.get("routes",[])),
      "claim_allowed":False,
      "boundary":"Registry validation proves governance consistency only; it does not execute routes, prove OS sandboxing, legal compliance, or absence of vulnerabilities."
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))
    out=ROOT/"results/executable_entrypoint_authority_registry_validation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return 0 if result["pass"] else 5

if __name__=="__main__":
    raise SystemExit(main())
