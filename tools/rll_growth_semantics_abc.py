#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from typing import Any

SCHEMA = "rll.growth_semantics_abc.v1.report"
CASES = (
    (0.1, 0.05), (0.1, 0.3), (0.1, 2.0),
    (1.0, 0.05), (1.0, 0.3), (1.0, 2.0),
    (10.0, 0.05), (10.0, 0.3), (10.0, 2.0),
)

def transition_f(z: float, zt: float, wt: float) -> float:
    x = max(-700.0, min(700.0, (z - zt) / wt))
    return 1.0 / (1.0 + math.exp(x))

def dfdlna(z: float, zt: float, wt: float) -> float:
    f = transition_f(z, zt, wt)
    return (1.0 + z) * f * (1.0 - f) / wt

def rho_factor(z: float, zt: float, wt: float) -> float:
    f = transition_f(z, zt, wt)
    return f + (1.0 - f) * (1.0 + z) ** 3

def drho_factor_dlna(z: float, zt: float, wt: float) -> float:
    f = transition_f(z, zt, wt)
    return dfdlna(z, zt, wt) * (1.0 - (1.0 + z) ** 3) - 3.0 * (1.0 - f) * (1.0 + z) ** 3

def p_documented(z: float, zt: float, wt: float) -> float:
    return -transition_f(z, zt, wt)

def p_conserved(z: float, zt: float, wt: float) -> float:
    return -rho_factor(z, zt, wt) - drho_factor_dlna(z, zt, wt) / 3.0

def continuity_residual(z: float, zt: float, wt: float, p: float) -> float:
    return drho_factor_dlna(z, zt, wt) + 3.0 * (rho_factor(z, zt, wt) + p)

def q_over_h_factor(z: float, zt: float, wt: float) -> float:
    return dfdlna(z, zt, wt) * (1.0 - (1.0 + z) ** 3)

def sample_points(zt: float) -> list[float]:
    return sorted({0.0, zt, max(0.2, 2.0 * zt), 10.0, 100.0})

def build_report() -> dict[str, Any]:
    a_rows = []
    b_rows = []
    min_one_plus_w = math.inf

    for zt, wt in CASES:
        for z in sample_points(zt):
            r_cons = continuity_residual(z, zt, wt, p_conserved(z, zt, wt))
            r_doc = continuity_residual(z, zt, wt, p_documented(z, zt, wt))
            q = q_over_h_factor(z, zt, wt)
            w_cons = p_conserved(z, zt, wt) / rho_factor(z, zt, wt)
            min_one_plus_w = min(min_one_plus_w, 1.0 + w_cons)
            a_rows.append({
                "zt": zt, "wt": wt, "z": z,
                "continuity_residual": r_cons,
                "w_cons": w_cons,
                "one_plus_w": 1.0 + w_cons,
            })
            b_rows.append({
                "zt": zt, "wt": wt, "z": z,
                "documented_residual": r_doc,
                "q_s_over_h_factor": q,
                "source_matches_residual": math.isclose(r_doc, q, rel_tol=1e-10, abs_tol=1e-10),
                "formal_total_residual_with_equal_opposite_receiver": r_doc - q,
            })

    a_closes = all(abs(row["continuity_residual"]) <= 1e-10 for row in a_rows)
    a_no_phantom = min_one_plus_w >= -1e-10
    b_source = all(row["source_matches_residual"] for row in b_rows)
    b_total = all(abs(row["formal_total_residual_with_equal_opposite_receiver"]) <= 1e-10 for row in b_rows)

    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "selected_semantics": "TOKEN_VAZIO",
        "route_A": {
            "id": "CONSERVED_EFFECTIVE_FLUID",
            "state": "SURVIVES_MATH_GATE_PHYSICS_OPEN",
            "continuity_math": "PASS" if a_closes else "FAIL",
            "canonical_kinetic_sign_sweep": "PASS_NO_W_LT_MINUS1" if a_no_phantom else "FAIL",
            "min_one_plus_w": min_one_plus_w,
            "rows": a_rows,
            "boundary": "Algebraic conservation and no-phantom kinetic sign over this declared sweep do not prove a canonical scalar or observational viability.",
        },
        "route_B": {
            "id": "INTERACTING_SECTOR",
            "state": "FORMAL_Q_PASS_RECEIVER_BLOCKED",
            "formal_q_source": "PASS" if b_source else "FAIL",
            "formal_equal_opposite_total_accounting": "PASS" if b_total else "FAIL",
            "receiver_sector_implemented": False,
            "covariant_Q_mu_implemented": False,
            "rows": b_rows,
            "boundary": "Derived background source function is not a validated physical interaction.",
        },
        "route_C": {
            "id": "PHENOMENOLOGICAL_BACKGROUND",
            "state": "SURVIVES_AS_BACKGROUND_ONLY",
            "background_claim_boundary": "PASS",
            "physical_cs2": "TOKEN_VAZIO",
            "dark_sector_perturbations": "BLOCKED",
            "boundary": "A background function can be tested phenomenologically without selecting microphysics; it cannot authorize new-sector perturbation claims.",
        },
        "comparison": {
            "unique_physical_winner": False,
            "operational_order": [
                "A_TEST_FIRST",
                "B_IF_INTERACTION_IS_CHOSEN_OR_A_FAILS",
                "C_SAFE_BACKGROUND_FALLBACK",
            ],
            "reason": "A currently requires the fewest new physical structures to falsify next; B requires a recipient sector and covariant transfer; C deliberately ends the claim-bearing perturbation branch. This is an operational ordering, not evidence that A is physically true.",
        },
        "next": "version route A as a bounded candidate and test transition regularity, pressure perturbation closure, gauge/IC compatibility and conservation residuals; keep B and C live as rollback/fallback branches.",
    }

def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (
        report["route_A"]["continuity_math"] == "PASS"
        and report["route_B"]["formal_q_source"] == "PASS"
        and report["route_C"]["background_claim_boundary"] == "PASS"
        and report["claim_allowed"] is False
    ) else 1

if __name__ == "__main__":
    raise SystemExit(main())
