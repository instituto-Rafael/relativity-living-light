from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

from tools.rll_route_forest_snapshot import (
    load_effective_blueprint,
    load_effective_events,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_rll_route_forest.py"
spec = importlib.util.spec_from_file_location("route_forest", MODULE_PATH)
assert spec and spec.loader
route_forest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_forest)


def load_inputs() -> tuple[dict, list[dict]]:
    return load_effective_blueprint(), load_effective_events()


def event_for(route_id: str, event_id: str = "EVT-9999") -> dict:
    blueprint, _ = load_inputs()
    return {
        "event_id": event_id,
        "window_id": blueprint["frequency_semantics"]["window_id"],
        "route_id": route_id,
        "event_kind": "route_linked",
        "observed_at": "2026-07-31T15:15:00Z",
        "source_ref": "tools/validate_workflow_docs.py",
        "weight": 1,
    }


def test_current_route_forest_compiles_with_effective_snapshot_metrics() -> None:
    blueprint, events = load_inputs()
    assert blueprint["forest_id"] == "RLL-OMEGA-ROUTE-FOREST-20260731"
    assert blueprint["frequency_semantics"]["window_id"] == "SNAPSHOT-20260731"
    assert route_forest.semantic_findings(blueprint, events) == []
    forest = route_forest.compile_forest(blueprint, events)
    assert forest["state"] == "STRUCTURAL_MAP_READY_ML_BLOCKED"
    assert forest["claim_allowed"] is False
    assert forest["metrics"]["region_count"] == len(blueprint["regions"])
    assert forest["metrics"]["tree_count"] == len(blueprint["trees"])
    assert forest["metrics"]["node_count"] == len(blueprint["nodes"])
    assert forest["metrics"]["route_count"] == len(blueprint["routes"])
    assert forest["metrics"]["event_count"] == len(events)
    assert forest["metrics"]["weighted_flow"] == sum(event["weight"] for event in events)
    assert forest["metrics"]["orphan_count"] == 0
    assert forest["metrics"]["cycle_count"] == 0
    assert forest["metrics"]["max_depth"] == max(
        route_forest.depth(node_id, blueprint["nodes"])
        for node_id in blueprint["nodes"]
    )
    assert forest["metrics"]["mean_vector_norm"] > 0


def test_overlay_adds_audited_real_data_methodology_routes() -> None:
    blueprint, _ = load_inputs()
    expected = {
        "RT-RD-METH-INGEST",
        "RT-RD-HZ-LIKELIHOOD",
        "RT-RD-BAO-LIKELIHOOD",
        "RT-RD-GROWTH-CLAIM-GATE",
        "RT-RD-CMB-MODEL-SELECT",
    }
    assert expected.issubset(blueprint["routes"])
    assert blueprint["routes"]["RT-RD-TO-SCIENCE"]["status"] == "verified"
    assert blueprint["routes"]["RT-METH-FALSIFIER"]["status"] == "partial_resolution"


def test_cross_tree_routes_require_explicit_audited_status() -> None:
    blueprint, events = load_inputs()
    mutated = copy.deepcopy(blueprint)
    mutated["routes"]["RT-RD-TO-SCIENCE"].pop("status")
    findings = route_forest.semantic_findings(mutated, events)
    assert any("cross-tree route requires audited status" in finding for finding in findings)


def test_cross_tree_routes_restrict_relations() -> None:
    blueprint, events = load_inputs()
    mutated = copy.deepcopy(blueprint)
    mutated["routes"]["RT-RD-TO-SCIENCE"]["relation"] = "governs"
    findings = route_forest.semantic_findings(mutated, events)
    assert any("relation is not permitted for cross-tree routing" in finding for finding in findings)


def test_cycle_is_rejected() -> None:
    blueprint, events = load_inputs()
    mutated = copy.deepcopy(blueprint)
    mutated["routes"]["RT-CYCLE"] = {
        "tree": "T-GOVERNANCE",
        "source": "N-WORKFLOW-CONTRACT",
        "target": "N-GOV-ROOT",
        "relation": "routes",
        "refs": ["tools/validate_workflow_docs.py"],
    }
    events.append(event_for("RT-CYCLE", "EVT-9991"))
    findings = route_forest.semantic_findings(mutated, events)
    assert any("cyclic" in finding for finding in findings)


