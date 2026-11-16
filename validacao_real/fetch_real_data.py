#!/usr/bin/env python3
"""Materialize declared real-data anchors for the legacy validation route.

Stdlib/project-local only. JSON is the executable serialization; historical
YAML files remain preserved as provenance and are checked by
tools/validate_validacao_real_serialization_parity.py.

Network is OFF by default. Optional public-source reachability probes must be
explicitly enabled with RLL_LEGACY_NETWORK_PROBE=1 and pass the shared
development_guard host policy.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from internal.governance.development_guard import safe_public_probe

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "fetched"
SOURCES = HERE / "sources_rx.json"
POLICY = ROOT / "data" / "governance" / "RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json"
CLAIM_BOUNDARY = (
    "Committed local fallback payloads are provenance anchors only. "
    "Remote reachability or fallback materialization does not validate RLL, "
    "does not prove superiority over LCDM/CPL, and does not replace a full "
    "likelihood with baseline, metric, uncertainty/covariance and report."
)

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    registry = load_json(SOURCES)
    policy = load_json(POLICY)
    network_enabled = os.environ.get("RLL_LEGACY_NETWORK_PROBE", "0") == "1"
    OUT.mkdir(exist_ok=True)
    manifest = {
        "schema": "rll.validacao_real.legacy_json_materialization.v1",
        "generated_utc": utc_now(),
        "network_probe_enabled": network_enabled,
        "claim_boundary": CLAIM_BOUNDARY,
        "sources": [],
    }

    for source in registry["sources"]:
        sid = source["id"]
        fallback = HERE / source["embedded_fallback"]
        portal = source.get("portal", "")
        remote = None
        remote_error = "NETWORK_OFF"
        if network_enabled and portal:
            try:
                remote = safe_public_probe(policy, portal, user_agent="RLL-validacao-json/1.0")
                remote_error = ""
            except Exception as exc:
                remote_error = exc.__class__.__name__

        payload = load_json(fallback)
        out_path = OUT / (sid + ".json")
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        provenance = {
            "source_id": sid,
            "fetched_utc": utc_now(),
            "portal": portal,
            "network_probe_enabled": network_enabled,
            "remote_probe": remote,
            "remote_error": remote_error or "NONE",
            "used": "committed_rx_json_fallback",
            "fallback_path": str(fallback.relative_to(HERE)),
            "fallback_state": "committed_local_payload_not_fresh_remote_download",
            "claim_boundary": CLAIM_BOUNDARY,
            "n_points": len(payload.get("points", [])),
        }
        manifest["sources"].append(provenance)
        print("[%s] wrote %s (%d points)" % (
            sid, out_path.relative_to(HERE), provenance["n_points"]
        ))

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("manifest -> fetched/manifest.json")
    print("serialization=JSON third_party_python_dependencies=0")
    print("claim boundary -> " + CLAIM_BOUNDARY)
    return 0

if __name__ == "__main__":
    sys.exit(main())
