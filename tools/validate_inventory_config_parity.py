#!/usr/bin/env python3
"""Validate parity between historical inventory_config.yml and canonical JSON mirror.

Stdlib only. Parser intentionally supports only the simple mapping/list subset used
by tools/inventory_config.yml; it is not a generic YAML parser.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
YML=ROOT/"tools/inventory_config.yml"
JSON_PATH=ROOT/"tools/inventory_config.json"

def scalar(text):
    s=text.strip()
    if len(s)>=2 and s[0]==s[-1] and s[0] in {"'", '"'}:
        return s[1:-1]
    return s

def parse_simple_yaml(path):
    root={}
    current_key=None
    current_mode=None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent=len(raw)-len(raw.lstrip(" "))
        s=raw.strip()
        if indent==0:
            if ":" not in s:
                raise ValueError("unsupported top-level line: "+s)
            key,val=s.split(":",1)
            key=key.strip(); val=val.strip()
            if val:
                root[key]=scalar(val); current_key=None; current_mode=None
            else:
                root[key]=None; current_key=key; current_mode=None
            continue
        if current_key is None:
            raise ValueError("indented value without parent: "+s)
        if s.startswith("- "):
            if current_mode not in (None,"list"):
                raise ValueError("mixed container for "+current_key)
            if current_mode is None:
                root[current_key]=[]; current_mode="list"
            root[current_key].append(scalar(s[2:]))
        else:
            if ":" not in s:
                raise ValueError("unsupported mapping line: "+s)
            if current_mode not in (None,"dict"):
                raise ValueError("mixed container for "+current_key)
            if current_mode is None:
                root[current_key]={}; current_mode="dict"
            key,val=s.split(":",1)
            root[current_key][key.strip()]=scalar(val)
    return root

legacy=parse_simple_yaml(YML)
modern=json.loads(JSON_PATH.read_text(encoding="utf-8"))
payload={
    "schema":"rll.inventory_config.serialization_parity.v1",
    "pass":legacy==modern,
    "legacy":str(YML.relative_to(ROOT)),
    "canonical_json":str(JSON_PATH.relative_to(ROOT)),
    "third_party_python_dependencies":[],
    "claim_allowed":False,
    "boundary":"Config serialization parity only; this is not a generic YAML parser or scientific evidence."
}
out=ROOT/"results/inventory_config_serialization_parity.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
