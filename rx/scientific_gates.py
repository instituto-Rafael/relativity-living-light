"""Fail-closed bridge from Rx Execution Fabric to SCI_GATE:G0..G11.

This module builds an evidence dependency graph only. It never executes arbitrary
commands named by JSON/YAML and never promotes a scientific gate from file
presence alone.
"""
from __future__ import annotations

from pathlib import Path

from .kernel import load_json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data/contracts/rll_scientific_validation_orchestrator.v1.json"
EXECUTOR_REGISTRY_PATH = ROOT / "data/governance/RLL_SCIENTIFIC_GATE_EXECUTOR_REGISTRY_V1.json"
NAMESPACE_PATH = ROOT / "data/governance/RLL_GATE_NAMESPACE_REGISTRY_V1.json"


def _qualified(gate_id):
    return "SCI_GATE:" + str(gate_id)


def build_scientific_gate_graph():
    contract = load_json(CONTRACT_PATH)
    executors = load_json(EXECUTOR_REGISTRY_PATH)
    namespaces = load_json(NAMESPACE_PATH)

    if contract.get("schema") != "rll.scientific_validation_orchestrator.v1":
        raise ValueError("unexpected scientific validation contract")
    if executors.get("schema") != "rll.scientific_gate_executor_registry.v1":
        raise ValueError("unexpected scientific gate executor registry")
    if contract.get("claim_allowed") is not False or executors.get("claim_allowed") is not False:
        raise ValueError("scientific gate bridge must remain claim_allowed=false")

    science_ids = (namespaces.get("namespaces", {}).get("SCI_GATE", {}) or {}).get("ids", {})
    declared = contract.get("gates", [])
    if not isinstance(declared, list):
        raise ValueError("scientific gates must be a list")
    declared_ids = [str(row.get("id", "")) for row in declared]
    if set(declared_ids) != set(science_ids):
        raise ValueError("SCI_GATE namespace and scientific contract disagree")

    gate_map = {str(row["id"]): row for row in declared}
    executor_map = executors.get("gates", {})
    if set(executor_map) != set(gate_map):
        raise ValueError("executor registry must cover every SCI_GATE exactly once")

    nodes = []
    for gate_id in declared_ids:
        gate = gate_map[gate_id]
        entry = executor_map[gate_id]
        requires = [str(x) for x in gate.get("requires", [])]
        unknown = [dep for dep in requires if dep not in gate_map]
        if unknown:
            raise ValueError("%s has unknown prerequisites %s" % (gate_id, unknown))

        executor_paths = []
        for path in entry.get("executors", []):
            resolved = ROOT / str(path)
            executor_paths.append({
                "path": str(path),
                "present": resolved.is_file(),
            })

        output_presence = []
        for output in gate.get("must_produce", []):
            # must_produce entries are semantic artifact names, not guessed paths.
            output_presence.append({
                "artifact_id": str(output),
                "state": "TOKEN_VAZIO_UNTIL_RECEIPT_BINDING",
            })

        executor_state = str(entry.get("executor_state", "TOKEN_VAZIO_EXECUTOR"))
        all_executor_paths_present = all(row["present"] for row in executor_paths)
        mapping_state = (
            "MAPPED_PARTIAL_OR_BLOCKING"
            if executor_paths and all_executor_paths_present
            else "TOKEN_VAZIO_EXECUTOR"
            if not executor_paths
            else "BROKEN_EXECUTOR_MAPPING"
        )

        nodes.append({
            "id": gate_id,
            "qualified_id": _qualified(gate_id),
            "name": gate.get("name"),
            "priority": gate.get("priority"),
            "requires": requires,
            "qualified_requires": [_qualified(dep) for dep in requires],
            "must_produce": output_presence,
            "pass_when": gate.get("pass_when", []),
            "stop_when": gate.get("stop_when", []),
            "executor_state": executor_state,
            "executor_paths": executor_paths,
            "mapping_state": mapping_state,
            "evidence_state": "TOKEN_VAZIO_UNTIL_GATE_RECEIPT",
            "claim_allowed": False,
        })

    return {
        "schema": "rll.rx.scientific_gate_execution_graph.v1",
        "source_contract_status": contract.get("status"),
        "source_execution_effect": contract.get("execution_effect"),
        "namespace": "SCI_GATE",
        "nodes": nodes,
        "gate_count": len(nodes),
        "arbitrary_command_execution": False,
        "claim_allowed": False,
        "boundary": (
            "This graph wires declared scientific dependencies and authorized internal "
            "executor mappings. A mapped executor is not gate closure; closure requires "
            "the gate-specific evidence receipt and pass criteria."
        ),
    }
