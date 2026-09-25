import json
from pathlib import Path

from rx.population_dispersion import route_population_dispersion

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "governance" / "RLL_POPULATION_DISPERSION_HYPOTHESIS_V1.json"


def test_disabled_layer_is_backward_compatible():
    out = route_population_dispersion({})
    assert out["state"] == "NOT_APPLICABLE"
    assert out["claim_allowed"] is False


def test_two_population_hypothesis_routes_without_claim_promotion():
    out = route_population_dispersion(
        {
            "enabled": True,
            "covariance_mode": "full",
            "age_mixture": True,
            "origin_mixture": True,
            "velocity_mixture": True,
            "residence_or_capture": True,
            "intervening_medium": True,
            "projection_effects": True,
            "selection_function": True,
            "selection_ref": "fixture:selection-v1",
            "populations": [{"id": "old_slow"}, {"id": "young_fast"}],
            "latents": {
                "origin": "MODEL_DEFINED",
                "age": "SOURCE_BOUND",
                "velocity": "SOURCE_BOUND",
                "residence_time": "HYPOTHESIS",
                "transport_history": "MODEL_DEFINED",
            },
            "parameters": [
                {
                    "id": "sigma_v",
                    "domain": "galactic_kinematics",
                    "unit": "km/s",
                    "state": "SOURCE_BOUND",
                    "source_ref": "fixture:kinematics",
                    "prior": "positive",
                    "falsifier": "one-population baseline is sufficient",
                }
            ],
        }
    )
    assert out["readiness"] == "ROUTABLE_HYPOTHESIS"
    assert out["source_bound_parameter_ids"] == ["sigma_v"]
    assert out["claim_allowed"] is False


def test_missing_parameter_evidence_stays_blocked():
    out = route_population_dispersion(
        {
            "enabled": True,
            "covariance_mode": "dataset_contract",
            "populations": [{"id": "a"}, {"id": "b"}],
            "latents": {},
            "parameters": [
                {
                    "id": "rll_extra",
                    "domain": "cosmology",
                    "unit": "TOKEN_VAZIO",
                    "state": "HYPOTHESIS",
                    "source_ref": "TOKEN_VAZIO_SOURCE",
                    "prior": "TOKEN_VAZIO",
                    "falsifier": "TOKEN_VAZIO",
                }
            ],
        }
    )
    assert "rll_extra" in out["blocked_parameter_ids"]
    assert out["claim_allowed"] is False


def test_diagonal_covariance_is_not_silently_used_for_mixed_medium():
    out = route_population_dispersion(
        {
            "enabled": True,
            "covariance_mode": "diagonal",
            "origin_mixture": True,
            "intervening_medium": True,
            "populations": [{"id": "a"}, {"id": "b"}],
        }
    )
    assert out["readiness"] == "BLOCKED_QUANTITATIVE"
    assert "diagonal_covariance_requires_explicit_independence_justification" in out["blocked_reasons"]


def test_cross_domain_evidence_cannot_be_promoted_to_cosmology():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    earth = contract["cross_domain_hidden_reservoir_analogy"]["earth_deep_water"]
    offshore = contract["cross_domain_hidden_reservoir_analogy"]["offshore_freshened_groundwater"]
    assert "not evidence for dark matter" in earth["forbidden_use"]
    assert "Do not equate" in offshore["forbidden_use"]
    assert contract["claim_allowed"] is False


def test_more_observations_do_not_automatically_authorize_more_parameters():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rule = contract["core_hypothesis"]["complexity_rule"]
    assert "do not by themselves authorize more free parameters" in rule
