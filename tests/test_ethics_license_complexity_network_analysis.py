import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_ethics_license_complexity_network.py"
REGISTRY = ROOT / "governance/ethics_license_complexity_sustainment.v1.json"

spec = importlib.util.spec_from_file_location("network_analysis", TOOL)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def test_network_analysis_passes_with_structural_boundaries():
    report = mod.build_report(REGISTRY, ROOT)
    assert report["state"] == "PASS_STRUCTURAL_NETWORK_ANALYSIS"
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["legal_effect_claim"] is False
    assert report["graph"]["node_count"] == 9
    assert report["graph"]["edge_count"] == 6
    assert report["invariants"]["graph_metrics_are_not_truth_scores"] is True
    assert report["F_gap"] == []


def test_critical_routes_are_explicit_and_deterministic():
    first = mod.build_report(REGISTRY, ROOT)
    second = mod.build_report(REGISTRY, ROOT)
    assert first["registry_sha256"] == second["registry_sha256"]
    assert first["graph"] == second["graph"]
    assert first["critical_routes"] == second["critical_routes"]
    assert first["critical_routes"]["TOKEN_VAZIO_to_RECEIPT"] == [
        "NODE-TOKEN-VAZIO", "NODE-RECEIPT"
    ]
    assert first["critical_routes"]["ETHICS_OPERATIONAL_to_EVIDENCE"] == [
        "NODE-ETHICS-OPERATIONAL", "NODE-EVIDENCE"
    ]


def test_graph_has_no_isolated_or_cyclic_components_in_v1():
    report = mod.build_report(REGISTRY, ROOT)
    assert report["graph"]["isolated_nodes"] == []
    assert report["graph"]["cyclic_components"] == []
    assert report["graph"]["self_loop_edge_ids"] == []


def test_structural_reachability_is_not_total_and_not_truth_score():
    report = mod.build_report(REGISTRY, ROOT)
    fraction = report["graph"]["reachability_fraction_structural_only"]
    assert 0.0 < fraction < 1.0
    assert "not truth" in report["boundary"].lower()


def test_token_receipt_route_does_not_fake_evidence_route():
    report = mod.build_report(REGISTRY, ROOT)
    # The current graph intentionally gives TOKEN_VAZIO a closure path to a
    # receipt but not a direct evidence path. A receipt records closure; it is
    # not retroactively treated as the evidence-producing node itself.
    assert report["critical_routes"]["TOKEN_VAZIO_to_RECEIPT"] is not None
    assert report["critical_routes"]["TOKEN_VAZIO_to_EVIDENCE"] is None
