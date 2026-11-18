from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import yaml
import pytest

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


def test_rll_declared_implementation_does_not_prove_executed_checks():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    result = orch.evaluate_item(queue["items"][0], contract)
    states = {entry["pass_id"]: entry["state"] for entry in result["prompt_passes"]}
    assert states["P4_IMPLEMENT"] == "TOKEN_VAZIO_CHECK_EXECUTION"
    assert result["prompt_passes"][4]["declared_stage_reached"] is True
    assert states["P5_STATISTICS"].startswith("TOKEN_VAZIO")


def test_unformalized_fragment_does_not_receive_implicit_promotion():
    contract = load(CONTRACT_PATH)
    queue = load(QUEUE_PATH)
    result = orch.evaluate_item(queue["items"][1], contract)
    states = {entry["pass_id"]: entry["state"] for entry in result["prompt_passes"]}
    assert states["P1_SOURCE"] == "TOKEN_VAZIO_CHECK_EXECUTION"
    assert states["P2_FORMAL"].startswith("TOKEN_VAZIO")
    assert result["claim_allowed"] is False


def test_receipt_preserves_publication_boundary():
    receipt = orch.build_receipt(CONTRACT_PATH, QUEUE_PATH)
    assert receipt["status"] == "FIXED_POINT"
    assert receipt["publication_effect"] == "NONE"
    assert receipt["claim_allowed"] is False
    assert receipt["token_vazio_pass_count"] > 0
    assert receipt["fixed_point_scope"] == "DECLARATION_EVALUATION_ONLY"
    assert receipt["scientific_checks_execution"] == "NOT_RUN"


def test_high_stage_and_filenames_cannot_promote_to_pass():
    contract = load(CONTRACT_PATH)
    item = load(QUEUE_PATH)["items"][0]
    item.update(current_stage="S9_SYNTHESIS", state="REPLICATED")
    for evidence in ([], ["unexecuted_test.py"], ["receipt-not-verified.json"]):
        item["evidence"] = evidence
        result = orch.evaluate_item(item, contract)
        assert all(outcome["state"] == "TOKEN_VAZIO_CHECK_EXECUTION" for outcome in result["prompt_passes"])
        assert all(outcome["checks_execution"] == "NOT_RUN" for outcome in result["prompt_passes"])


def test_runtime_rejects_stage_index_aliases_and_collisions():
    for field, value in (("order", True), ("order", "1"), ("order", -1), ("id", "S0_FRAGMENT")):
        contract = load(CONTRACT_PATH)
        contract["stages"][1][field] = value
        with pytest.raises(ValueError, match="INVALID_STAGE_INDEX"):
            orch.iterate_to_fixed_point(contract, load(QUEUE_PATH))


def test_runtime_rejects_unknown_duplicate_and_missing_passes():
    for mode in ("unknown", "duplicate", "missing"):
        contract = load(CONTRACT_PATH)
        passes = contract["prompt_evolution"]["passes"]
        if mode == "unknown":
            passes[0]["id"] = "P99_UNKNOWN"
        elif mode == "duplicate":
            passes.append(copy.deepcopy(passes[0]))
        else:
            passes.pop()
        with pytest.raises(ValueError, match="PASS"):
            orch.iterate_to_fixed_point(contract, load(QUEUE_PATH))


def test_runtime_rejects_duplicate_fragments_before_fixed_point():
    queue = load(QUEUE_PATH)
    queue["items"].append(copy.deepcopy(queue["items"][0]))
    with pytest.raises(ValueError, match="DUPLICATE_FRAGMENT_ID"):
        orch.iterate_to_fixed_point(load(CONTRACT_PATH), queue)


def test_runtime_rejects_empty_unknown_and_null_inputs():
    with pytest.raises(ValueError, match="INVALID_QUEUE_ITEMS"):
        orch.iterate_to_fixed_point(load(CONTRACT_PATH), {"items": [], "claim_allowed": False})
    for field, value in (("current_stage", "UNKNOWN"), ("state", None), ("title", "")):
        queue = load(QUEUE_PATH)
        queue["items"][0][field] = value
        with pytest.raises(ValueError):
            orch.iterate_to_fixed_point(load(CONTRACT_PATH), queue)


def test_stage_label_swaps_cannot_change_gate_meaning():
    contract = load(CONTRACT_PATH)
    a, b = contract["stages"][0], contract["stages"][-1]
    a["id"], b["id"] = b["id"], a["id"]
    with pytest.raises(ValueError, match="INVALID_STAGE_INDEX_ORDER"):
        orch.iterate_to_fixed_point(contract, load(QUEUE_PATH))


def test_runtime_rejects_claim_promotion_and_string_evidence():
    queue = load(QUEUE_PATH)
    queue["claim_allowed"] = True
    with pytest.raises(ValueError, match="CLAIM_POLICY"):
        orch.iterate_to_fixed_point(load(CONTRACT_PATH), queue)
    queue = load(QUEUE_PATH)
    queue["items"][0]["evidence"] = "a filename is not a list of evidence"
    with pytest.raises(ValueError, match="INVALID_QUEUE_ITEM_evidence"):
        orch.iterate_to_fixed_point(load(CONTRACT_PATH), queue)
