from tools.verify_mf160_formal_expressions import run


def test_mf160_has_one_result_per_formally_routed_expression():
    report = run()
    assert report["summary"]["target_count"] == 160
    assert report["summary"]["executed_count"] == 160
    assert report["summary"]["all_ids_have_result"] is True


def test_mf160_expected_epistemic_outcomes_are_preserved():
    report = run()
    by_id = {row["mf_id"]: row["status"] for row in report["results"]}
    assert by_id["MF-0219"] == "FAIL"
    assert by_id["MF-0130"] == "TOKEN_VAZIO_SEMANTICS"
    assert by_id["MF-0191"] == "TOKEN_VAZIO_SEMANTICS"
    assert by_id["MF-0129"] == "PASS_CONDITIONAL"
    assert by_id["MF-0221"] == "PASS_CONDITIONAL"


def test_mf160_does_not_promote_physics():
    report = run()
    assert report["claim_allowed"] is False
    assert report["physical_claim"] == "BLOCKED"
