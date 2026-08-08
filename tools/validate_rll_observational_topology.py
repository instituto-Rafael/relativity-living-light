#!/usr/bin/env python3
"""Fail-closed validation for the append-only RLL observational topology."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = ROOT / "data/governance/RLL_OBSERVATIONAL_TOPOLOGY_20260808_V1.json"
SCHEMA = ROOT / "schemas/rll_observational_topology.v1.schema.json"
DEFAULT_OUTPUT = ROOT / "artifacts/governance/RLL_OBSERVATIONAL_TOPOLOGY_VALIDATION.json"

RECONCILER = "data/governance/RLL_MODERN_VALIDATION_RECONCILIATION_20260808_V2.json"
REQUIRED_NODE_IDS = frozenset(
    {
        "MECH-RLL-LINEAR-PERTURBATION-CLOSURE",
        "MECH-COMMON-LIKELIHOOD-CONTRACT",
        "OBS-BAO-DESI-DR2",
        "OBS-SN-PANTHEON-PLUS",
        "OBS-H0-SHOES",
        "OBS-HZ-COSMIC-CHRONOMETERS",
        "OBS-GROWTH-FSIGMA8",
        "OBS-LSS-DES-Y6-3X2PT",
        "OBS-CMB-PLANCK-PR4-TTTEEE",
        "OBS-CMB-ACT-DR6-TTTEEE",
        "OBS-CMB-LENSING-ACT-PLANCK-SPT",
        "OBS-CMB-SPT3G-D1-TTTEEE",
        "OBS-DESI-DR2-LYA-FULLSHAPE",
        "OBS-CMB-BMODES-MAGNETOOPTICAL",
        "OBS-ADVERSARY-FAIRNESS",
        "OBS-FRB-CHIME-CAT2",
        "OBS-RM-POLARIZATION",
    }
)
ALLOWED_STATES = frozenset(
    {
        "MATERIALIZED",
        "VERIFIED_LIMITED",
        "OPEN_INTERNAL",
        "OPEN_EXTERNAL",
        "BLOCKED_DEPENDENCY",
        "INVALIDATED",
        "TOKEN_VAZIO",
    }
)
ALLOWED_BINDING_MODES = frozenset(
    {
        "BOUND_CURRENT_TOKEN",
        "HISTORICAL_CHAIN_TERMINAL",
        "UNBOUND_TOKEN_VAZIO",
        "MULTI_SOURCE_GAP",
    }
)
NODE_REQUIRED = frozenset(
    {
        "id",
        "kind",
        "domain",
        "observable",
        "state",
        "priority",
        "observation_class",
        "ready_for_joint_inference",
        "source_status",
        "current_evidence",
        "token_binding",
        "required_gates",
        "dependencies",
        "claim_boundary",
        "next_action",
    }
)


@dataclass(frozen=True)
class ValidationResult:
    decision: str
    claim_allowed: bool
    publication_ready: bool
    node_count: int
    invalidated_nodes: list[str]
    topology_only_tokens: list[str]
    errors: list[str]


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _repository_file_exists(root: Path, value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    text = value.strip()
    if "://" in text:
        return True
    candidate = root / text
    return candidate.is_file()


def _node_lookup(nodes: list[Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for candidate in nodes:
        if isinstance(candidate, dict) and isinstance(candidate.get("id"), str):
            lookup[candidate["id"]] = candidate
    return lookup


def _has_cycle(node_ids: set[str], edges: list[dict[str, Any]]) -> bool:
    successors: dict[str, set[str]] = defaultdict(set)
    indegree = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        if source in node_ids and target in node_ids and target not in successors[source]:
            successors[source].add(target)
            indegree[target] += 1

    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for target in sorted(successors[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited != len(node_ids)


def validate(root: Path = ROOT, path: Path | None = None) -> ValidationResult:
    topology_path = Path(path) if path is not None else root / TOPOLOGY.relative_to(ROOT)
    errors: list[str] = []

    if not SCHEMA.is_file():
        errors.append(f"schema missing: {SCHEMA.relative_to(ROOT)}")
    if not topology_path.is_file():
        errors.append(f"topology missing: {topology_path}")
        return ValidationResult(
            decision="BLOCKED",
            claim_allowed=False,
            publication_ready=False,
            node_count=0,
            invalidated_nodes=[],
            topology_only_tokens=[],
            errors=errors,
        )

    try:
        data = _read_json(topology_path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read topology: {exc}")
        return ValidationResult(
            decision="BLOCKED",
            claim_allowed=False,
            publication_ready=False,
            node_count=0,
            invalidated_nodes=[],
            topology_only_tokens=[],
            errors=errors,
        )

    if not isinstance(data, dict):
        errors.append("topology root must be an object")
        return ValidationResult(
            decision="BLOCKED",
            claim_allowed=False,
            publication_ready=False,
            node_count=0,
            invalidated_nodes=[],
            topology_only_tokens=[],
            errors=errors,
        )

    root_required = {
        "schema",
        "version",
        "generated_at",
        "repository",
        "source_main_commit",
        "append_only",
        "claim_allowed",
        "publication_ready",
        "authority_order",
        "state_machine",
        "invariants",
        "nodes",
        "topological_edges",
        "promotion_gate",
    }
    missing_root = sorted(root_required - set(data))
    if missing_root:
        errors.append(f"missing root fields: {', '.join(missing_root)}")
    if data.get("schema") != "rll.observational_topology.v1":
        errors.append("schema identifier must be rll.observational_topology.v1")
    if data.get("version") != "20260808.v1":
        errors.append("version must be 20260808.v1")
    if data.get("repository") != "instituto-Rafael/relativity-living-light":
        errors.append("repository identity mismatch")
    if not isinstance(data.get("source_main_commit"), str) or not re.fullmatch(
        r"[0-9a-f]{40}", data.get("source_main_commit", "")
    ):
        errors.append("source_main_commit must be a 40-character lowercase SHA")
    if data.get("append_only") is not True:
        errors.append("append_only must remain true")
    if data.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if data.get("publication_ready") is not False:
        errors.append("publication_ready must remain false")

    try:
        datetime.fromisoformat(str(data.get("generated_at", "")).replace("Z", "+00:00"))
    except ValueError:
        errors.append("generated_at must be an ISO-8601 timestamp")

    authority_order = data.get("authority_order")
    if not isinstance(authority_order, list) or len(authority_order) < 3:
        errors.append("authority_order must contain at least three sources")
    else:
        if authority_order[0] != RECONCILER:
            errors.append("authoritative reconciler must be first in authority_order")
        for source in authority_order:
            if not _repository_file_exists(root, source):
                errors.append(f"authority source missing: {source}")

    state_machine = data.get("state_machine")
    if not isinstance(state_machine, dict):
        errors.append("state_machine must be an object")
    else:
        if state_machine.get("fail_closed_default") != "TOKEN_VAZIO":
            errors.append("state_machine fail_closed_default must be TOKEN_VAZIO")
        declared_states = state_machine.get("states")
        if not isinstance(declared_states, list) or set(declared_states) != ALLOWED_STATES:
            errors.append("state_machine states must declare the complete allowed state set")

    invariants = data.get("invariants")
    if not isinstance(invariants, list) or len(invariants) < 4 or not all(
        _is_nonempty_string(item) for item in invariants
    ):
        errors.append("invariants must contain at least four nonempty statements")

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        errors.append("nodes must be an array")
        nodes = []
    node_ids: list[str] = []
    invalidated_nodes: list[str] = []
    topology_only_tokens: list[str] = []

    for position, item in enumerate(nodes):
        prefix = f"nodes[{position}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(NODE_REQUIRED - set(item))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue
        node_id = item.get("id")
        if not isinstance(node_id, str) or not re.fullmatch(r"(OBS|MECH)-[A-Z0-9-]+", node_id):
            errors.append(f"{prefix} has invalid id")
            continue
        node_ids.append(node_id)
        if item.get("kind") not in {"observation", "mechanism"}:
            errors.append(f"{node_id} has invalid kind")
        if item.get("state") not in ALLOWED_STATES:
            errors.append(f"{node_id} has invalid state")
        if item.get("priority") not in {"P0", "P1", "P2"}:
            errors.append(f"{node_id} has invalid priority")
        if item.get("ready_for_joint_inference") is not False:
            errors.append(f"{node_id} must remain unavailable for joint inference")
        for field in ("domain", "observable", "observation_class", "source_status", "claim_boundary", "next_action"):
            if not _is_nonempty_string(item.get(field)):
                errors.append(f"{node_id} has empty {field}")

        evidence_list = item.get("current_evidence")
        if not isinstance(evidence_list, list) or not evidence_list:
            errors.append(f"{node_id} must cite current_evidence")
        else:
            for evidence_index, entry in enumerate(evidence_list):
                if not isinstance(entry, dict):
                    errors.append(f"{node_id} evidence[{evidence_index}] must be an object")
                    continue
                for field in ("path", "status", "note"):
                    if not _is_nonempty_string(entry.get(field)):
                        errors.append(f"{node_id} evidence[{evidence_index}] has empty {field}")
                if not _repository_file_exists(root, entry.get("path")):
                    errors.append(f"{node_id} evidence path missing: {entry.get('path')}")

        binding = item.get("token_binding")
        if not isinstance(binding, dict):
            errors.append(f"{node_id} token_binding must be an object")
        else:
            mode = binding.get("mode")
            tokens = binding.get("tokens")
            queue_effect = binding.get("queue_effect")
            if mode not in ALLOWED_BINDING_MODES:
                errors.append(f"{node_id} has invalid token binding mode")
            if not isinstance(tokens, list) or not all(
                isinstance(token, str) and token.startswith("TOKEN_VAZIO_") for token in tokens
            ):
                errors.append(f"{node_id} token_binding tokens must be TOKEN_VAZIO identifiers")
            if mode == "UNBOUND_TOKEN_VAZIO":
                if queue_effect != "topology_only" or not tokens:
                    errors.append(f"{node_id} unbound token must be nonempty and topology_only")
                else:
                    topology_only_tokens.extend(tokens)
            elif mode == "HISTORICAL_CHAIN_TERMINAL":
                if queue_effect != "historical_only" or tokens:
                    errors.append(f"{node_id} historical binding must have no active tokens")
            elif mode == "BOUND_CURRENT_TOKEN":
                if queue_effect != "existing_queue" or not tokens:
                    errors.append(f"{node_id} current binding must have nonempty existing_queue tokens")
            elif mode == "MULTI_SOURCE_GAP":
                if queue_effect not in {"existing_queue", "mixed", "topology_only"} or not tokens:
                    errors.append(f"{node_id} multi-source binding must have an allowed queue effect and tokens")

        gates = item.get("required_gates")
        if not isinstance(gates, list) or not gates or not all(_is_nonempty_string(gate) for gate in gates):
            errors.append(f"{node_id} must provide nonempty required_gates")
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list) or not all(isinstance(dep, str) for dep in dependencies):
            errors.append(f"{node_id} dependencies must be a string array")

        contradiction = item.get("contradiction")
        if item.get("state") == "INVALIDATED":
            invalidated_nodes.append(node_id)
            if not isinstance(contradiction, dict):
                errors.append(f"INVALIDATED node {node_id} requires a contradiction record")
            else:
                paths = contradiction.get("conflicting_paths")
                if not isinstance(paths, list) or len(paths) < 2 or not all(
                    _repository_file_exists(root, value) for value in paths
                ):
                    errors.append(f"INVALIDATED node {node_id} needs two existing conflicting_paths")
                for field in ("resolution_gate", "safe_interpretation"):
                    if not _is_nonempty_string(contradiction.get(field)):
                        errors.append(f"INVALIDATED node {node_id} has empty contradiction {field}")
        elif contradiction is not None:
            errors.append(f"non-invalidated node {node_id} must not carry a contradiction record")

    node_id_set = set(node_ids)
    if len(node_ids) != len(node_id_set):
        errors.append("node ids must be unique")
    missing_nodes = sorted(REQUIRED_NODE_IDS - node_id_set)
    if missing_nodes:
        errors.append(f"missing required topology nodes: {', '.join(missing_nodes)}")
    if "OBS-BAO-DESI-DR2" not in invalidated_nodes:
        errors.append("OBS-BAO-DESI-DR2 must remain INVALIDATED until authority conflict is reconciled")

    lookup = _node_lookup(nodes)
    for node_id, item in lookup.items():
        dependencies = item.get("dependencies", [])
        if isinstance(dependencies, list):
            for dependency in dependencies:
                if dependency not in node_id_set:
                    errors.append(f"{node_id} references unknown dependency {dependency}")
                if dependency == node_id:
                    errors.append(f"{node_id} cannot depend on itself")

    edges = data.get("topological_edges")
    if not isinstance(edges, list) or not edges:
        errors.append("topological_edges must be a nonempty array")
        edges = []
    edge_pairs: set[tuple[str, str]] = set()
    valid_edges: list[dict[str, Any]] = []
    for position, edge in enumerate(edges):
        prefix = f"topological_edges[{position}]"
        if not isinstance(edge, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if set(edge) != {"from", "to", "relation", "why"}:
            errors.append(f"{prefix} must contain only from, to, relation and why")
            continue
        source, target = edge.get("from"), edge.get("to")
        if source not in node_id_set or target not in node_id_set:
            errors.append(f"{prefix} references an unknown node")
            continue
        if source == target:
            errors.append(f"{prefix} cannot be a self-edge")
        if edge.get("relation") not in {"requires", "shares_likelihood_contract", "must_precede"}:
            errors.append(f"{prefix} has invalid relation")
        if not _is_nonempty_string(edge.get("why")):
            errors.append(f"{prefix} requires why")
        edge_pairs.add((source, target))
        valid_edges.append(edge)

    for node_id, item in lookup.items():
        for dependency in item.get("dependencies", []):
            if (dependency, node_id) not in edge_pairs:
                errors.append(f"{node_id} dependency {dependency} has no matching topological edge")
    if node_id_set and _has_cycle(node_id_set, valid_edges):
        errors.append("topological_edges must be acyclic")

    promotion_gate = data.get("promotion_gate")
    if not isinstance(promotion_gate, dict):
        errors.append("promotion_gate must be an object")
    else:
        if promotion_gate.get("scientific_claim_allowed") is not False:
            errors.append("promotion_gate scientific_claim_allowed must remain false")
        conditions = promotion_gate.get("required_conditions")
        if not isinstance(conditions, list) or len(conditions) < 4 or not all(
            _is_nonempty_string(condition) for condition in conditions
        ):
            errors.append("promotion_gate must enumerate at least four required_conditions")
        if not _is_nonempty_string(promotion_gate.get("safe_current_conclusion")):
            errors.append("promotion_gate requires a safe_current_conclusion")

    return ValidationResult(
        decision="PASS_FAIL_CLOSED_CONTRACT" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_ready=False,
        node_count=len(nodes),
        invalidated_nodes=sorted(invalidated_nodes),
        topology_only_tokens=sorted(set(topology_only_tokens)),
        errors=errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topology", type=Path, default=TOPOLOGY, help="Topology JSON to validate.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Receipt JSON to write.")
    args = parser.parse_args()

    result = validate(path=args.topology)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

