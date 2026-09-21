#!/usr/bin/env python3
"""Validate the recursive RLL manifold index scaffold.

This validator checks navigation/reconstruction integrity only.  A valid
manifold scaffold never promotes a scientific claim.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data/navigation/rll_manifold_index_scaffolding_v1.yml"
DEFAULT_SCHEMA = ROOT / "schemas/rll_manifold_index_scaffolding_v1.schema.json"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return value


def _structural_order(nodes: dict[str, dict[str, Any]], root_id: str) -> tuple[list[str], list[str]]:
    order: list[str] = []
    errors: list[str] = []
    state: dict[str, int] = {}

    def visit(node_id: str, trail: list[str]) -> None:
        marker = state.get(node_id, 0)
        if marker == 1:
            errors.append("structural_cycle:" + "->".join(trail + [node_id]))
            return
        if marker == 2:
            return
        if node_id not in nodes:
            errors.append(f"missing_structural_node:{node_id}")
            return

        state[node_id] = 1
        order.append(node_id)
        node = nodes[node_id]
        children = node.get("structural_children", [])
        if not isinstance(children, list):
            errors.append(f"invalid_children_type:{node_id}")
            children = []
        for child in children:
            if not isinstance(child, str):
                errors.append(f"invalid_child_ref:{node_id}:{child!r}")
                continue
            visit(child, trail + [node_id])
        state[node_id] = 2

    visit(root_id, [])
    return order, errors


def validate_manifest(
    manifest: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []

    validator = Draft202012Validator(schema)
    for failure in sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path)):
        location = "/".join(str(part) for part in failure.absolute_path) or "$"
        errors.append(f"schema:{location}:{failure.message}")

    if manifest.get("claim_allowed") is not False:
        errors.append("claim_boundary:claim_allowed_must_be_false")

    root_id = manifest.get("root_id")
    nodes = manifest.get("nodes", {})
    relations = manifest.get("relations", {})

    if not isinstance(nodes, dict):
        nodes = {}
        errors.append("nodes:not_mapping")
    if not isinstance(relations, dict):
        relations = {}
        errors.append("relations:not_mapping")

    if not isinstance(root_id, str) or root_id not in nodes:
        errors.append(f"root:unresolved:{root_id}")
        structural_order: list[str] = []
    else:
        root_parent = nodes[root_id].get("primary_parent")
        if root_parent is not None:
            errors.append(f"root:primary_parent_must_be_null:{root_id}")
        structural_order, cycle_errors = _structural_order(nodes, root_id)
        errors.extend(cycle_errors)

    declared_parents: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for parent_id, node in nodes.items():
        children = node.get("structural_children", [])
        if not isinstance(children, list):
            continue
        seen: set[str] = set()
        for child_id in children:
            if not isinstance(child_id, str):
                continue
            if child_id in seen:
                errors.append(f"structure:duplicate_child:{parent_id}:{child_id}")
            seen.add(child_id)
            if child_id not in nodes:
                errors.append(f"structure:unresolved_child:{parent_id}:{child_id}")
                continue
            declared_parents.setdefault(child_id, []).append(parent_id)

    for node_id, node in nodes.items():
        parent = node.get("primary_parent")
        if node_id == root_id:
            continue
        if not isinstance(parent, str) or not parent:
            errors.append(f"structure:missing_primary_parent:{node_id}")
        elif parent not in nodes:
            errors.append(f"structure:unresolved_primary_parent:{node_id}:{parent}")
        elif node_id not in nodes[parent].get("structural_children", []):
            errors.append(f"structure:parent_child_asymmetry:{node_id}:{parent}")

        parents = declared_parents.get(node_id, [])
        if len(parents) != 1:
            errors.append(f"structure:expected_one_structural_parent:{node_id}:{parents}")

        summaries = node.get("summaries", {})
        if not isinstance(summaries, dict) or "SIGMA0" not in summaries or "SIGMA1" not in summaries:
            errors.append(f"summary:missing_sigma0_or_sigma1:{node_id}")

        source_refs = node.get("source_refs", [])
        index_refs = node.get("index_refs", [])
        if not source_refs and not index_refs:
            errors.append(f"provenance:no_source_or_index_ref:{node_id}")

        if node.get("claim_allowed") is True:
            errors.append(f"claim_boundary:node_claim_true:{node_id}")

    allowed_relations: set[str] = set()
    relation_types = manifest.get("relation_types", {})
    if isinstance(relation_types, dict):
        for family in relation_types.values():
            if isinstance(family, list):
                allowed_relations.update(str(value) for value in family)

    unresolved_edges: list[str] = []
    for edge_id, edge in relations.items():
        if not isinstance(edge, dict):
            errors.append(f"relation:not_mapping:{edge_id}")
            continue
        source = edge.get("source")
        target = edge.get("target")
        if source not in nodes:
            errors.append(f"relation:unresolved_source:{edge_id}:{source}")
            unresolved_edges.append(edge_id)
        if target not in nodes:
            errors.append(f"relation:unresolved_target:{edge_id}:{target}")
            unresolved_edges.append(edge_id)
        relation = edge.get("relation")
        if allowed_relations and relation not in allowed_relations:
            errors.append(f"relation:unknown_type:{edge_id}:{relation}")
        if edge.get("claim_allowed") is True:
            errors.append(f"claim_boundary:relation_claim_true:{edge_id}")

    unreachable = sorted(set(nodes) - set(structural_order))
    if root_id in nodes and unreachable:
        errors.append("structure:unreachable_nodes:" + ",".join(unreachable))

    pyramid = manifest.get("summary_pyramid", {})
    summary_levels = set(pyramid) if isinstance(pyramid, dict) else set()
    recipes = manifest.get("reconstruction_examples", [])
    if not isinstance(recipes, list):
        recipes = []
    for recipe in recipes:
        if not isinstance(recipe, dict):
            errors.append("recipe:not_mapping")
            continue
        rid = recipe.get("recipe_id", "TOKEN_VAZIO")
        if recipe.get("root_node") not in nodes:
            errors.append(f"recipe:unresolved_root:{rid}:{recipe.get('root_node')}")
        if recipe.get("summary_level") not in summary_levels:
            errors.append(f"recipe:unknown_summary_level:{rid}:{recipe.get('summary_level')}")

    overlays = manifest.get("overlays", [])
    if not isinstance(overlays, list):
        overlays = []
    overlay_ids: set[str] = set()
    for overlay in overlays:
        if not isinstance(overlay, dict):
            errors.append("overlay:not_mapping")
            continue
        oid = overlay.get("overlay_id")
        if not isinstance(oid, str) or not oid:
            errors.append("overlay:missing_id")
            continue
        if oid in overlay_ids:
            errors.append(f"overlay:duplicate_id:{oid}")
        overlay_ids.add(oid)
        if not overlay.get("base_ref"):
            errors.append(f"overlay:missing_base_ref:{oid}")

    summary_counts = {
        level: sum(
            1
            for node in nodes.values()
            if isinstance(node, dict)
            and isinstance(node.get("summaries"), dict)
            and level in node["summaries"]
        )
        for level in sorted(summary_levels)
    }

    return {
        "schema": "rll.manifold_index_validation_receipt.v1",
        "valid": not errors,
        "claim_allowed": False,
        "root_id": root_id,
        "resolved_nodes": len(structural_order),
        "declared_nodes": len(nodes),
        "resolved_edges": max(0, len(relations) - len(set(unresolved_edges))),
        "declared_edges": len(relations),
        "unresolved_nodes": unreachable,
        "unresolved_edges": sorted(set(unresolved_edges)),
        "structural_order": structural_order,
        "summary_coverage": summary_counts,
        "overlay_count": len(overlays),
        "errors": errors,
    }


def run(manifest_path: Path, schema_path: Path, output: Path | None) -> int:
    manifest = load_yaml(manifest_path)
    schema = load_json(schema_path)
    receipt = validate_manifest(manifest, schema)

    encoded = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if receipt["valid"] else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    return run(args.manifest, args.schema, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
