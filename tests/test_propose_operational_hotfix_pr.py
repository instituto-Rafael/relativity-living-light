from tools.propose_operational_hotfix_pr import maturity_route_decision


def test_unverified_hotfix_route_is_fail_closed() -> None:
    allowed, state, residual = maturity_route_decision(
        {
            "main_hotfix_route": {
                "allowed": False,
                "state": "TOKEN_VAZIO_MATURITY_ROUTE",
                "verified_proposal_base": "TOKEN_VAZIO_MATURITY_ROUTE",
            }
        },
        "main",
    )
    assert allowed is False
    assert state == "TOKEN_VAZIO_MATURITY_ROUTE"
    assert residual == "HOTFIX_ROUTE_NOT_AUTHORIZED"


def test_missing_verified_base_is_not_permission() -> None:
    allowed, state, residual = maturity_route_decision(
        {"main_hotfix_route": {"allowed": True}},
        "main",
    )
    assert allowed is False
    assert state == "TOKEN_VAZIO_MATURITY_ROUTE"
    assert residual == "VERIFIED_PROPOSAL_BASE_MISSING"


def test_requested_base_must_equal_verified_base() -> None:
    allowed, state, residual = maturity_route_decision(
        {
            "main_hotfix_route": {
                "allowed": True,
                "state": "VERIFIED_REVIEWED_ROUTE",
                "verified_proposal_base": "rll/lab",
            }
        },
        "main",
    )
    assert allowed is False
    assert state == "TOKEN_VAZIO_MATURITY_ROUTE"
    assert "DIFFERS_FROM_VERIFIED" in residual


def test_verified_route_allows_only_declared_base() -> None:
    allowed, state, residual = maturity_route_decision(
        {
            "main_hotfix_route": {
                "allowed": True,
                "state": "VERIFIED_REVIEWED_ROUTE",
                "verified_proposal_base": "rll/lab",
            }
        },
        "rll/lab",
    )
    assert allowed is True
    assert state == "VERIFIED_REVIEWED_ROUTE"
    assert residual == "NONE"
