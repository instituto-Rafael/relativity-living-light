#!/usr/bin/env python3
"""Fail-closed maturity gate for RLL promotion edges.

Repository-local structure only; never validates scientific claims or external settings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

TOPOLOGY={"rll/lab":"WORK","rll/integration":"rll/lab","rll/release":"rll/integration","main":"rll/release"}
SENSITIVE={".env","rclone.conf","id_rsa","id_ed25519","credentials.json","service-account.json"}
# YAML/TOML scalar assignment only. Anchoring at the beginning of a logical line
# prevents documentation strings such as '- "claim_allowed=true"' from being
# mistaken for an executable governance field.
CLAIM_TRUE_ASSIGNMENT=re.compile(
    r"(?im)^\s*[\"']?claim_allowed[\"']?\s*[:=]\s*(?:true|yes|on|1)\s*(?:#.*)?$"
)


def norm(ref:str)->str:
    for p in ("refs/heads/","origin/"):
        if ref.startswith(p): return ref[len(p):]
    return ref


def valid_transition(head:str,base:str)->bool:
    head,base=norm(head),norm(base)
    expected=TOPOLOGY.get(base)
    return bool(expected and ((expected=="WORK" and head not in TOPOLOGY and head!=base) or head==expected))


def changed(base_sha:str,head_sha:str)->list[str]:
    p=subprocess.run(["git","diff","--name-only","--diff-filter=ACMRTUXB",base_sha,head_sha],check=True,capture_output=True,text=True)
    return sorted({x.strip() for x in p.stdout.splitlines() if x.strip()})


def _json_has_claim_true(value:object)->bool:
    if isinstance(value,dict):
        for key,item in value.items():
            if str(key).lower()=="claim_allowed" and item is True:
                return True
            if _json_has_claim_true(item):
                return True
    elif isinstance(value,list):
        return any(_json_has_claim_true(item) for item in value)
    return False


def file_has_claim_true(path:Path)->bool:
    """Detect actual claim_allowed=true fields, not quoted documentation text."""
    text=path.read_text(encoding="utf-8",errors="replace")
    suffix=path.suffix.lower()
    if suffix==".json":
        try:
            return _json_has_claim_true(json.loads(text))
        except json.JSONDecodeError:
            # Invalid JSON is handled by other architecture/YAML gates; remain
            # fail-closed here only if an explicit assignment is still visible.
            return bool(CLAIM_TRUE_ASSIGNMENT.search(text))
    return bool(CLAIM_TRUE_ASSIGNMENT.search(text))


def evaluate(root:Path,head_ref:str,base_ref:str,files:list[str])->dict:
    residuals=[]
    if not valid_transition(head_ref,base_ref): residuals.append("INVALID_BRANCH_TRANSITION")
    if not files: residuals.append("EMPTY_CHANGESET")
    for rel in files:
        p=Path(rel); low=rel.lower()
        if p.name.lower() in SENSITIVE or low.startswith(".ssh/") or low.endswith((".pem",".p12",".pfx",".key")): residuals.append(f"SENSITIVE_PATH:{rel}")
        if low.startswith(("tests/","docs/","fixtures/","examples/")): continue
        if p.suffix.lower() in {".yml",".yaml",".json",".toml"}:
            target=root/rel
            if target.is_file() and target.stat().st_size<1_000_000 and file_has_claim_true(target):
                residuals.append(f"CLAIM_ALLOWED_TRUE:{rel}")
    base=norm(base_ref)
    if base in {"rll/release","main"} and any(x.startswith(("src/","tools/","scripts/","data/")) for x in files):
        has_evidence=any(any(k in x.lower() for k in ("receipt","evidence","manifest","provenance","ledger")) for x in files)
        has_gap=any("token_vazio" in x.lower() for x in files)
        if not (has_evidence or has_gap): residuals.append("RELEASE_REQUIRES_EVIDENCE_OR_EXPLICIT_GAP")
    return {"schema":"rll.branch_maturity_gate.v2","head_ref":norm(head_ref),"base_ref":base,"changed_files":files,"decision":"PASS" if not residuals else "BLOCKED","residuals":residuals,"claim_allowed":False,"publication_effect":"NONE","external_settings":"TOKEN_VAZIO_EXTERNAL_SETTINGS"}


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--head-ref",required=True); p.add_argument("--base-ref",required=True); p.add_argument("--base-sha",required=True); p.add_argument("--head-sha",required=True); p.add_argument("--output",default="artifacts/branch-maturity-v2/receipt.json"); args=p.parse_args()
    root=Path.cwd(); data=evaluate(root,args.head_ref,args.base_ref,changed(args.base_sha,args.head_sha)); out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8"); print(json.dumps(data,indent=2)); return 0 if data["decision"]=="PASS" else 1


if __name__=="__main__": sys.exit(main())
