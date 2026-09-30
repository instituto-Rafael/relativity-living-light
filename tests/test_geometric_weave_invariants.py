from tools.verify_geometric_weave_invariants import run


def test_geometric_weave_invariants_all_scoped_checks_pass():
    report = run()
    assert report["summary"]["checks"] == 10
    assert report["summary"]["pass"] == 10
    assert report["summary"]["fail"] == 0
    assert all(row["status"] == "PASS" for row in report["checks"])


def test_external_claim_gates_remain_closed():
    report = run()
    assert report["summary"]["claim_allowed"] is False
    assert report["external_gates"]["prior_art"] == "TOKEN_VAZIO"
    assert report["external_gates"]["image_calibration"] == "TOKEN_VAZIO"
    assert report["external_gates"]["independent_reproduction"] == "NOT_RUN"
    assert report["external_gates"]["physical_binding"] == "TOKEN_VAZIO_BLOCKED"
