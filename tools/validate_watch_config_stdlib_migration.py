#!/usr/bin/env python3
"""Parity gate for stdlib technology-watch config/schema migration."""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from rx.schema_subset import RxSchemaSubsetError
from rx.yaml_subset import RxYamlSubsetError, loads as load_yaml_text

TARGET=ROOT/"scripts"/"validate_watch_config.py"
LEGACY=ROOT/"rll_inovacao_tecnologica_watch.yml"
CANONICAL=ROOT/"rll_inovacao_tecnologica_watch.json"
SCHEMA=ROOT/"schemas"/"rll_watch.schema.json"

spec=importlib.util.spec_from_file_location("rll_watch_validator_gate",TARGET)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tree=ast.parse(TARGET.read_text(encoding="utf-8"))
roots=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Import):
        roots.update(alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node,ast.ImportFrom) and node.module:
        roots.add(node.module.split(".")[0])

checks={}
checks["no_yaml_import"]="yaml" not in roots
checks["no_jsonschema_import"]="jsonschema" not in roots

legacy=mod.load_config(LEGACY)
canonical=mod.load_config(CANONICAL)
checks["legacy_yaml_equals_canonical_json"]=legacy==canonical

try:
    mod.validate_config(LEGACY,SCHEMA)
    checks["legacy_schema_pass"]=True
except Exception:
    checks["legacy_schema_pass"]=False

try:
    mod.validate_config(CANONICAL,SCHEMA)
    checks["canonical_schema_pass"]=True
except Exception:
    checks["canonical_schema_pass"]=False

schema=json.loads(SCHEMA.read_text(encoding="utf-8"))

def invalid_case(payload):
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"config.json"
        p.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
        try:
            mod.validate_config(p,SCHEMA)
        except (RxSchemaSubsetError,ValueError,TypeError):
            return True
        return False

missing=json.loads(json.dumps(canonical))
del missing["source"]["name"]
checks["missing_required_rejected"]=invalid_case(missing)

bad_enum=json.loads(json.dumps(canonical))
bad_enum["source"]["academic_weight"]="invented_weight"
checks["enum_rejected"]=invalid_case(bad_enum)

bad_date=json.loads(json.dumps(canonical))
bad_date["source"]["last_reviewed"]="2026-99-99"
checks["invalid_date_rejected"]=invalid_case(bad_date)

try:
    load_yaml_text("source:\n  name: &anchor value\n")
    checks["yaml_anchor_rejected"]=False
except RxYamlSubsetError:
    checks["yaml_anchor_rejected"]=True

try:
    load_yaml_text("source:\n  text: |\n    hello\n")
    checks["yaml_block_scalar_rejected"]=False
except RxYamlSubsetError:
    checks["yaml_block_scalar_rejected"]=True

failed=[name for name,ok in checks.items() if not ok]
payload={
    "schema":"rll.watch_config.stdlib_migration_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "legacy_yaml_preserved":True,
    "canonical_config":"rll_inovacao_tecnologica_watch.json",
    "yaml_support":"STRICT_SUBSET_ONLY",
    "json_schema_support":"STRICT_SUBSET_ONLY",
    "third_party_python_dependencies":[],
    "scientific_semantics_changed":False,
    "claim_allowed":False,
    "boundary":"Parity covers only the versioned technology-watch configuration and its declared schema subset. It is not general YAML/JSON-Schema conformance or scientific validation."
}
out=ROOT/"results"/"watch_config_stdlib_migration.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
