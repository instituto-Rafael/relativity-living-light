from __future__ import annotations

import json
import math
from pathlib import Path

from tools import rll_academic_safety_route56 as route56

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_ACADEMIC_SAFETY_ROUTE56_V1.json"
EVIDENCE = ROOT / "results/audit/rll_real_data_evidence_bridge.json"
E0 = ROOT / "results/audit/rll_cosmology_e0_preflight.json"


def report():
    return route56.build_report(
        route56.load_json(CONTRACT),
        route56.load_json(EVIDENCE),
        route56.load_json(E0),
    )


def test_permutation_contract_is_exactly_8p2_56() -> None:
    r = report()
    assert r["direction_count"] == 8
    assert r["route_count"] == math.perm(8, 2) == 56
    assert r["poi_per_route"] == 6
    assert r["control_cell_count"] == 336


def test_each_direction_has_seven_out_and_seven_in_routes() -> None:
    r = report()
    for d in r["directions"]:
        assert sum(x["from"]["id"] == d["id"] for x in r["routes"]) == 7
        assert sum(x["to"]["id"] == d["id"] for x in r["routes"]) == 7


def test_no_self_loops_and_every_route_has_reverse() -> None:
    r = report()
    pairs = {(x["from"]["id"], x["to"]["id"]) for x in r["routes"]}
    assert all(a != b for a, b in pairs)
    assert all((b, a) in pairs for a, b in pairs)


def test_45_degree_relation_partition_sums_to_56() -> None:
    r = report()
    assert r["relation_counts"] == {
        "TANGENTIAL_NEIGHBOR": 16,
        "ORTHOGONAL": 16,
        "OBLIQUE_CROSS": 16,
        "ANTIPODAL": 8,
    }


def test_pt_en_and_arrow_addresses_are_total() -> None:
    r = report()
    assert {d["emoji"] for d in r["directions"]} == {"↑", "↗️", "➡️", "↘️", "⬇️", "↙️", "⬅️", "↖️"}
    assert all(d["pt"] and d["en"] for d in r["directions"])


def test_radial_and_tangent_vectors_are_orthogonal() -> None:
    r = report()
    for v in r["direction_vectors"]:
        assert math.isclose(v["radial_norm"], 1.0, abs_tol=1e-12)
        assert math.isclose(v["radial_dot_tangent"], 0.0, abs_tol=1e-12)


def test_sqrt3_over_2_is_not_smuggled_in_as_evidence_weight() -> None:
    r = report()
    token = r["geometry"]["sqrt3_over_2"]
    assert token["exact"] == "sqrt(3)/2 = cos(30 degrees)"
    assert token["native_to_45deg_mesh"] is False
    assert token["evidence_weight"] is False
    assert token["status"] == "DEFINED_SECOND_STAGE_RESIDUAL_PROJECTION"


def test_center_is_not_a_ninth_permutation_node() -> None:
    r = report()
    assert r["geometry"]["center_in_permutation"] is False
    assert r["center"]["state"] in {"UP_READY", "HOLD_TOKEN_VAZIO", "DOWN_BLOCKED"}


def test_current_scientific_claim_remains_fail_closed() -> None:
    r = report()
    assert r["claim_allowed"] is False
    assert r["scientific_confirmation"] is False
    assert r["center"]["state"] == "DOWN_BLOCKED"
    assert r["domain_state"]["METHOD_VALIDITY"]["status"] == "BLOCKED"


def test_route56_structure_validator_passes() -> None:
    r = report()
    assert route56.validate_structure(r) == []



def test_45deg_borrowed_square_recovers_opposite_cathetus_area() -> None:
    r = report()
    iso = r["quadratic_projection_bridge"]["isosceles_45_leg_normalized"]
    assert math.isclose(iso["recovered_b_squared"], 1.0, abs_tol=1e-12)
    assert math.isclose(
        iso["borrowed_square"] + iso["borrowed_rectangles_2ad"],
        1.0,
        abs_tol=1e-12,
    )


def test_difference_of_squares_matches_pythagoras() -> None:
    r = report()
    iso = r["quadratic_projection_bridge"]["isosceles_45_leg_normalized"]
    assert math.isclose(iso["factor_product"], 1.0, abs_tol=1e-12)
    assert iso["factor_identity_exact"] == "(sqrt(2)-1)(sqrt(2)+1)=1"


def test_sqrt3_over_2_projects_the_45_residual_without_changing_norm() -> None:
    r = report()
    p = r["quadratic_projection_bridge"]["secondary_projection_sqrt3_over_2"]
    assert math.isclose(
        p["projected_parallel"] ** 2 + p["projected_orthogonal"] ** 2,
        p["residual_squared"],
        abs_tol=1e-12,
    )
    assert p["evidence_weight"] is False
    assert p["physical_claim"] is False


def test_45deg_catheti_are_equal_but_hypotenuse_residual_is_nonzero() -> None:
    r = report()
    iso = r["quadratic_projection_bridge"]["isosceles_45_leg_normalized"]
    assert math.isclose(iso["catheti_difference"], 0.0, abs_tol=1e-12)
    assert iso["d_a"] > 0.0
    assert math.isclose(iso["d_a"], iso["d_b"], abs_tol=1e-12)
