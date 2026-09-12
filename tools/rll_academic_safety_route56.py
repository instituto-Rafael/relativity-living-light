#!/usr/bin/env python3
"""Generate the RLL 8x7 academic-safety cross-examination graph.

Eight compass directions are navigation domains, not evidence weights.
Every ordered pair of distinct directions is one route: P(8,2)=56.
Each route carries six academic-production checkpoints:
SOURCE, ARTEFACT, METHOD, EXECUTION, EVIDENCE, CLAIM.

The center is not a ninth permutation node. It reduces the current scientific
claim state to UP_READY, HOLD_TOKEN_VAZIO, or DOWN_BLOCKED.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "governance" / "RLL_ACADEMIC_SAFETY_ROUTE56_V1.json"
DEFAULT_EVIDENCE = ROOT / "results" / "audit" / "rll_real_data_evidence_bridge.json"
DEFAULT_E0 = ROOT / "results" / "audit" / "rll_cosmology_e0_preflight.json"
DEFAULT_OUTPUT = ROOT / "results" / "audit" / "rll_academic_safety_route56.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _pass(check: dict[str, Any] | None) -> bool:
    return bool(check and check.get("pass") is True)


def build_domain_state(
    contract: dict[str, Any],
    evidence: dict[str, Any],
    e0: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    checks = evidence.get("checks", {})
    registry = load_json(ROOT / contract["production_inputs"]["evidence_registry"])
    validation = load_json(ROOT / contract["production_inputs"]["validation_contract"])

    source_ok = (
        _pass(checks.get("desi_local_hash"))
        and _pass(checks.get("cmb_local_hash"))
        and _pass(checks.get("growth_local_hash"))
        and _pass(checks.get("pantheon_literature_identity"))
    )
    data_ok = bool(evidence.get("data_bridge_pass"))
    execution_observed = bool(os.getenv("GITHUB_RUN_ID") and os.getenv("GITHUB_SHA"))
    history_ok = all(
        item.get("historical_artifact_mutated") is False
        for item in registry.get("known_provenance_corrections", [])
    )
    overlap_limited_ok = (
        _pass(checks.get("hz_independence_partition"))
        and _pass(checks.get("desi_schema_covariance"))
        and evidence.get("latest_external_update_policy", {}).get("combination_policy", "").startswith("MUTUALLY_EXCLUSIVE")
    )
    claim_fail_closed = (
        evidence.get("claim_allowed") is False
        and e0.get("claim_allowed") is False
        and validation.get("claim_allowed") is False
    )

    method_ready = bool(e0.get("model_selection_claim_allowed"))
    full_inference = bool(evidence.get("full_joint_inference_ready"))

    return {
        "SOURCE_AUTHORITY": {
            "status": "PASS_LIMITED" if source_ok else "BLOCKED",
            "evidence": ["external evidence registry", "local hashes", "literature identities"],
        },
        "METHOD_VALIDITY": {
            "status": "PASS" if method_ready else "BLOCKED",
            "evidence": [e0.get("status", "TOKEN_VAZIO_E0_STATUS")],
            "gap": None if method_ready else "E0 scientific-promotion prerequisites remain blocked",
        },
        "DATA_PROVENANCE": {
            "status": "PASS_LIMITED" if data_ok else "BLOCKED",
            "evidence": [evidence.get("status", "TOKEN_VAZIO_EVIDENCE_BRIDGE_STATUS")],
        },
        "EXECUTION_REPRODUCIBILITY": {
            "status": "PASS_LIMITED" if execution_observed else "TOKEN_VAZIO",
            "evidence": [{
                "github_run_id": os.getenv("GITHUB_RUN_ID", "TOKEN_VAZIO_RUNTIME"),
                "github_sha": os.getenv("GITHUB_SHA", "TOKEN_VAZIO_RUNTIME"),
            }],
        },
        "FALSIFICATION": {
            "status": "PASS_LIMITED" if full_inference else "TOKEN_VAZIO",
            "evidence": ["claim remains blocked", "null/adversary infrastructure exists"],
            "gap": None if full_inference else "TOKEN_VAZIO_FULL_JOINT_INFERENCE",
        },
        "DEPENDENCE_BIAS": {
            "status": "PASS_LIMITED" if overlap_limited_ok else "BLOCKED",
            "evidence": ["independent CC partition", "DESI covariance", "Ly-alpha mutual-exclusion policy"],
            "gap": "TOKEN_VAZIO_HETEROGENEOUS_GROWTH_COVARIANCE",
        },
        "HISTORY_VERSIONING": {
            "status": "PASS" if history_ok else "BLOCKED",
            "evidence": ["append-only provenance corrections"],
        },
        "CLAIM_GOVERNANCE": {
            "status": "PASS_FAIL_CLOSED" if claim_fail_closed else "BLOCKED",
            "evidence": ["claim_allowed=false across evidence/E0/validation contract"],
        },
    }


def relation_class(min_turn_deg: int) -> str:
    return {
        45: "TANGENTIAL_NEIGHBOR",
        90: "ORTHOGONAL",
        135: "OBLIQUE_CROSS",
        180: "ANTIPODAL",
    }[min_turn_deg]


def build_quadratic_projection_bridge() -> dict[str, Any]:
    """Exact 45-degree residual geometry plus secondary sqrt(3)/2 projection.

    Let a,b be the catheti, h=sqrt(a^2+b^2), and d_a=h-a.  Writing
    h=a+d_a gives d_a^2+2*a*d_a=b^2.  This is the completing-square /
    borrowed-area form of the same identity as (h-a)(h+a)=b^2.

    For the 45-degree isosceles case a=b=1, d=sqrt(2)-1.  The pair
    (sqrt(3)/2*d, 1/2*d) is a second-stage orthogonal decomposition of d,
    because 3/4+1/4=1.  It is geometric metadata, never evidence weight.
    """

    a = 1.0
    b = 1.0
    h = math.sqrt(a * a + b * b)
    d_a = h - a
    d_b = h - b

    borrowed_square = d_a * d_a
    borrowed_rectangles = 2.0 * a * d_a
    recovered_opposite_square = borrowed_square + borrowed_rectangles

    factor_left = h - a
    factor_right = h + a
    factor_product = factor_left * factor_right

    projection_30 = math.sqrt(3.0) / 2.0
    projection_orth = 0.5
    p = projection_30 * d_a
    q = projection_orth * d_a

    h_unit = 1.0
    leg_h_unit = math.sqrt(2.0) / 2.0
    residual_h_unit = h_unit - leg_h_unit

    return {
        "general_identities": {
            "pythagoras": "h^2=a^2+b^2",
            "residual_definition": "d_a=h-a",
            "completing_square": "d_a^2+2*a*d_a=b^2",
            "difference_of_squares": "(h-a)(h+a)=b^2",
            "symmetric_difference_of_squares": "(h-b)(h+b)=a^2",
            "catheti_difference": "(a-b)(a+b)=a^2-b^2",
        },
        "isosceles_45_leg_normalized": {
            "a": a,
            "b": b,
            "h": h,
            "d_a": d_a,
            "d_b": d_b,
            "catheti_difference": a - b,
            "d_exact": "sqrt(2)-1",
            "borrowed_square": borrowed_square,
            "borrowed_rectangles_2ad": borrowed_rectangles,
            "recovered_b_squared": recovered_opposite_square,
            "factor_product": factor_product,
            "factor_identity_exact": "(sqrt(2)-1)(sqrt(2)+1)=1",
        },
        "secondary_projection_sqrt3_over_2": {
            "coefficient_parallel": projection_30,
            "coefficient_orthogonal": projection_orth,
            "projected_parallel": p,
            "projected_orthogonal": q,
            "projected_parallel_exact": "(sqrt(6)-sqrt(3))/2",
            "projected_orthogonal_exact": "(sqrt(2)-1)/2",
            "norm_reconstructed": p * p + q * q,
            "residual_squared": d_a * d_a,
            "evidence_weight": False,
            "physical_claim": False,
        },
        "isosceles_45_hypotenuse_normalized": {
            "h": h_unit,
            "a": leg_h_unit,
            "b": leg_h_unit,
            "residual_h_minus_cathetus": residual_h_unit,
            "residual_exact": "1-sqrt(2)/2",
        },
    }


def route_state(a: str, b: str) -> str:
    statuses = {a, b}
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "TOKEN_VAZIO" in statuses:
        return "TOKEN_VAZIO"
    return "ROUTABLE_LIMITED"


def poi_state(name: str, route_status: str, evidence: dict[str, Any], e0: dict[str, Any]) -> str:
    if name == "SOURCE":
        return "PASS_LIMITED" if evidence.get("data_bridge_pass") else "BLOCKED"
    if name == "ARTEFACT":
        return "PASS_LIMITED" if evidence.get("data_bridge_pass") else "BLOCKED"
    if name == "METHOD":
        return "PASS" if e0.get("model_selection_claim_allowed") else "BLOCKED"
    if name == "EXECUTION":
        return "OBSERVED" if os.getenv("GITHUB_RUN_ID") else "TOKEN_VAZIO_RUNTIME"
    if name == "EVIDENCE":
        return route_status
    if name == "CLAIM":
        return "BLOCKED_FALSE"
    raise KeyError(name)


def build_report(contract: dict[str, Any], evidence: dict[str, Any], e0: dict[str, Any]) -> dict[str, Any]:
    directions = sorted(contract["directions"], key=lambda x: x["index"])
    domains = build_domain_state(contract, evidence, e0)
    six_poi = contract["six_poi"]

    routes: list[dict[str, Any]] = []
    relation_counts: dict[str, int] = {}

    for src in directions:
        for dst in directions:
            if src["id"] == dst["id"]:
                continue
            cw_steps = (dst["index"] - src["index"]) % 8
            ccw_steps = (src["index"] - dst["index"]) % 8
            min_steps = min(cw_steps, ccw_steps)
            min_turn = int(min_steps * 45)
            rel = relation_class(min_turn)
            relation_counts[rel] = relation_counts.get(rel, 0) + 1

            src_status = domains[src["domain"]]["status"]
            dst_status = domains[dst["domain"]]["status"]
            state = route_state(src_status, dst_status)

            core = {
                "from": src["id"],
                "to": dst["id"],
                "from_domain": src["domain"],
                "to_domain": dst["domain"],
                "cw_steps": cw_steps,
                "ccw_steps": ccw_steps,
                "min_turn_deg": min_turn,
                "relation_class": rel,
            }
            route_hash = canonical_sha256(core)
            routes.append({
                "id": f"{src['id']}->{dst['id']}",
                "from": {
                    "id": src["id"], "emoji": src["emoji"], "pt": src["pt"], "en": src["en"],
                    "angle_deg": src["angle_deg"], "domain": src["domain"], "status": src_status,
                },
                "to": {
                    "id": dst["id"], "emoji": dst["emoji"], "pt": dst["pt"], "en": dst["en"],
                    "angle_deg": dst["angle_deg"], "domain": dst["domain"], "status": dst_status,
                },
                "rotation": {
                    "cw_steps": cw_steps,
                    "ccw_steps": ccw_steps,
                    "min_turn_deg": min_turn,
                    "relation_class": rel,
                },
                "route_state": state,
                "six_poi": [
                    {"id": poi["id"], "name": poi["name"], "state": poi_state(poi["name"], state, evidence, e0)}
                    for poi in six_poi
                ],
                "route_contract_sha256": route_hash,
                "scientific_weight": None,
            })

    critical_statuses = [domains[d["domain"]]["status"] for d in directions]
    if "BLOCKED" in critical_statuses:
        center_state = "DOWN_BLOCKED"
    elif "TOKEN_VAZIO" in critical_statuses:
        center_state = "HOLD_TOKEN_VAZIO"
    else:
        center_state = "UP_READY"

    # Compass convention: 0 degrees is UP; x=sin(theta), y=cos(theta).
    vectors = []
    for d in directions:
        theta = math.radians(d["angle_deg"])
        radial = [math.sin(theta), math.cos(theta)]
        tangent_clockwise = [math.cos(theta), -math.sin(theta)]
        vectors.append({
            "id": d["id"],
            "radial_xy": radial,
            "tangent_clockwise_xy": tangent_clockwise,
            "radial_norm": math.hypot(*radial),
            "radial_dot_tangent": radial[0] * tangent_clockwise[0] + radial[1] * tangent_clockwise[1],
        })

    graph_core = [{
        "id": r["id"],
        "rotation": r["rotation"],
        "route_state": r["route_state"],
        "route_contract_sha256": r["route_contract_sha256"],
    } for r in routes]

    return {
        "schema": "rll.academic_safety_route56.report.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "route_count": len(routes),
        "poi_per_route": len(six_poi),
        "control_cell_count": len(routes) * len(six_poi),
        "direction_count": len(directions),
        "directions": directions,
        "direction_vectors": vectors,
        "domain_state": domains,
        "relation_counts": relation_counts,
        "center": {
            "state": center_state,
            "claim_allowed": False,
            "semantic_boundary": contract["center_state_semantics"][center_state],
        },
        "geometry": contract["geometry"],
        "quadratic_projection_bridge": build_quadratic_projection_bridge(),
        "routes": routes,
        "graph_contract_sha256": canonical_sha256(graph_core),
        "claim_allowed": False,
        "scientific_confirmation": False,
        "invariants": contract["invariants"],
    }


def validate_structure(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report["direction_count"] != 8:
        errors.append("direction_count must be 8")
    if report["route_count"] != 56:
        errors.append("route_count must be 56")
    if report["poi_per_route"] != 6:
        errors.append("poi_per_route must be 6")
    if report["control_cell_count"] != 336:
        errors.append("control_cell_count must be 336")

    ids = [r["id"] for r in report["routes"]]
    if len(ids) != len(set(ids)):
        errors.append("route ids must be unique")
    if any(r["from"]["id"] == r["to"]["id"] for r in report["routes"]):
        errors.append("self routes are forbidden")

    expected_relations = {
        "TANGENTIAL_NEIGHBOR": 16,
        "ORTHOGONAL": 16,
        "OBLIQUE_CROSS": 16,
        "ANTIPODAL": 8,
    }
    if report["relation_counts"] != expected_relations:
        errors.append(f"relation counts mismatch: {report['relation_counts']}")

    for d in report["directions"]:
        outdegree = sum(1 for r in report["routes"] if r["from"]["id"] == d["id"])
        indegree = sum(1 for r in report["routes"] if r["to"]["id"] == d["id"])
        if outdegree != 7 or indegree != 7:
            errors.append(f"{d['id']} degree mismatch: out={outdegree}, in={indegree}")

    for v in report["direction_vectors"]:
        if not math.isclose(v["radial_norm"], 1.0, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"{v['id']} radial vector is not unit length")
        if not math.isclose(v["radial_dot_tangent"], 0.0, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"{v['id']} tangent is not orthogonal")

    if report["geometry"]["sqrt3_over_2"]["evidence_weight"] is not False:
        errors.append("sqrt3/2 must not be an evidence weight")

    bridge = report["quadratic_projection_bridge"]
    iso = bridge["isosceles_45_leg_normalized"]
    projection = bridge["secondary_projection_sqrt3_over_2"]
    if not math.isclose(iso["recovered_b_squared"], 1.0, rel_tol=0.0, abs_tol=1e-12):
        errors.append("quadratic borrowed-area identity must recover b^2")
    if not math.isclose(iso["factor_product"], 1.0, rel_tol=0.0, abs_tol=1e-12):
        errors.append("difference-of-squares identity must recover b^2")
    if not math.isclose(
        projection["norm_reconstructed"],
        projection["residual_squared"],
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        errors.append("sqrt3/2 secondary projection must preserve residual norm")
    if projection["evidence_weight"] is not False or projection["physical_claim"] is not False:
        errors.append("quadratic projection bridge must remain non-empirical")

    if report["claim_allowed"] is not False:
        errors.append("route graph cannot promote scientific claim")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--evidence-report", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--e0-report", type=Path, default=DEFAULT_E0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-structure", action="store_true")
    args = parser.parse_args()

    contract_path = args.contract if args.contract.is_absolute() else ROOT / args.contract
    evidence_path = args.evidence_report if args.evidence_report.is_absolute() else ROOT / args.evidence_report
    e0_path = args.e0_report if args.e0_report.is_absolute() else ROOT / args.e0_report
    output_path = args.output if args.output.is_absolute() else ROOT / args.output

    report = build_report(load_json(contract_path), load_json(evidence_path), load_json(e0_path))
    errors = validate_structure(report)
    report["structure_pass"] = not errors
    report["structure_errors"] = errors

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "route_count": report["route_count"],
        "control_cell_count": report["control_cell_count"],
        "relation_counts": report["relation_counts"],
        "center_state": report["center"]["state"],
        "claim_allowed": report["claim_allowed"],
        "structure_pass": report["structure_pass"],
        "graph_contract_sha256": report["graph_contract_sha256"],
    }, indent=2, ensure_ascii=False))

    if args.require_structure and errors:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
