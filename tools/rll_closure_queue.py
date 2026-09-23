#!/usr/bin/env python3
"""Build a deterministic, fail-closed RLL closure queue from the workstream registry."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data/governance/RLL_CLOSURE_WORKSTREAM_REGISTRY_V1.json"
DEFAULT_NAMESPACE = ROOT / "data/governance/RLL_GATE_NAMESPACE_REGISTRY_V1.json"
DEFAULT_JSON = ROOT / "results/rll_closure_queue.json"
DEFAULT_MD = ROOT / "results/rll_closure_queue.md"

TERMINAL = {"CLOSED"}
BLOCKED_PREFIXES = ("BLOCKED_", "TOKEN_VAZIO")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_registry(registry, namespace):
    if registry.get("schema") != "rll.closure_workstream_registry.v1":
        raise ValueError("unsupported closure registry schema")
    if registry.get("claim_allowed") is not False:
        raise ValueError("closure registry must set claim_allowed=false")
    if namespace.get("schema") != "rll.gate_namespace_registry.v1":
        raise ValueError("unsupported gate namespace schema")
    if namespace.get("claim_allowed") is not False:
        raise ValueError("gate namespace registry must set claim_allowed=false")

    streams = registry.get("workstreams")
    if not isinstance(streams, list) or not streams:
        raise ValueError("workstreams must be a non-empty list")

    ids = [str(row.get("id", "")) for row in streams]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("workstream ids must be non-empty and unique")
    known = set(ids)
    for row in streams:
        deps = row.get("dependencies", [])
        if not isinstance(deps, list):
            raise ValueError("%s dependencies must be a list" % row["id"])
        unknown = sorted(set(str(x) for x in deps) - known)
        if unknown:
            raise ValueError("%s has unknown dependencies: %s" % (row["id"], unknown))

    graph = {row["id"]: list(row.get("dependencies", [])) for row in streams}
    visiting = set()
    visited = set()

    def visit(node):
        if node in visiting:
            raise ValueError("dependency cycle detected at %s" % node)
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)

    spaces = namespace.get("namespaces", {})
    if set(spaces) != {"REGIME", "SCI_GATE"}:
        raise ValueError("gate namespaces must be exactly REGIME and SCI_GATE")
    regime_ids = (spaces["REGIME"] or {}).get("ids", {})
    science_ids = (spaces["SCI_GATE"] or {}).get("ids", {})
    if set(regime_ids) != {"G%d" % i for i in range(7)}:
        raise ValueError("REGIME namespace must expose exactly G0..G6")
    if set(science_ids) != {"G%d" % i for i in range(12)}:
        raise ValueError("SCI_GATE namespace must expose exactly G0..G11")
    return streams


def topological_order(streams):
    rows = {row["id"]: row for row in streams}
    done = set()
    order = []
    while len(done) < len(rows):
        progressed = False
        for key in sorted(rows):
            if key in done:
                continue
            deps = rows[key].get("dependencies", [])
            if all(dep in done for dep in deps):
                order.append(key)
                done.add(key)
                progressed = True
        if not progressed:
            raise ValueError("dependency graph could not be ordered")
    return order


def effective_state(row, by_id):
    state = str(row.get("current_state", "TOKEN_VAZIO"))
    if state in TERMINAL:
        return "CLOSED"
    if state.startswith(BLOCKED_PREFIXES):
        return state
    unresolved = [
        dep for dep in row.get("dependencies", [])
        if str(by_id[dep].get("current_state")) not in TERMINAL
    ]
    if unresolved:
        return "WAIT_DEPENDENCY"
    if state in {"READY_ENGINEERING", "OPEN_ENGINEERING"}:
        return "READY"
    return state


def evidence_status(row):
    details = []
    for value in row.get("required_outputs", []):
        path = ROOT / str(value)
        details.append({
            "path": str(value),
            "present": path.exists(),
            "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
        })
    return details


def build(registry_path=DEFAULT_REGISTRY, namespace_path=DEFAULT_NAMESPACE):
    registry = load_json(registry_path)
    namespace = load_json(namespace_path)
    streams = validate_registry(registry, namespace)
    by_id = {row["id"]: row for row in streams}
    order = topological_order(streams)

    queue = []
    counts = {}
    for workstream_id in order:
        row = by_id[workstream_id]
        state = effective_state(row, by_id)
        counts[state] = counts.get(state, 0) + 1
        queue.append({
            "id": workstream_id,
            "priority": row.get("priority"),
            "name": row.get("name"),
            "discipline": row.get("discipline", []),
            "declared_state": row.get("current_state"),
            "effective_state": state,
            "dependencies": row.get("dependencies", []),
            "closes_tokens": row.get("closes_tokens", []),
            "required_outputs": evidence_status(row),
            "next_task": (row.get("tasks") or ["TOKEN_VAZIO"])[0],
            "claim_allowed": False,
        })

    return {
        "schema": "rll.closure_queue.v1",
        "repo_ref": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_REF"),
        "registry_sha256": sha256_file(registry_path),
        "namespace_registry_sha256": sha256_file(namespace_path),
        "workstream_count": len(queue),
        "state_counts": counts,
        "queue": queue,
        "namespace_contract": {
            "regime": "REGIME:G0..G6",
            "scientific_gate": "SCI_GATE:G0..G11",
        },
        "claim_allowed": False,
        "boundary": "Queue state is operational planning metadata, not scientific evidence or claim promotion.",
    }


def write_outputs(payload, json_path=DEFAULT_JSON, md_path=DEFAULT_MD):
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# RLL Closure Queue V1",
        "",
        "Claim allowed: **false**.",
        "",
        "Qualified namespaces: REGIME:G0..G6 and SCI_GATE:G0..G11.",
        "",
        "## Queue",
        "",
        "| ID | Priority | Effective state | Discipline | First next task |",
        "|---|---|---|---|---|",
    ]
    for row in payload["queue"]:
        disciplines = ", ".join(row["discipline"])
        task = str(row["next_task"]).replace("|", "/")
        lines.append("| %s | %s | %s | %s | %s |" % (
            row["id"], row["priority"], row["effective_state"], disciplines, task
        ))
    lines += ["", "## Boundary", "", payload["boundary"]]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY.relative_to(ROOT)))
    parser.add_argument("--namespace-registry", default=str(DEFAULT_NAMESPACE.relative_to(ROOT)))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    payload = build(ROOT / args.registry, ROOT / args.namespace_registry)
    if args.write:
        write_outputs(payload)
    print(json.dumps({
        "schema": payload["schema"],
        "workstream_count": payload["workstream_count"],
        "state_counts": payload["state_counts"],
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
