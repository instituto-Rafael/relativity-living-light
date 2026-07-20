from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_rll_route_forest.py"
spec = importlib.util.spec_from_file_location("route_forest", MODULE_PATH)
assert spec and spec.loader
route_forest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_forest)


def load_inputs() -> tuple[dict, list[dict]]:
    return route_forest.read_json(route_forest.BLUEPRINT), route_forest.read_events(route_forest.EVENTS)


def test_current_route_forest_compiles_with_expected_metrics() -> None:
    blueprint, events = load_inputs()
    assert route_forest.semantic_findings(blueprint, events) == []
    forest = route_forest.compile_forest(blueprint, events)
    assert forest["state"] == "STRUCTURAL_MAP_READY_ML_BLOCKED"
    assert forest["claim_allowed"] is False
    assert forest["metrics"] == {
        "region_count": 7,
        "tree_count": 4,
        "node_count": 17,
        "route_count": 13,
        "event_count": 21,
        "weighted_flow": 21,
        "orphan_count": 0,
        "cycle_count": 0,
        "max_depth": 3,
        "mean_vector_norm": 1.495802823499,
    }


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
    events.append({
        "event_id": "EVT-9991",
        "window_id": "SNAPSHOT-20260720",
        "route_id": "RT-CYCLE",
        "event_kind": "route_linked",
        "observed_at": "2026-07-20T09:20:00Z",
        "source_ref": "tools/validate_workflow_docs.py",
        "weight": 1,
    })
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


def test_unknown_event_route_is_rejected() -> None:
    blueprint, events = load_inputs()
    events.append({
        "event_id": "EVT-9992",
        "window_id": "SNAPSHOT-20260720",
        "route_id": "RT-UNKNOWN",
        "event_kind": "route_linked",
        "observed_at": "2026-07-20T09:20:00Z",
        "source_ref": "schemas/README.md",
        "weight": 1,
    })
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
    assert forest["frequency_window"]["event_count"] == 21
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
