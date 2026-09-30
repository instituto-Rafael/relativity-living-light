#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import Any

from tools.rll_growth_semantics_abc import build_report as build_abc
from tools.rll_perturbation_barotropic_candidate_v1 import build as build_barotropic

SCHEMA = "rll.growth_semantics_final_consolidation.v1.report"

def build_report() -> dict[str, Any]:
    abc = build_abc()
    baro = build_barotropic()
    baro_cases = baro["sweep"]["cases"]
    passing = sum(bool(row["pass"]) for row in baro_cases)

    a0_falsified = (
        baro["state"] == "FALSIFIED_AS_GLOBAL_DEFAULT"
        and len(baro_cases) == 9
        and passing == 0
        and baro["claim_allowed"] is False
    )
    a1_background_needed = (
        abc["route_A"]["continuity_math"] == "PASS"
        and abc["route_A"]["canonical_kinetic_sign_sweep"] == "PASS_NO_W_LT_MINUS1"
    )
    b_formal = (
        abc["route_B"]["formal_q_source"] == "PASS"
        and abc["route_B"]["formal_equal_opposite_total_accounting"] == "PASS"
        and abc["route_B"]["receiver_sector_implemented"] is False
        and abc["route_B"]["covariant_Q_mu_implemented"] is False
    )
    c_safe = (
        abc["route_C"]["background_claim_boundary"] == "PASS"
        and abc["route_C"]["physical_cs2"] == "TOKEN_VAZIO"
        and abc["route_C"]["dark_sector_perturbations"] == "BLOCKED"
    )

    state = "CONSOLIDATED_FAIL_CLOSED" if all((a0_falsified, a1_background_needed, b_formal, c_safe)) else "INCONSISTENT"

    return {
        "schema": SCHEMA,
        "state": state,
        "claim_allowed": False,
        "publication_ready": False,
        "physical_semantics_selected": False,
        "selected_semantics": "TOKEN_VAZIO",
        "operational_baseline": "C_PHENOMENOLOGICAL_BACKGROUND" if c_safe else "TOKEN_VAZIO",
        "A0": {
            "state": "FALSIFIED_AS_GLOBAL_DEFAULT" if a0_falsified else "INCONSISTENT",
            "cases": len(baro_cases),
            "passing_cases": passing,
        },
        "A1": {
            "state": "OPEN_BOUNDED_NECESSARY_CONDITIONS_PASS" if a1_background_needed else "BLOCKED",
            "continuity_math": abc["route_A"]["continuity_math"],
            "canonical_kinetic_sign_sweep": abc["route_A"]["canonical_kinetic_sign_sweep"],
            "min_one_plus_w": abc["route_A"]["min_one_plus_w"],
            "exact_perturbations": "TOKEN_VAZIO",
        },
        "B": {
            "state": "FORMAL_Q_PASS_PHYSICS_BLOCKED" if b_formal else "INCONSISTENT",
            "receiver_sector_implemented": abc["route_B"]["receiver_sector_implemented"],
            "covariant_Q_mu_implemented": abc["route_B"]["covariant_Q_mu_implemented"],
        },
        "C": {
            "state": "SURVIVES_AS_OPERATIONAL_BASELINE" if c_safe else "INCONSISTENT",
            "physical_cs2": abc["route_C"]["physical_cs2"],
            "dark_sector_perturbations": abc["route_C"]["dark_sector_perturbations"],
        },
        "downstream": {
            "GROWTH_CS2_001": "BLOCKED_BY_UNASSIGNED_PHYSICAL_CLOSURE",
            "GROWTH_CONSERVATION_001": "BLOCKED_BY_UPSTREAM_POLICY",
            "GROWTH_D_001": "BLOCKED_BY_UPSTREAM_POLICY",
            "GROWTH_FSIG8_001": "BLOCKED_BY_UPSTREAM_POLICY",
            "FIT_MODELSEL_001": "BLOCKED_BY_DEPENDENCY",
        },
        "final_decision": {
            "operational": "USE_C_BACKGROUND_ONLY",
            "scientific": "NO_UNIQUE_PHYSICAL_WINNER",
            "claim": "BLOCKED",
        },
        "boundary": (
            "Final consolidation is operational and epistemic, not a physical discovery. "
            "A0 negative evidence is preserved; A1 and B remain research candidates; "
            "C is the safest currently supported operational boundary."
        ),
    }

def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report["state"] != "CONSOLIDATED_FAIL_CLOSED":
        errors.append("state:not_consolidated")
    if report["claim_allowed"] is not False:
        errors.append("claim:must_remain_false")
    if report["physical_semantics_selected"] is not False:
        errors.append("semantics:must_remain_unselected")
    if report["A0"]["passing_cases"] != 0:
        errors.append("A0:negative_evidence_regressed")
    if report["A1"]["exact_perturbations"] != "TOKEN_VAZIO":
        errors.append("A1:perturbations_promoted_without_evidence")
    if report["B"]["receiver_sector_implemented"] is not False:
        errors.append("B:receiver_status_changed_without_source")
    if report["C"]["state"] != "SURVIVES_AS_OPERATIONAL_BASELINE":
        errors.append("C:background_baseline_missing")
    if report["final_decision"]["claim"] != "BLOCKED":
        errors.append("claim:final_not_blocked")
    return errors

def main() -> int:
    report = build_report()
    errors = validate(report)
    print(json.dumps({"report": report, "errors": errors}, indent=2, sort_keys=True))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
