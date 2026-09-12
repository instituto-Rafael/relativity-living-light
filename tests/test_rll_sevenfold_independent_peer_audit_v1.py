from __future__ import annotations

from tools import rll_sevenfold_independent_peer_audit_v1 as sevenfold


def _receipt(peer_id: str, verdict: str) -> dict:
    return {
        "peer_id": peer_id,
        "verdict": verdict,
        "sealed": True,
        "peer_verdicts_visible_before_seal": False,
        "mandatory_test_count": 7,
    }


def test_contract_is_exactly_seven_by_seven() -> None:
    report = sevenfold.validate_contract()
    assert report["pass"] is True
    assert report["peer_count"] == 7
    assert report["tests_per_peer"] == [7] * 7
    assert report["total_checks"] == 49
    assert report["claim_allowed"] is False


def test_each_peer_has_unique_omega_and_ddagger() -> None:
    d = sevenfold.load_contract()
    assert len({p["omega_namespace"] for p in d["peers"]}) == 7
    assert len({p["ddagger_operator"] for p in d["peers"]}) == 7


def test_no_majority_vote_or_compensatory_average() -> None:
    d = sevenfold.load_contract()
    p = d["independence_protocol"]
    assert p["majority_vote"] == "FORBIDDEN"
    assert p["averaging"] == "FORBIDDEN"
    assert p["token_vazio_compensation"] == "FORBIDDEN"


def test_hidden_internal_tokens_and_literal_free_will_are_not_claimed() -> None:
    d = sevenfold.load_contract()
    g = d["semantic_token_graph_policy"]
    assert g["externalized_graph_only"] is True
    assert g["internal_hidden_tokens_or_chain_of_thought_claimed"] is False
    assert g["literal_free_will_claim"] is False


def test_one_falsification_blocks_global_promotion() -> None:
    d = sevenfold.load_contract()
    peers = [p["peer_id"] for p in d["peers"]]
    receipts = [_receipt(pid, "PASS_BOUNDED") for pid in peers]
    receipts[3]["verdict"] = "FAIL_FALSIFIED"
    out = sevenfold.aggregate_receipts(receipts)
    assert out["state"] == "REVIEW_BLOCKED_BY_FALSIFICATION"
    assert out["claim_allowed"] is False


def test_token_vazio_is_non_compensatory() -> None:
    d = sevenfold.load_contract()
    peers = [p["peer_id"] for p in d["peers"]]
    receipts = [_receipt(pid, "PASS_BOUNDED") for pid in peers]
    receipts[5]["verdict"] = "TOKEN_VAZIO"
    out = sevenfold.aggregate_receipts(receipts)
    assert out["state"] == "NOT_PROMOTABLE_INCOMPLETE_REVIEW"


def test_internal_disagreement_is_non_promotional() -> None:
    d = sevenfold.load_contract()
    peers = [p["peer_id"] for p in d["peers"]]
    receipts = [_receipt(pid, "PASS_BOUNDED") for pid in peers]
    receipts[1]["verdict"] = "INCONCLUSIVE"
    out = sevenfold.aggregate_receipts(receipts)
    assert out["state"] == "NOT_PROMOTABLE_INCOMPLETE_REVIEW"


def test_all_seven_pass_is_method_pass_not_scientific_claim() -> None:
    d = sevenfold.load_contract()
    receipts = [_receipt(p["peer_id"], "PASS_BOUNDED") for p in d["peers"]]
    out = sevenfold.aggregate_receipts(receipts)
    assert out["state"] == "SEVENFOLD_REVIEW_PASSED_NO_CLAIM_PROMOTION"
    assert out["claim_allowed"] is False
    assert out["replication_required"] is True


def test_missing_receipt_is_fail_closed() -> None:
    d = sevenfold.load_contract()
    receipts = [_receipt(p["peer_id"], "PASS_BOUNDED") for p in d["peers"][:-1]]
    out = sevenfold.aggregate_receipts(receipts)
    assert out["state"] == "NOT_PROMOTABLE_INVALID_OR_INCOMPLETE_RECEIPTS"
    assert out["errors"]


def test_authorship_is_not_inferred_from_hash_or_ai_role() -> None:
    d = sevenfold.load_contract()
    a = d["authorship_policy"]
    assert a["analytical_peer_role_is_legal_author"] is False
    assert a["hash_or_commit_proves_chronology_not_authorship"] is True
