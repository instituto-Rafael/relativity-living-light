#!/usr/bin/env python3
"""Offline RLL LATIN evidence boundary validation; no physical/cosmological inference."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/governance/latin-evidence-bridge.v1.json"
OUT = ROOT / "results/latin/latin-bridge-receipt.v1.json"

# Immutable source-locator contract for this bounded candidate bridge.
PRODUCERS = {
    "graph": ("rafaelmeloreisnovo/RafPolimata", "research/LATIN/seed.v1.json", "555_20_latin_graph.yml"),
    "governance": ("rafaelmeloreisnovo/RafGitTools", "contracts/latin/latin-authority.v1.json", "START.yml"),
}
RELATIONS = {"analogy_only", "candidate_semantic_link", "requires_human_translation_profile"}
FORBIDDEN = {
    "REAL_COSMOLOGY_VALIDATION", "SCIENTIFIC_CONFIRMATION", "PROVED_ISOMORPHISM",
    "CULTURAL_TRANSLATION_EQUIVALENCE", "LOWFALA_DEVICE_RUNTIME",
    "PROVIDER_ADMIN_ENFORCEMENT",
}
GATES = {
    "graph_artifact_exact_head", "governance_policy_exact_head", "human_approval",
    "provider_server_rule_readback", "lowfala_ir_abi_parity",
    "independent_rll_falsifier", "copyright_translation_edition",
    "rll_pr1076_independent_validation", "privacy_legal_review",
}
SECRETS = {
    "GITPAT": "RLL_MANUAL_READ_ASSURANCE_ONLY",
    "CLIMA": "UNRELATED_CLIMATE_GATE",
    "PAT_ENV": "RafGitTools_MANUAL_SEPARATE_LANE",
    "K_SECRETS": "TOKEN_VAZIO_NO_VERIFIED_PROVIDER_INSTALLATION",
}
REPLAY = (
    "python3 -m unittest discover -s tests/latin -p 'test_*.py' -v"
    " && python3 scripts/latin/validate_latin_evidence_bridge.py"
)

def _exact_set(items, expected):
    return isinstance(items, list) and len(items) == len(expected) and set(
        v for v in items if isinstance(v, str)
    ) == expected

def validate(x):
    if not isinstance(x, dict):
        raise ValueError("invalid boundary type")
    if (x.get("schema") != "rll.latin-evidence-bridge.v1"
            or x.get("repo") != "instituto-Rafael/relativity-living-light"):
        raise ValueError("invalid evidence authority")
    if x.get("owner_role") != "SCIENTIFIC_CONSUMER_NOT_AUTHORITATIVE_FOR_LATIN_COMPILE":
        raise ValueError("compiler owner override")
    if x.get("source_class") != "ORIGINAL_METADATA_HYPOTHESIS_ONLY":
        raise ValueError("unsupported source class")
    if not _exact_set(x.get("admissible_relation_types"), RELATIONS):
        raise ValueError("untrusted relation class")
    if not _exact_set(x.get("forbidden_claims"), FORBIDDEN):
        raise ValueError("missing claim prohibition")
    sources = x.get("source_producers")
    if not isinstance(sources, dict) or set(sources) != set(PRODUCERS):
        raise ValueError("producer set mismatch")
    for name, expected in PRODUCERS.items():
        src = sources[name]
        if not isinstance(src, dict) or set(src) != {"repo", "commit", "path", "workflow"}:
            raise ValueError("producer locator shape: " + name)
        repo, path, workflow = expected
        commit = src["commit"]
        if (src["repo"], src["path"], src["workflow"]) != (repo, path, workflow):
            raise ValueError("producer locator changed: " + name)
        if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None or int(commit, 16) == 0:
            raise ValueError("producer missing/non-resolving commit: " + name)
    gates = x.get("outstanding_gates")
    if not isinstance(gates, dict) or not GATES.issubset(gates):
        raise ValueError("missing gate")
    if any(not isinstance(state, str) or state.upper() in {"PASS", "SUCCESS", "APPROVED"} for state in gates.values()):
        raise ValueError("unproven gate promotion")
    if gates["independent_rll_falsifier"] != "NOT_RUN":
        raise ValueError("science falsifier was not executed")
    s = x.get("secrets_boundary")
    if not isinstance(s, dict):
        raise ValueError("missing credential boundary")
    for name, expected in SECRETS.items():
        if s.get(name) != expected:
            raise ValueError("credential boundary changed: " + name)
    for name in ("secret_values_used", "secret_fallback", "administration_called"):
        if s.get(name) is not False:
            raise ValueError("credential misuse: " + name)
    g = x.get("governance")
    if not isinstance(g, dict):
        raise ValueError("missing governance")
    for name in ("no_network", "no_admin", "no_code_mutation", "no_training"):
        if g.get(name) is not True:
            raise ValueError("unsafe runtime permission: " + name)
    for name in ("auto_dispatch", "auto_merge", "claim_allowed"):
        if g.get(name) is not False:
            raise ValueError("automatic promotion: " + name)
    if x.get("claim_allowed") is not False:
        raise ValueError("scientific claim not allowed")
    if x.get("replay") != REPLAY:
        raise ValueError("replay must fail fast before receipt")
    return {
        "schema": "rll.latin-bridge-receipt.v1",
        "state": "PASS_EVIDENCE_BOUNDARY_STRUCTURE_ONLY",
        "physical_runtime": "NOT_RUN",
        "scientific_validation": "NOT_RUN",
        "provider_admin": "NOT_RUN",
        "claim_allowed": False,
    }

def main():
    raw = SOURCE.read_bytes()
    receipt = validate(json.loads(raw))
    receipt["contract_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))

if __name__ == "__main__":
    main()
