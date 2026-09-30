# RLL Evidence Evolution Matrix V1 — CORR1

Date: 2026-09-13
Parent: receipts/2026-09-13_RLL_EVIDENCE_EVOLUTION_MATRIX_V1.md
Claim allowed: false

## Correction

The initial matrix projected GROWTH-CS2-001 as the next scientific delta.

A subsequent direct source reconciliation found an older exact audit that proves
the documented rho_s,p_s pair does not satisfy separate continuity during the
transition and explicitly requires a physical-semantics choice before deriving
claim-bearing dark-sector perturbations.

The prior routing is preserved as historical context; it is not silently erased.

Corrected route:

CONTINUITY_SEMANTICS → GROWTH-CS2-001 → CONSERVATION/REGULARITY → D(z)

Successor evidence:
- PR #901
- data/governance/RLL_GROWTH_CONTINUITY_SEMANTICS_GATE_V1.json
- exact residual C(a)=f_prime*(1-a^-3)
- local math cross-check PASS over 33 sampled points

State:
- selected_semantics=TOKEN_VAZIO
- GROWTH-CS2-001=BLOCKED_BY_CONTINUITY_SEMANTICS
- claim_allowed=false

Rollback:
revert only this matrix correction if PR #901 is falsified; preserve both source
statements and the contradiction receipt.