def test_orphan_is_rejected() -> None:
    blueprint, events = load_inputs()
    mutated = copy.deepcopy(blueprint)
    mutated["nodes"]["N-ORPHAN"] = {
        "tree": "T-SCIENCE",
        "region": "R5",
        "label": "Unlinked historical fragment",
        "kind": "gap",
        "status": "TOKEN_VAZIO",
        "scores": [1, 1, 1, 1, 1, 1, 1],
        "refs": ["data/omega_operational/rll_omega7_operational.json"],
        "parent": None,
    }
    mutated["trees"]["T-SCIENCE"]["nodes"].append("N-ORPHAN")
    findings = route_forest.semantic_findings(mutated, events)
    assert any("non-root orphans" in finding for finding in findings)


def test_parent_hierarchy_prevents_false_orphans() -> None:
    blueprint, _ = load_inputs()
    roots = {tree["root"] for tree in blueprint["trees"].values()}
    cycles, orphans = route_forest.graph_state(blueprint["nodes"], blueprint["routes"], roots)
    assert cycles == 0
    assert orphans == 0


def test_unknown_event_route_is_rejected() -> None:
    blueprint, events = load_inputs()
    events.append(event_for("RT-UNKNOWN", "EVT-9992"))
    findings = route_forest.semantic_findings(blueprint, events)
    assert any("unknown route" in finding for finding in findings)


def test_training_requires_all_twelve_gates() -> None:
    blueprint, events = load_inputs()
    mutated = copy.deepcopy(blueprint)
    mutated["trees"]["T-ML-EVOLUTION"]["training_allowed"] = True
    findings = route_forest.semantic_findings(mutated, events)
    assert any("training requires all twelve gates" in finding for finding in findings)


def test_frequency_is_event_count_not_hertz() -> None:
    blueprint, events = load_inputs()
    forest = route_forest.compile_forest(blueprint, events)
    assert forest["frequency_window"]["unit"] == "events_per_snapshot"
    assert forest["frequency_window"]["event_count"] == sum(
        event["weight"] for event in events
    )
    assert forest["frequency_window"]["event_records"] == len(events)
    assert "Hertz" in forest["boundaries"]["frequency"]
    assert all(route["frequency_unit"] == "events_per_snapshot" for route in forest["routes"])


def test_vector_delta_and_ml_readiness_are_deterministic() -> None:
    blueprint, events = load_inputs()
    forest = route_forest.compile_forest(blueprint, events)
    route = next(item for item in forest["routes"] if item["route_id"] == "RT-GOV-OMEGA7")
    assert route["vector_delta"] == [-0.25, 0.0, -0.25, 0.0, 0.0, 0.0, -0.25]
    states = {tree["tree_id"]: tree["ml_readiness"]["state"] for tree in forest["trees"]}
    assert states == {
        "T-GOVERNANCE": "NOT_APPLICABLE",
        "T-SCIENCE": "NOT_READY",
        "T-LATENTES": "FEATURE_ENGINEERING_ONLY",
        "T-ML-EVOLUTION": "FEATURE_ENGINEERING_ONLY",
        "T-REAL-DATA": "NOT_READY",
        "T-METHODOLOGY": "NOT_APPLICABLE",
    }


def test_reports_include_graphml_and_checksums(tmp_path: Path) -> None:
    blueprint, events = load_inputs()
    forest = route_forest.compile_forest(blueprint, events)
    material = route_forest.write_artifacts(forest, tmp_path)
    assert {path.name for path in material} == {
        "route_forest_report.json",
        "ROUTE_FOREST_REPORT.md",
        "rll_route_forest.graphml",
        "CHECKSUMS.sha256",
    }
    graph = (tmp_path / "rll_route_forest.graphml").read_text(encoding="utf-8")
    assert '<graph id="RLLRouteForest" edgedefault="directed">' in graph
    checksums = (tmp_path / "CHECKSUMS.sha256").read_text(encoding="utf-8")
    assert "route_forest_report.json" in checksums
    assert "rll_route_forest.graphml" in checksums
