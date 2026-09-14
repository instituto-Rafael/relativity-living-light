#!/usr/bin/env python3
"""Observe RLL credential bindings and emit seven-guard receipts without network I/O.

A structural PASS validates this preflight, never authentication or scientific
readiness. Run with --require-bindings to make absent/ambiguous bindings fatal.
Receipts are created exclusively; a second run must use a new receipt path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from scripts import rll_dual_api_real_climate_calibration as dualapi
from tools.agent import rll_agent_authority as authority
from tools.validate_rll_evidence_evolution_matrix import REQUIRED_GUARDS, validate_matrix

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "2a6e80ad0efa182217aa76c55665a4c98a4e5523"
REPOSITORY = "instituto-Rafael/relativity-living-light"
SOURCES = (
    "data/governance/rll_agent_authority.v1.json",
    "data/governance/RLL_CREDENTIAL_AUTHORITY_POLICY_V1.json",
    "data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json",
    "tools/agent/rll_agent_authority.py",
    "tools/agent/rll_agent_seven_guards.py",
    "tools/validate_rll_evidence_evolution_matrix.py",
)
TV = "TOKEN_VAZIO"


def observe_bindings(runtime):
    if runtime not in {"agents", "actions", "offline"}:
        raise ValueError("UNSUPPORTED_RUNTIME")
    bindings = {}
    gaps = []
    if runtime == "offline":
        return bindings, ["TOKEN_VAZIO_RUNTIME_BINDINGS_NOT_CHECKED"]
    if runtime == "actions":
        # Actions values must be injected by a reviewed manual job. Never
        # fall back to Agents names just because they happen to be present.
        for role, name in (("github_assurance", "GITPAT"), ("climate", "CLIMA")):
            bindings[role] = {"name": name, "present": bool(os.environ.get(name))}
            if not bindings[role]["present"]:
                gaps.append(f"TOKEN_VAZIO_ACTIONS_{role.upper()}_BINDING")
        return bindings, gaps

    for role, resolver, known in (
        ("github", authority.resolve_pat, {*authority.PAT_ALIASES, "GIT"}),
        ("climate", lambda: dualapi.resolve_secret(
            dualapi.CLIMATE_SELECTOR, ("CLIMATE", "CLIMATE_ENGINE_API_KEY")
        ), {"CLIMATE", "CLIMATE_ENGINE_API_KEY"}),
    ):
        try:
            name, value = resolver()
            bindings[role] = {
                "name": name if name in known else ("CUSTOM_SELECTOR" if name else TV),
                "present": bool(value),
            }
            if not value:
                gaps.append(f"TOKEN_VAZIO_AGENTS_{role.upper()}_BINDING")
            del value
        except (authority.AuthorityError, dualapi.CalibrationError):
            # No exception payload, environment dump, secret size or hash.
            bindings[role] = {"name": TV, "present": False}
            gaps.append(f"TOKEN_VAZIO_AGENTS_{role.upper()}_RESOLUTION")
    return bindings, gaps


def source_commit(root):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=False,
            capture_output=True, text=True, timeout=5,
        )
        candidate = result.stdout.strip()
        if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40,64}", candidate):
            return candidate
    except (OSError, subprocess.SubprocessError):
        pass
    return TV


def build_receipt(runtime="offline", root=ROOT):
    root = Path(root)
    sources = []
    errors = []
    for name in SOURCES:
        try:
            raw = (root / name).read_bytes()
            sources.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest()})
        except OSError:
            errors.append("SOURCE_UNAVAILABLE:" + name)
    matrix_path = root / "data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json"
    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        matrix_errors = validate_matrix(matrix)
        # Persist only counts: malformed source fields may contain arbitrary text.
        if matrix_errors:
            errors.append("MATRIX_CONTRACT_INVALID")
    except (OSError, ValueError, TypeError, AttributeError):
        errors.append("MATRIX_UNAVAILABLE_OR_INVALID")

    bindings, binding_gaps = observe_bindings(runtime)
    observed_commit = source_commit(root)
    gaps = [
        "TOKEN_VAZIO_AUTHENTICATION_NOT_TESTED_BY_THIS_PREFLIGHT",
        "TOKEN_VAZIO_INTRINSIC_PAT_PERMISSIONS",
        "TOKEN_VAZIO_GIT_SECRET_ROLE",
        "TOKEN_VAZIO_CLIMATE_DATASET_AND_INDEPENDENT_SCIENTIFIC_GATE",
        *binding_gaps,
    ]
    if observed_commit == TV:
        gaps.append("TOKEN_VAZIO_SOURCE_COMMIT")
    ready = bool(bindings) and all(item["present"] for item in bindings.values())
    receipt = {
        "schema": "rll.agent_seven_guards.receipt.v1",
        "receipt_id": "RLL-AGENT-7G-" + uuid.uuid4().hex,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "parent": BASELINE,
        "kind": "CREDENTIAL_BINDING_PREFLIGHT",
        "claim_allowed": False,
        "structural_status": "FAIL" if errors else "PASS",
        "runtime_readiness": (
            "NOT_CHECKED" if runtime == "offline"
            else "BINDINGS_PRESENT_AUTH_UNVERIFIED" if ready
            else "BLOCKED_BINDING"
        ),
        "guards": list(REQUIRED_GUARDS),
        "provenance": {
            "authority": REPOSITORY,
            "source_commit": observed_commit,
            "sources": sources,
            "names_evidence": "OWNER_REPORTED_2026-09-14_NOT_SETTINGS_API_READBACK",
            "hash_scope": "current local source bytes; commit alone does not attest a clean tree",
        },
        "context": {
            "runtime_requested": runtime,
            "runtime_identity_attested": False,
            "scope": "credential binding and existing seven-guard matrix preflight",
            "boundary": "binding presence != authentication != authority != scientific evidence",
        },
        "evidence": {
            "state": "LOCAL_PREFLIGHT_EXECUTED",
            "bindings": bindings,
            "checks": {"source_files_observed": len(sources), "structural_errors": errors},
            "network_requests": 0,
            "remote_mutations": 0,
            "secret_material_persisted": False,
        },
        "contradiction": {
            "state": "OPEN" if errors or binding_gaps and runtime != "offline" else "RESOLVED_MAPPING_ONLY",
            "summary": "Actions CLIMA supersedes the historical Climate secret name; Agents use a separate surface.",
            "legacy_source_ref": BASELINE + ":data/governance/RLL_CREDENTIAL_AUTHORITY_POLICY_V1.json",
            "current_findings": [*errors, *binding_gaps],
        },
        "uncertainty": {"state": "OPEN", "open_items": gaps},
        "reproduction": {
            "state": "LOCAL_PREFLIGHT_ONLY",
            "python": platform.python_version(),
            "procedure": "python -m tools.agent.rll_agent_seven_guards --runtime " + runtime,
            "comparison": "compare source hashes and check outcomes; timestamps and receipt IDs vary",
            "authentication_procedure": "run the existing read-only authority probe in the intended runtime",
        },
        "rollback": {
            "state": "READY",
            "anchor": BASELINE,
            "procedure": "revert this change commit on a work branch; preserve receipts and prior evidence",
            "executed": False,
            "external_mutation_to_undo": False,
        },
        "F_next": "Observe authentication in the intended runtime; retain a new receipt and exact source ref.",
    }
    return receipt


def write_receipt(receipt, output):
    # Content hash covers the receipt payload before adding the hash field.
    encoded = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    document = dict(receipt)
    document["payload_sha256"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(document, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=["agents", "actions", "offline"], default="offline")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-bindings", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt(args.runtime)
    output = args.output or ROOT / "artifacts/rll-agent-authority" / (receipt["receipt_id"] + ".json")
    try:
        write_receipt(receipt, output)
    except FileExistsError:
        print(json.dumps({"status": "RECEIPT_EXISTS_USE_NEW_PATH", "claim_allowed": False}))
        return 2
    print(json.dumps({
        "receipt_id": receipt["receipt_id"],
        "structural_status": receipt["structural_status"],
        "runtime_readiness": receipt["runtime_readiness"],
        "claim_allowed": False,
    }))
    if receipt["structural_status"] != "PASS":
        return 1
    if args.require_bindings and receipt["runtime_readiness"] != "BINDINGS_PRESENT_AUTH_UNVERIFIED":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
