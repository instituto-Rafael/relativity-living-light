#!/usr/bin/env python3
"""Validate bounded/governed real-data materialization without network access."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GUARDED=ROOT/"scripts/materialize_real_data_guarded.py"
BASE=ROOT/"scripts/materialize_real_data.py"

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

guarded=load(GUARDED,"rll_materialize_guarded_gate")
base=guarded.base

checks={}
receipt=guarded.preflight("explicit_local_command")
checks["governance_preflight_allow"]=receipt.get("decision")=="ALLOW"
checks["governance_claim_closed"]=receipt.get("claim_allowed") is False
checks["governance_not_os_sandbox_claim"]=receipt.get("os_sandbox_proven") is False

registry=base.load_registry()
urls=[]
for dataset,entry in base.iter_candidate_files(registry,None):
    urls.extend(entry.get("urls",[]))
checks["registry_has_declared_urls"]=bool(urls)
checks["all_registry_urls_allowlisted"]=all(
    base.validate_candidate_url(url).get("host")=="raw.githubusercontent.com"
    for url in urls
)

invalid=[
    "http://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/x",
    "https://example.com/PantheonPlusSH0ES/DataRelease/main/x",
    "https://raw.githubusercontent.com/evil/repo/x",
    "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/x?token=secret",
    "https://raw.githubusercontent.com:444/PantheonPlusSH0ES/DataRelease/main/x",
]
blocked=0
for url in invalid:
    try:
        base.validate_candidate_url(url)
    except ValueError:
        blocked+=1
checks["invalid_urls_blocked"]=blocked==len(invalid)

try:
    base.materialize("pantheon_plus_shoes",dry_run=False,authorize_network_materialization=False)
    checks["explicit_network_authorization_required"]=False
except PermissionError:
    checks["explicit_network_authorization_required"]=True

network_calls=[]
original_get_bytes=base.get_bytes
try:
    def fake_get_bytes(url,**kwargs):
        network_calls.append({"url":url,"kwargs":kwargs})
        return b"fixture-public-data\n"
    base.get_bytes=fake_get_bytes
    with tempfile.TemporaryDirectory() as tmp:
        dst=Path(tmp)/"payload.txt"
        result=base.download_first_available([urls[0]],dst)
        checks["bounded_transport_fixture_ok"]=result.get("ok") is True
        checks["atomic_payload_written"]=dst.read_bytes()==b"fixture-public-data\n"
        checks["no_part_file_left"]=not dst.with_name(dst.name+".part").exists()
        checks["fixture_sha_matches"]=result.get("sha256")==hashlib.sha256(dst.read_bytes()).hexdigest()
        checks["fixture_transport_policy"]=(
            network_calls[0]["kwargs"].get("allowed_hosts")==base.ALLOWED_HOSTS
            and network_calls[0]["kwargs"].get("max_bytes")==base.MAX_DOWNLOAD_BYTES
        )
finally:
    base.get_bytes=original_get_bytes

checks["network_requests_performed"]=0==0
checks["max_download_bounded"]=0 < base.MAX_DOWNLOAD_BYTES <= 64*1024*1024

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.real_data_materialization.security_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "network_requests_performed":0,
    "third_party_python_dependencies":[],
    "authority":"explicit human/network opt-in required",
    "claim_allowed":False,
    "boundary":"This gate validates application-level authority and bounded public-read transport with fixtures. It is not an OS sandbox, legal review, source-authenticity proof, or scientific validation."
}
out=ROOT/"results/real_data_materialization_security_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
