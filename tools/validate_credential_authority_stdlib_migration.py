#!/usr/bin/env python3
"""Validate stdlib-only migration of the credential-authority workflow scanner."""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"tools"/"validate_rll_credential_authority.py"

module_name="rll_validate_credential_authority_gate_target"
spec=importlib.util.spec_from_file_location(module_name,TARGET)
mod=importlib.util.module_from_spec(spec)
sys.modules[module_name]=mod
spec.loader.exec_module(mod)

tree=ast.parse(TARGET.read_text(encoding="utf-8"))
imports=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Import):
        imports.update(alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node,ast.ImportFrom) and node.module:
        imports.add(node.module.split(".")[0])

checks={}
checks["no_pyyaml_import"]="yaml" not in imports

findings,payload=mod.audit(ROOT,mod.DEFAULT_POLICY)
checks["current_repository_static_pass"]=(
    payload.get("decision")=="PASS"
    and not [x for x in findings if x.severity=="ERROR"]
)

def fixture(workflow,path=".github/workflows/test.yml"):
    temp=tempfile.TemporaryDirectory()
    root=Path(temp.name)
    (root/".github/workflows").mkdir(parents=True)
    (root/"data/governance").mkdir(parents=True)
    policy=json.loads((ROOT/mod.DEFAULT_POLICY).read_text(encoding="utf-8"))
    (root/mod.DEFAULT_POLICY).write_text(json.dumps(policy,indent=2)+"\n",encoding="utf-8")
    target=root/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(workflow,encoding="utf-8")
    return temp,root

manual="""name: x
'on':
  workflow_dispatch:
permissions:
  contents: read
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      GITPAT: ${{ secrets.GITPAT }}
    steps:
      - run: echo safe
"""
tmp,root=fixture(manual,mod.GITHUB_ASSURANCE_WORKFLOW)
try:
    findings,_=mod.audit(root)
    codes={x.code for x in findings}
    checks["quoted_on_manual_guard_supported"]=(
        "GITPAT_NON_MANUAL" not in codes
        and "GITPAT_OUTSIDE_ASSURANCE_WORKFLOW" not in codes
        and "GITPAT_STRUCTURE_UNPARSED" not in codes
    )
finally:
    tmp.cleanup()

push="""name: x
on:
  push:
jobs:
  x:
    runs-on: ubuntu-latest
    env:
      CLIMA: ${{ secrets.CLIMA }}
    steps:
      - run: echo safe
"""
tmp,root=fixture(push)
try:
    findings,_=mod.audit(root)
    checks["non_manual_secret_blocked"]="CLIMATE_TRIAL_NON_MANUAL" in {x.code for x in findings}
finally:
    tmp.cleanup()

destructive="""name: x
on:
  workflow_dispatch:
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      CLIMA: ${{ secrets.CLIMA }}
    steps:
      - run: curl -X DELETE https://example.invalid/resource
"""
tmp,root=fixture(destructive)
try:
    findings,_=mod.audit(root)
    checks["destructive_secret_operation_blocked"]="DESTRUCTIVE_OPERATION_WITH_SECRET" in {x.code for x in findings}
finally:
    tmp.cleanup()

cross="""name: x
on: [workflow_dispatch]
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      GITPAT: ${{ secrets.GITPAT }}
      CLIMA: ${{ secrets.CLIMA }}
    steps:
      - run: echo safe
"""
tmp,root=fixture(cross,mod.GITHUB_ASSURANCE_WORKFLOW)
try:
    findings,_=mod.audit(root)
    checks["cross_credential_blocked"]="CROSS_CREDENTIAL_SAME_WORKFLOW" in {x.code for x in findings}
finally:
    tmp.cleanup()

failed=[name for name,ok in checks.items() if not ok]
result={
    "schema":"rll.credential_authority.stdlib_migration_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "third_party_python_dependencies":[],
    "network_requests_performed":0,
    "claim_allowed":False,
    "boundary":"This proves the narrow credential-workflow scanner preserves declared governance cases. It is not a general YAML parser, secret scanner, legal compliance proof, or security certification."
}
out=ROOT/"results"/"credential_authority_stdlib_migration.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result["pass"] else 5)
