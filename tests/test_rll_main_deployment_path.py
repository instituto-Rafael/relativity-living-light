from __future__ import annotations
import json
from pathlib import Path
from tools.rll_main_deployment_path import validate

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance/RLL_MAIN_DEPLOYMENT_PATH_20260925_V1.json"

def payload():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def test_registry_is_valid_and_fail_closed():
    p = payload()
    r = validate(p)
    assert r["valid"], r["errors"]
    assert p["claim_allowed"] is False
    assert r["main_protected_deployment_allowed"] is False
    assert r["main_blocker"] == "TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT"

def test_exact_current_open_denominator_and_priorities():
    r = validate(payload())
    assert r["open_count"] == 12
    assert r["priority_counts"] == {"P0": 5, "P1": 5, "P2": 2}

def test_resolved_facts_are_not_reopened():
    p = payload()
    opened = {x["token"] for x in p["work_items"]}
    resolved = {x["token"] for x in p["resolved_facts"]}
    assert not opened & resolved
    assert "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE" in resolved
    assert "TOKEN_VAZIO_DIVERGED_OR_DESCENDANT_REF_SEMANTIC_REVIEW" in resolved
    assert "TOKEN_VAZIO_EXTERNAL_SETTINGS" in resolved

def test_main_topology_has_no_feature_direct_to_main():
    topo = [(x["from"], x["to"]) for x in payload()["promotion_topology"]]
    assert topo[-1] == ("rll/release", "main")
    assert all(not (src.startswith("feature") and dst == "main") for src, dst in topo)

def test_scientific_dependencies_are_explicit():
    p = payload()
    by = {x["token"]: x for x in p["work_items"]}
    assert by["TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION"]["dependencies"] == [
        "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS"
    ]
    assert set(by["TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE"]["dependencies"]) == {
        "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
        "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION",
        "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION",
    }
    assert by["TOKEN_VAZIO_INDEPENDENT_REPLICATION"]["dependencies"] == [
        "TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE"
    ]

def test_every_open_item_has_receipt_close_conditions_and_boundary():
    for item in payload()["work_items"]:
        assert item["expected_receipt"]
        assert item["close_when"]
        assert item["boundary"]
        assert item["branch"]

def test_known_main_readme_regression_is_marked_not_silently_fixed():
    points = {x["id"]: x for x in payload()["necessary_points"]}
    assert points["NP-003"]["state"] == "OPEN_DOC_HOTFIX"
    assert "literal" in points["NP-003"]["issue"]
