from __future__ import annotations

from tools import rll_perturbation_sound_speed_candidate_v1 as candidate


def test_sound_speed_candidate_contract_passes() -> None:
    report = candidate.build_report()
    assert report["pass"] is True
    assert report["status"] == "SOUND_SPEED_CANDIDATE_CONFIG_VALID"


def test_candidate_is_configured_but_not_effective() -> None:
    report = candidate.build_report()
    assert report["configured"] is True
    assert report["effective"] is False
    assert report["claim_allowed"] is False
    assert report["publication_ready"] is False


def test_candidate_is_cs2_one_comparator_not_rll_derivation() -> None:
    d = candidate.load()
    c = d["candidate"]
    assert c["rest_frame_cs2"] == 1.0
    assert c["derived_from_rll_background"] is False
    assert c["independent_of_ca2"] is True
    assert c["role"] == "comparator_only_not_RLL_derived"


def test_downstream_policy_tokens_remain_open() -> None:
    d = candidate.load()
    assert set(d["unresolved_dependencies"]) == candidate.REQUIRED_UNRESOLVED
    assert d["semantics"]["gauge_pressure_mapping"] == "TOKEN_VAZIO_GAUGE_POLICY"
    assert d["semantics"]["effective_in_perturbation_solver"] is False
