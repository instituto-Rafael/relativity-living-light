#!/usr/bin/env python3
"""Validate bounded Rx HTTP migration without performing real network I/O.

Stdlib only. Tests transport semantics plus the two migrated fetcher surfaces.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from rx import http as rx_http

TARGETS=[
    ROOT/"scripts"/"fetch_real_sources.py",
    ROOT/"scripts"/"fetch_public_astronomy_catalog_samples.py",
]

def imported_roots(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    out=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            out.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out

def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FakeHeaders(dict):
    def get(self,key,default=None):
        return super().get(key,default)

class FakeResponse:
    def __init__(self,payload,status=200,headers=None):
        self.payload=payload
        self.status=status
        self.headers=FakeHeaders(headers or {})
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n=-1):
        return self.payload if n<0 else self.payload[:n]

class FakeOpener:
    def __init__(self,payload):
        self.payload=payload
        self.last_request=None
    def open(self,request,timeout=None):
        self.last_request=request
        return FakeResponse(self.payload,status=200,headers={"Content-Length":str(len(self.payload))})

checks={}
details={}

for path in TARGETS:
    roots=imported_roots(path)
    checks[path.name+"_no_requests_import"]="requests" not in roots
    checks[path.name+"_uses_rx"]="rx" in roots

real=load_module(TARGETS[0],"rll_fetch_real_sources_gate")
astro=load_module(TARGETS[1],"rll_fetch_public_astronomy_gate")

nonheavy_hosts={
    urlsplit(cfg["url"]).hostname
    for cfg in real.SOURCES.values()
    if not cfg.get("heavy",False)
}
checks["real_source_nonheavy_hosts_allowlisted"]=nonheavy_hosts.issubset(set(real.FETCH_ALLOWED_HOSTS))
details["real_source_nonheavy_hosts"]=sorted(nonheavy_hosts)
checks["astronomy_endpoints_allowlisted"]={
    urlsplit(astro.SDSS_ENDPOINT).hostname,
    urlsplit(astro.OSC_URL).hostname,
}.issubset(set(astro.FETCH_ALLOWED_HOSTS))

original_build=urllib.request.build_opener
try:
    fake=FakeOpener(b'{"ok":true}')
    urllib.request.build_opener=lambda *args,**kwargs: fake
    payload=rx_http.get_json(
        "https://example.org/api",
        allowed_hosts={"example.org"},
        params={"q":"a b","n":2},
        max_bytes=1024,
    )
    checks["allowlisted_json_success"]=payload=={"ok":True}
    checks["query_params_encoded"]="q=a+b" in fake.last_request.full_url and "n=2" in fake.last_request.full_url

    try:
        rx_http.get_bytes("http://example.org/a",allowed_hosts={"example.org"})
        checks["http_scheme_blocked"]=False
    except rx_http.RxHttpError:
        checks["http_scheme_blocked"]=True

    try:
        rx_http.get_bytes("https://evil.example/a",allowed_hosts={"example.org"})
        checks["unknown_host_blocked"]=False
    except rx_http.RxHttpError:
        checks["unknown_host_blocked"]=True

    urllib.request.build_opener=lambda *args,**kwargs: FakeOpener(b"x"*33)
    try:
        rx_http.get_bytes("https://example.org/a",allowed_hosts={"example.org"},max_bytes=32)
        checks["response_limit_enforced"]=False
    except rx_http.RxHttpError:
        checks["response_limit_enforced"]=True
finally:
    urllib.request.build_opener=original_build

failed=[name for name,passed in checks.items() if not passed]
payload={
    "schema":"rll.rx.http_migration_gate.v1",
    "pass":not failed,
    "checks":checks,
    "failed_checks":failed,
    "details":details,
    "third_party_python_dependencies":[],
    "network_requests_performed":0,
    "claim_allowed":False,
    "boundary":"This gate proves bounded transport behavior and import migration only. It does not prove remote service availability, legal permission for a source, scientific validity, or absence of network-stack vulnerabilities."
}
out=ROOT/"results"/"rx_http_migration_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
