from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_frontier_possibility_ladder.py"
spec = importlib.util.spec_from_file_location("possibility_ladder_validator", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

LADDER_PATH = ROOT / "data" / "contracts" / "frontier_possibility_ladder.v1.yml"
QUEUE_PATH = ROOT / "data" / "inputs" / "cosmology_joint" / "frontier_research_queue.v1.yml"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_canonical_ladder_passes():
    report = module.build_report(LADDER_PATH, QUEUE_PATH)
    assert report["status"] == "PASS"
    assert report["claim_allowed"] is False
    assert report["tier_count"] == 6
    assert report["portfolio_count"] == 5


def test_tiers_descend_from_near_to_unrankable():
    ladder = load(LADDER_PATH)
    assert [(item["id"], item["rank"]) for item in ladder["tiers"]] == module.EXPECTED_TIERS


def test_exploration_and_promotion_orders_are_separate():
    ladder = load(LADDER_PATH)
    orders = ladder["separation_of_orders"]
    assert orders["promotion_order"] == "evidence_dependency"
    assert orders["exploration_order"] == "theory_practice_proximity_descending"


def test_rejects_truth_probability_interpretation():
    ladder = load(LADDER_PATH)
    ladder["method"]["forbidden"].remove("numeric_truth_probability_without_calibration")
    errors = module.validate_ladder(ladder)
    assert "uncalibrated truth probability must be forbidden" in errors


def test_rejects_gap_hiding_average():
    ladder = load(LADDER_PATH)
    ladder["method"]["forbidden"].remove("weighted_average_hiding_mandatory_gap")
    errors = module.validate_ladder(ladder)
    assert "gap-hiding weighted averages must be forbidden" in errors


def test_rejects_missing_next_bridge():
    ladder = load(LADDER_PATH)
    ladder["portfolio"][0]["next_bridge"] = ""
    errors = module.validate_ladder(ladder)
    assert any("next_bridge required" in error for error in errors)


def test_rejects_unknown_tier():
    ladder = load(LADDER_PATH)
    ladder["portfolio"][0]["exploration_tier"] = "P9_CERTAIN"
    errors = module.validate_ladder(ladder)
    assert any("unknown exploration_tier" in error for error in errors)


def test_rejects_promotion_state_drift_from_queue():
    ladder = load(LADDER_PATH)
    queue = load(QUEUE_PATH)
    ladder["portfolio"][0]["current_promotion_state"] = "THEORY_CANDIDATE"
    errors = module.validate_against_queue(ladder, queue)
    assert any("promotion state differs from queue" in error for error in errors)


def test_token_bottleneck_must_exist_in_queue_gaps():
    ladder = load(LADDER_PATH)
    queue = load(QUEUE_PATH)
    ladder["portfolio"][0]["bottleneck"] = "TOKEN_VAZIO_NOT_IN_QUEUE"
    errors = module.validate_against_queue(ladder, queue)
    assert any("bottleneck is not recorded in queue gaps" in error for error in errors)


def test_duplicate_portfolio_fragment_is_rejected():
    ladder = load(LADDER_PATH)
    ladder["portfolio"].append(copy.deepcopy(ladder["portfolio"][0]))
    errors = module.validate_ladder(ladder)
    assert "portfolio fragment ids must be unique" in errors


def test_high_tier_does_not_change_claim_boundary():
    report = module.build_report(LADDER_PATH, QUEUE_PATH)
    assert report["tier_counts"]["P5_NEAR_OPERATIONAL"] == 1
    assert report["publication_effect"] == "NONE"
    assert report["claim_allowed"] is False
