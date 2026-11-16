#!/usr/bin/env python3
"""Verify legacy validacao_real YAML point payloads equal the Rx JSON siblings.

Stdlib only. This parser is intentionally narrow: it accepts only the two
committed legacy point formats used by validacao_real/data/*.yml.
"""
from __future__ import annotations
import ast,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"validacao_real"/"data"

def scalar(text):
    value=text.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value in {"true","True"}: return True
    if value in {"false","False"}: return False
    try:
        return int(value)
    except ValueError:
        try: return float(value)
        except ValueError: return value

def parse_inline_map(text):
    body=text.strip()
    if body.startswith("-"): body=body[1:].strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError("expected inline mapping")
    body=body[1:-1]
    out={}
    for part in body.split(","):
        if not part.strip(): continue
        key,val=part.split(":",1)
        out[key.strip()]=scalar(val)
    return out

def parse_points(path):
    lines=path.read_text(encoding="utf-8").splitlines()
    in_points=False; points=[]; current=None
    for raw in lines:
        stripped=raw.strip()
        if not in_points:
            if stripped=="points:": in_points=True
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if raw and not raw.startswith(" "):
            break
        if stripped.startswith("- {"):
            points.append(parse_inline_map(stripped))
            current=None
            continue
        if stripped.startswith("- "):
            if current is not None: points.append(current)
            current={}
            first=stripped[2:]
            if ":" in first:
                key,val=first.split(":",1); current[key.strip()]=scalar(val)
            continue
        if current is not None and ":" in stripped:
            key,val=stripped.split(":",1)
            current[key.strip()]=scalar(val)
    if current is not None: points.append(current)
    return points

def norm(obj):
    if isinstance(obj,float): return round(obj,12)
    if isinstance(obj,dict): return {k:norm(v) for k,v in sorted(obj.items())}
    if isinstance(obj,list): return [norm(v) for v in obj]
    return obj

pairs=[
 ("desi_dr2_bao.yml","desi_dr2_bao_rx.json"),
 ("hz_cosmic_chronometers.yml","hz_cosmic_chronometers_rx.json"),
]
rows=[]; overall=True
for legacy_name,json_name in pairs:
    legacy=parse_points(BASE/legacy_name)
    modern=json.loads((BASE/json_name).read_text(encoding="utf-8"))["points"]
    passed=norm(legacy)==norm(modern)
    overall=overall and passed
    rows.append({
      "legacy":str((BASE/legacy_name).relative_to(ROOT)),
      "rx_json":str((BASE/json_name).relative_to(ROOT)),
      "legacy_points":len(legacy),
      "rx_points":len(modern),
      "pass":passed
    })

payload={
 "schema":"rll.validacao_real.serialization_parity.v1",
 "pass":overall,
 "pairs":rows,
 "third_party_python_dependencies":[],
 "claim_allowed":False,
 "boundary":"This proves point-payload serialization parity only; it does not prove scientific validity or remote freshness."
}
out=ROOT/"results"/"validacao_real_serialization_parity.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if overall else 5)
