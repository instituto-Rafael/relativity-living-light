#!/usr/bin/env python3
"""Offline RLL LATIN evidence boundary validation; does not test physics."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/governance/latin-evidence-bridge.v1.json"
OUT=ROOT/"results/latin/latin-bridge-receipt.v1.json"
GATES={"graph_artifact_exact_head","governance_policy_exact_head","human_approval","provider_server_rule_readback","lowfala_ir_abi_parity","independent_rll_falsifier","copyright_translation_edition","rll_pr1076_independent_validation","privacy_legal_review"}

def validate(x):
    if x.get("schema")!="rll.latin-evidence-bridge.v1" or x.get("repo")!="instituto-Rafael/relativity-living-light":raise ValueError("invalid evidence authority")
    if x.get("owner_role")!="SCIENTIFIC_CONSUMER_NOT_AUTHORITATIVE_FOR_LATIN_COMPILE":raise ValueError("compiler owner override")
    for name,expected in (("graph","rafaelmeloreisnovo/RafPolimata"),("governance","rafaelmeloreisnovo/RafGitTools")):
        src=x.get("source_producers",{}).get(name,{})
        if src.get("repo")!=expected or re.fullmatch("[0-9a-f]{40}",src.get("commit","")) is None:raise ValueError("producer commit is unpinned")
    if not GATES.issubset(x.get("outstanding_gates",{})):raise ValueError("missing gate")
    if any(state=="PASS" for state in x["outstanding_gates"].values()):raise ValueError("unproven gate promotion")
    if x["outstanding_gates"]["independent_rll_falsifier"]!="NOT_RUN":raise ValueError("science falsifier was not executed")
    s=x.get("secrets_boundary",{})
    if s.get("secret_values_used") is not False or s.get("secret_fallback") is not False or s.get("administration_called") is not False:raise ValueError("secret misuse")
    if s.get("K_SECRETS")!="TOKEN_VAZIO_NO_VERIFIED_PROVIDER_INSTALLATION":raise ValueError("admin patch incorrectly asserted")
    g=x.get("governance",{})
    for k in ("no_network","no_admin","no_code_mutation","no_training"):
        if g.get(k) is not True:raise ValueError("unsafe runtime permission "+k)
    for k in ("auto_dispatch","auto_merge","claim_allowed"):
        if g.get(k) is not False:raise ValueError("automatic promotion "+k)
    if x.get("claim_allowed") is not False:raise ValueError("scientific claim not allowed")
    return {"schema":"rll.latin-bridge-receipt.v1","state":"PASS_EVIDENCE_BOUNDARY_STRUCTURE_ONLY","physical_runtime":"NOT_RUN","scientific_validation":"NOT_RUN","provider_admin":"NOT_RUN","claim_allowed":False}

def main():
    raw=SOURCE.read_bytes()
    receipt=validate(json.loads(raw))
    receipt["contract_sha256"]=hashlib.sha256(raw).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
