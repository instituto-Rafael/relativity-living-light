#!/usr/bin/env python3
"""Fail-closed validator for the Ethics/License/Complexity sustainment contract.

The validator intentionally separates symbolic/authorial material from legal,
scientific and runtime evidence. It validates provenance, typed graph topology,
TOKEN_VAZIO completeness and append-only closure semantics. It does not score
truth, ethics or legal enforceability.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "governance/ethics_license_complexity_sustainment.v1.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_URGENCY = {"P0", "P1", "P2"}
EXPECTED_PARABLE = [
    "ESTATISTICA", "TOKENS", "METAFORAS", "VECTORES",
    "PALAVRA", "PROMESSA", "OMEGA_N",
]


def fail(message: str) -> None:
    raise ValueError(message)


def require_nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: expected non-empty string")
    return value


def require_false(data: dict[str, Any], key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must remain false")


def validate_receipt(receipt: Any, label: str = "closure_receipt") -> dict[str, Any]:
    if not isinstance(receipt, dict):
        fail(f"{label}: expected object")
    if receipt.get("schema") != "rll.token_vazio_closure_receipt.v1":
        fail(f"{label}.schema: invalid closure receipt schema")
    require_nonempty(receipt.get("gap_id"), f"{label}.gap_id")
    require_nonempty(receipt.get("artifact_path"), f"{label}.artifact_path")
    sha256 = require_nonempty(receipt.get("sha256"), f"{label}.sha256")
    commit_sha = require_nonempty(receipt.get("commit_sha"), f"{label}.commit_sha")
    if not HEX64.fullmatch(sha256):
        fail(f"{label}.sha256: expected lowercase SHA-256")
    if not HEX40.fullmatch(commit_sha):
        fail(f"{label}.commit_sha: expected lowercase Git SHA-1")
    if receipt.get("result") not in {"PASS", "CLOSED_BY_EVIDENCE"}:
        fail(f"{label}.result: invalid closure state")
    if receipt.get("claim_allowed") is not False:
        fail(f"{label}.claim_allowed must remain false")
    return receipt


def validate_graph(data: dict[str, Any], root: Path = ROOT) -> None:
    if data.get("schema") != "rll.ethics_license_complexity_sustainment.v1":
        fail("invalid schema")
    if data.get("append_only") is not True:
        fail("append_only must be true")
    for key in ("claim_allowed", "scientific_confirmation", "legal_effect_claim", "certification_claim"):
        require_false(data, key)
    if data.get("publication_effect") != "NONE":
        fail("publication_effect must remain NONE")

    contract = data.get("contract")
    if not isinstance(contract, dict):
        fail("contract must be an object")
    for key in ("name", "expression", "rule", "stop_rule"):
        require_nonempty(contract.get(key), f"contract.{key}")

    bindings = data.get("source_bindings")
    if not isinstance(bindings, list) or not bindings:
        fail("source_bindings must be a non-empty array")
    binding_ids: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict):
            fail("source binding must be an object")
        artifact_id = require_nonempty(binding.get("artifact_id"), "source_binding.artifact_id")
        if artifact_id in binding_ids:
            fail(f"duplicate source binding: {artifact_id}")
        binding_ids.add(artifact_id)
        path = require_nonempty(binding.get("path"), f"{artifact_id}.path")
        blob = require_nonempty(binding.get("git_blob_sha1"), f"{artifact_id}.git_blob_sha1")
        if not HEX40.fullmatch(blob):
            fail(f"{artifact_id}.git_blob_sha1: expected lowercase Git blob SHA-1")
        require_nonempty(binding.get("role"), f"{artifact_id}.role")
        require_nonempty(binding.get("epistemic_boundary"), f"{artifact_id}.epistemic_boundary")
        if not (root / path).exists():
            fail(f"{artifact_id}: bound path is missing: {path}")

    license_info = data.get("license_interoperability")
    if not isinstance(license_info, dict):
        fail("license_interoperability must be an object")
    if license_info.get("spdx_standard_identifier") is not False:
        fail("custom license must not be presented as a standard SPDX identifier")
    license_ref = require_nonempty(license_info.get("local_license_reference"), "license_interoperability.local_license_reference")
    if not license_ref.startswith("LicenseRef-"):
        fail("local custom license route must use LicenseRef-")
    if not str(license_info.get("legal_effect", "")).startswith("TOKEN_VAZIO"):
        fail("legal effect must remain TOKEN_VAZIO until qualified review")
    if license_info.get("third_party_redistribution_default") != "BLOCK_UNTIL_RIGHTS_RECORD":
        fail("third-party redistribution must fail closed when rights are unknown")

    ethics = data.get("ethics_by_design")
    if not isinstance(ethics, dict):
        fail("ethics_by_design must be an object")
    if ethics.get("Ethica8_status") != "MODEL_ANALOGICO_OPERATIONAL_DESIGN_SPACE":
        fail("Ethica[8] must remain explicitly model-analogical in this contract")
    for key in ("physical_field_status", "lyapunov_status", "metric_status"):
        if not str(ethics.get(key, "")).startswith("TOKEN_VAZIO"):
            fail(f"ethics_by_design.{key} must remain TOKEN_VAZIO until evidence closes it")
    controls = ethics.get("hard_gate_translation")
    if not isinstance(controls, list) or len(set(controls)) != len(controls) or len(controls) < 4:
        fail("hard_gate_translation must contain distinct executable governance controls")

    network = data.get("complex_network")
    if not isinstance(network, dict) or network.get("design") != "typed_directed_multigraph":
        fail("complex_network must be a typed_directed_multigraph")
    nodes = network.get("nodes")
    edges = network.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not nodes or not edges:
        fail("complex network requires non-empty nodes and edges")
    node_by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        nid = require_nonempty(node.get("id"), "node.id")
        if nid in node_by_id:
            fail(f"duplicate node id: {nid}")
        require_nonempty(node.get("type"), f"{nid}.type")
        node_by_id[nid] = node
    edge_by_id: dict[str, dict[str, Any]] = {}
    for edge in edges:
        eid = require_nonempty(edge.get("id"), "edge.id")
        if eid in edge_by_id:
            fail(f"duplicate edge id: {eid}")
        source = require_nonempty(edge.get("source"), f"{eid}.source")
        target = require_nonempty(edge.get("target"), f"{eid}.target")
        if source not in node_by_id or target not in node_by_id:
            fail(f"{eid}: dangling edge {source}->{target}")
        for key in ("relation", "provenance", "claim_boundary"):
            require_nonempty(edge.get(key), f"{eid}.{key}")
        edge_by_id[eid] = edge

    parable = data.get("parable_router")
    if not isinstance(parable, dict) or parable.get("epistemic_status") != "PARABOLA":
        fail("parable_router must remain epistemically PARABOLA")
    stages = parable.get("sequence")
    if not isinstance(stages, list):
        fail("parable_router.sequence must be an array")
    names = [stage.get("stage") for stage in stages if isinstance(stage, dict)]
    if names != EXPECTED_PARABLE:
        fail(f"parable sequence must be exactly {EXPECTED_PARABLE}")
    for stage in stages:
        require_nonempty(stage.get("operational_meaning"), f"parable.{stage.get('stage')}.operational_meaning")
    if parable.get("symbolic_phrase_status") != "PARABOLA_MOTIVACIONAL":
        fail("symbolic no-limit phrase must remain a motivational parable")
    boundary = require_nonempty(parable.get("runtime_boundary"), "parable_router.runtime_boundary").lower()
    if "limits" not in boundary or "measured" not in boundary:
        fail("runtime boundary must explicitly preserve measurable operational limits")

    tokens = data.get("open_tokens")
    if not isinstance(tokens, list):
        fail("open_tokens must be an array")
    token_ids: set[str] = set()
    for token in tokens:
        if not isinstance(token, dict):
            fail("open token must be an object")
        tid = require_nonempty(token.get("id"), "open_token.id")
        if tid in token_ids:
            fail(f"duplicate TOKEN_VAZIO id: {tid}")
        token_ids.add(tid)
        if token.get("state") != "TOKEN_VAZIO":
            fail(f"{tid}: state must be TOKEN_VAZIO")
        if token.get("urgency") not in ALLOWED_URGENCY:
            fail(f"{tid}: urgency must be P0/P1/P2")
        for key in ("domain", "cause", "evidence_needed", "falsifier", "F_next"):
            require_nonempty(token.get(key), f"{tid}.{key}")
        if token.get("closure_policy") != "STRUCTURED_RECEIPT_REQUIRED":
            fail(f"{tid}: closure must require a structured receipt")

    receipts = data.get("closure_receipts")
    if not isinstance(receipts, list):
        fail("closure_receipts must be an array")
    receipt_gap_ids: set[str] = set()
    for index, receipt in enumerate(receipts):
        validated = validate_receipt(receipt, f"closure_receipts[{index}]")
        gap_id = validated["gap_id"]
        if gap_id in receipt_gap_ids:
            fail(f"duplicate closure receipt for {gap_id}")
        receipt_gap_ids.add(gap_id)
        if gap_id in token_ids:
            fail(f"{gap_id}: cannot be simultaneously open and closed")

    rules = data.get("non_regression_rules")
    if not isinstance(rules, list) or len(rules) < 6:
        fail("non_regression_rules must be explicit")
    rule_text = "\n".join(str(item).lower() for item in rules)
    required_boundaries = {
        "append-only": ("append-only",),
        "parable": ("parable", "parabola", "parábola"),
        "licenseref": ("licenseref",),
        "truth scores": ("truth scores",),
        "operational limits": ("operational limits",),
    }
    for label, aliases in required_boundaries.items():
        if not any(alias in rule_text for alias in aliases):
            fail(f"non_regression_rules missing required boundary: {label}")


def assert_non_regression(old: dict[str, Any], new: dict[str, Any], root: Path = ROOT) -> None:
    validate_graph(old, root)
    validate_graph(new, root)

    old_bindings = {item["artifact_id"]: item for item in old["source_bindings"]}
    new_bindings = {item["artifact_id"]: item for item in new["source_bindings"]}
    old_nodes = {item["id"]: item for item in old["complex_network"]["nodes"]}
    new_nodes = {item["id"]: item for item in new["complex_network"]["nodes"]}
    old_edges = {item["id"]: item for item in old["complex_network"]["edges"]}
    new_edges = {item["id"]: item for item in new["complex_network"]["edges"]}

    for label, old_items, new_items in (
        ("source binding", old_bindings, new_bindings),
        ("node", old_nodes, new_nodes),
        ("edge", old_edges, new_edges),
    ):
        for item_id, item in old_items.items():
            if item_id not in new_items:
                fail(f"non-regression: {label} removed: {item_id}")
            if new_items[item_id] != item:
                fail(f"non-regression: historical {label} mutated: {item_id}")

    if new.get("parable_router") != old.get("parable_router"):
        fail("non-regression: parable router is versioned and cannot mutate in place")

    old_tokens = {item["id"] for item in old.get("open_tokens", [])}
    new_tokens = {item["id"] for item in new.get("open_tokens", [])}
    disappeared = old_tokens - new_tokens
    receipts = {
        receipt["gap_id"]: receipt
        for receipt in new.get("closure_receipts", [])
        if isinstance(receipt, dict)
    }
    unjustified = sorted(gap_id for gap_id in disappeared if gap_id not in receipts)
    if unjustified:
        fail(f"non-regression: TOKEN_VAZIO disappeared without receipt: {unjustified}")
    for gap_id in disappeared:
        validate_receipt(receipts[gap_id], f"closure_for.{gap_id}")


def summary(data: dict[str, Any]) -> str:
    network = data["complex_network"]
    priorities = {key: 0 for key in sorted(ALLOWED_URGENCY)}
    for token in data["open_tokens"]:
        priorities[token["urgency"]] += 1
    return (
        "PASS ethics_license_complexity_sustainment_v1 "
        f"nodes={len(network['nodes'])} edges={len(network['edges'])} "
        f"tokens={len(data['open_tokens'])} "
        + " ".join(f"{key}={priorities[key]}" for key in sorted(priorities))
        + " claim_allowed=false legal_effect_claim=false"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", nargs="?", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--previous", help="previous registry snapshot for append-only non-regression validation")
    args = parser.parse_args()
    path = Path(args.registry)
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_graph(data, ROOT)
    if args.previous:
        previous = json.loads(Path(args.previous).read_text(encoding="utf-8"))
        assert_non_regression(previous, data, ROOT)
    print(summary(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
