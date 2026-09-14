from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_theory_practice_calibration.py"
spec = importlib.util.spec_from_file_location("theory_practice_calibration_validator", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

CALIBRATION_PATH = ROOT / "data" / "contracts" / "theory_practice_calibration.v1.yml"
LADDER_PATH = ROOT / "data" / "contracts" / "frontier_possibility_ladder.v1.yml"
QUEUE_PATH = ROOT / "data" / "inputs" / "cosmology_joint" / "frontier_research_queue.v1.yml"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_canonical_calibration_passes():
    report = module.build_report(CALIBRATION_PATH, LADDER_PATH, QUEUE_PATH)
    assert report["status"] == "PASS"
    assert report["claim_allowed"] is False
    assert report["publication_effect"] == "NONE"
    assert report["profile_count"] == 5
    assert report["mandatory_delta_axis_count"] == 6


def test_calibration_is_not_truth_probability():
    payload = load(CALIBRATION_PATH)
    assert payload["symbolic_language"]["working_relation"] == "theory ~= practice"
    assert "universal truth" in payload["symbolic_language"]["infinity"]
    assert payload["claim_allowed"] is False


def test_omega_pi_infinity_invariant_is_append_only():
    payload = load(CALIBRATION_PATH)
    invariant = payload["knowledge_invariant"]
    assert invariant["id"] == "OMEGA_PI_INFINITY_DATA_INVARIANT"
    assert invariant["append_only_transitions"] is True
    assert invariant["token_vazio_is_data"] is True
    assert invariant["silent_deletion_forbidden"] is True


def test_states_descend_from_reproduced_to_uncalibrated():
    payload = load(CALIBRATION_PATH)
    observed = [(item["id"], item["rank"]) for item in payload["calibration_states"]]
    assert observed == module.EXPECTED_STATES


def test_every_ranked_fragment_has_one_calibration_profile():
    calibration = load(CALIBRATION_PATH)
    ladder = load(LADDER_PATH)
    calibrated = {item["fragment_id"] for item in calibration["profiles"]}
    ranked = {item["fragment_id"] for item in ladder["portfolio"]}
    assert calibrated == ranked
    assert ladder["calibration_contract"] == module.EXPECTED_CALIBRATION_PATH


def test_rejects_missing_mandatory_delta_axis():
    payload = load(CALIBRATION_PATH)
    del payload["profiles"][0]["delta_vector"][module.EXPECTED_AXES[-1]]
    errors = module.validate_contract(payload)
    assert any("delta axes must be complete and ordered" in error for error in errors)


def test_rejects_token_vazio_without_exit_criterion():
    payload = load(CALIBRATION_PATH)
    axis = payload["profiles"][0]["delta_vector"]["prediction_to_receipt"]
    del axis["exit_criterion"]
    errors = module.validate_contract(payload)
    assert any("TOKEN_VAZIO requires exit_criterion" in error for error in errors)


def test_rejects_partial_without_missing_boundary():
    payload = load(CALIBRATION_PATH)
    axis = payload["profiles"][0]["delta_vector"]["observable_to_measurement"]
    del axis["missing"]
    errors = module.validate_contract(payload)
    assert any("PARTIAL requires missing boundary" in error for error in errors)


def test_rejects_bounded_approximation_with_token_vazio():
    payload = load(CALIBRATION_PATH)
    payload["profiles"][0]["relation_state"] = "APPROX_BOUNDED"
    errors = module.validate_contract(payload)
    assert any("APPROX_BOUNDED cannot contain TOKEN_VAZIO" in error for error in errors)


def test_rejects_executable_shadow_without_practice_anchor():
    payload = load(CALIBRATION_PATH)
    payload["profiles"][0]["practice_anchors"] = []
    errors = module.validate_contract(payload)
    assert any("executable shadow requires practice anchor" in error for error in errors)


def test_rejects_exploration_tier_drift():
    calibration = load(CALIBRATION_PATH)
    ladder = load(LADDER_PATH)
    queue = load(QUEUE_PATH)
    calibration["profiles"][0]["exploration_tier"] = "P0_UNRANKABLE_TOKEN_VAZIO"
    errors = module.validate_cross_links(calibration, ladder, queue)
    assert any("exploration tier drift" in error for error in errors)


def test_rejects_calibration_profile_drift():
    calibration = load(CALIBRATION_PATH)
    ladder = load(LADDER_PATH)
    queue = load(QUEUE_PATH)
    ladder["portfolio"][0]["calibration_profile"] = "CAL-WRONG"
    errors = module.validate_cross_links(calibration, ladder, queue)
    assert any("calibration profile drift" in error for error in errors)


def test_rejects_ladder_without_canonical_calibration_contract():
    calibration = load(CALIBRATION_PATH)
    ladder = load(LADDER_PATH)
    queue = load(QUEUE_PATH)
    ladder["calibration_contract"] = "TOKEN_VAZIO"
    errors = module.validate_cross_links(calibration, ladder, queue)
    assert "ladder must point to the canonical calibration contract" in errors


def test_rejects_promotion_state_drift():
    calibration = load(CALIBRATION_PATH)
    ladder = load(LADDER_PATH)
    queue = load(QUEUE_PATH)
    calibration["profiles"][0]["promotion_state"] = "THEORY_CONFIRMED"
    errors = module.validate_cross_links(calibration, ladder, queue)
    assert any("promotion state drift" in error for error in errors)


def test_duplicate_calibration_profile_is_rejected():
    payload = load(CALIBRATION_PATH)
    payload["profiles"].append(copy.deepcopy(payload["profiles"][0]))
    errors = module.validate_contract(payload)
    assert "calibration ids must be unique" in errors
    assert "calibration fragment ids must be unique" in errors


def test_negative_result_remains_valid_knowledge_state():
    payload = load(CALIBRATION_PATH)
    rules = " ".join(payload["rules"])
    assert "NOT_EQUAL_OBSERVED" in rules
    assert "must not be renamed as success" in rules
