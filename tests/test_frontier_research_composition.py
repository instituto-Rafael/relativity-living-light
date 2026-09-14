from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_frontier_research_composition.py"
spec = importlib.util.spec_from_file_location("frontier_validator", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

CONTRACT_PATH = ROOT / "data" / "contracts" / "frontier_research_composition.v1.yml"
QUEUE_PATH = ROOT / "data" / "inputs" / "cosmology_joint" / "frontier_research_queue.v1.yml"


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_canonical_contract_and_queue_pass():
    report = module.build_report(CONTRACT_PATH, QUEUE_PATH)
    assert report["status"] == "PASS"
    assert report["claim_allowed"] is False
    assert report["stage_count"] == 10
    assert report["prompt_pass_count"] == 9
    assert report["token_vazio_count"] > 0


def test_rejects_size_ordering():
    contract = load(CONTRACT_PATH)
    contract["ordering"]["mode"] = "smallest_to_largest"
    assert "ordering must be evidence-dependent" in module.validate_contract(contract)


def test_rejects_claim_promotion():
    contract = load(CONTRACT_PATH)
    contract["claim_allowed"] = True
    assert "claim_allowed must remain false" in module.validate_contract(contract)


def test_rejects_missing_token_vazio_exit():
    contract = load(CONTRACT_PATH)
    contract["stages"][3]["on_missing"] = "UNKNOWN"
    errors = module.validate_contract(contract)
    assert any("on_missing must be TOKEN_VAZIO" in error for error in errors)


def test_rejects_noncontiguous_stage_order():
    contract = load(CONTRACT_PATH)
    contract["stages"][4]["order"] = 99
    assert "stage order must be contiguous from zero" in module.validate_contract(contract)


def test_requires_no_double_counting_gate():
    contract = load(CONTRACT_PATH)
    contract["composition_policy"]["required_gates"].remove("no_double_counting")
    assert "composition requires no_double_counting gate" in module.validate_contract(contract)


def test_requires_identifiability_gate():
    contract = load(CONTRACT_PATH)
    contract["composition_policy"]["required_gates"].remove("identifiable_parameters")
    assert "composition requires identifiability gate" in module.validate_contract(contract)


def test_token_vazio_track_requires_exit_artifacts():
    contract = load(CONTRACT_PATH)
    track = copy.deepcopy(contract["frontier_tracks"][1])
    track["required_artifacts"] = []
    contract["frontier_tracks"][1] = track
    errors = module.validate_contract(contract)
    assert any("TOKEN_VAZIO requires exit artifacts" in error for error in errors)


def test_queue_requires_reference():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    queue["items"][0]["references"] = []
    errors = module.validate_queue(queue, contract)
    assert any("at least one reference required" in error for error in errors)


def test_queue_gaps_are_token_vazio():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    queue["items"][0]["gaps"] = ["TODO"]
    errors = module.validate_queue(queue, contract)
    assert any("gap must be TOKEN_VAZIO" in error for error in errors)


def test_queue_rejects_duplicate_fragment_ids():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    queue["items"].append(copy.deepcopy(queue["items"][0]))
    assert "fragment ids must be unique" in module.validate_queue(queue, contract)


def test_prompt_failures_are_token_vazio():
    contract = load(CONTRACT_PATH)
    contract["prompt_evolution"]["passes"][0]["on_failure"] = "FAIL"
    errors = module.validate_contract(contract)
    assert any("failure must become TOKEN_VAZIO" in error for error in errors)


ORCHESTRATOR_SCRIPT = ROOT / "scripts" / "run_frontier_research_orchestrator.py"
orch_spec = importlib.util.spec_from_file_location("frontier_orchestrator", ORCHESTRATOR_SCRIPT)
orch = importlib.util.module_from_spec(orch_spec)
assert orch_spec.loader is not None
orch_spec.loader.exec_module(orch)


def test_prompt_evolution_reaches_fixed_point():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    results, iterations = orch.iterate_to_fixed_point(contract, queue)
    assert iterations == 2
    assert len(results) == len(queue["items"])


def test_rll_fragment_passes_implementation_but_not_statistics():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    result = orch.evaluate_item(queue["items"][0], contract)
    states = {entry["pass_id"]: entry["state"] for entry in result["prompt_passes"]}
    assert states["P4_IMPLEMENT"] == "PASS"
    assert states["P5_STATISTICS"].startswith("TOKEN_VAZIO")


def test_unformalized_fragment_does_not_receive_implicit_promotion():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    result = orch.evaluate_item(queue["items"][1], contract)
    states = {entry["pass_id"]: entry["state"] for entry in result["prompt_passes"]}
    assert states["P1_SOURCE"] == "PASS_WITH_BOUNDARY"
    assert states["P2_FORMAL"].startswith("TOKEN_VAZIO")
    assert result["claim_allowed"] is False


def test_receipt_preserves_publication_boundary():
    receipt = orch.build_receipt(CONTRACT_PATH, QUEUE_PATH)
    assert receipt["status"] == "FIXED_POINT"
    assert receipt["publication_effect"] == "NONE"
    assert receipt["claim_allowed"] is False
    assert receipt["token_vazio_pass_count"] > 0
