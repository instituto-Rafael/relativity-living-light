# RLL Growth Continuity Semantics Gate V1

**Date:** 2026-09-13  
**State:** `BLOCKED_UNRESOLVED_PHYSICAL_SEMANTICS`  
**Claim allowed:** false

## Why this gate exists

The current RLL routing contains two statements that are individually
well-motivated but cannot safely be applied in the wrong order:

1. the 2026-09-12 gap retrofeedback ranks `GROWTH-CS2-001` as the best next
   perturbation delta;
2. the 2026-08-08 math/literature coherence audit proves that the documented
   `rho_s,p_s` pair does not satisfy separate continuity through the logistic
   transition and requires a semantic choice first.

This gate preserves both records and resolves the routing relation:

```text
continuity semantics
→ conservation / interaction accounting
→ GROWTH-CS2-001 candidate
→ conservation/regularity tests
→ D(z)
```

## Exact current residual

For

[
R(a)=f(a)+[1-f(a)]a^{-3},
qquad
p_{doc}/(Omega_{s0}ho_{c0})=-f(a),
]

separate conservation requires

[
rac{dR}{dln a}+3(R+p)=0.
]

The existing audit derives

[
oxed{mathcal C(a)=f'(1-a^{-3})}.
]

The executable gate reproduces that identity numerically and verifies that it
is nonzero inside the declared transition cases.

## Three legal routes

### A — Conserved effective fluid

Keep the versioned density and derive

[
p_{cons}=-ho_s-rac13rac{dho_s}{dln a}.
]

The gate verifies this closes continuity algebraically. That is a **math
result**, not a selection of physical semantics.

### B — Interacting sector

Keep the documented pressure only if a covariant `Q_mu` policy and an
equal-and-opposite receiving-sector accounting are defined consistently at
background and perturbation level.

### C — Phenomenological background

Keep the logistic `H(z)` map without claiming a closed effective
stress-energy/perturbation theory. In this route a claim-bearing `c_s^2`
remains `TOKEN_VAZIO`.

## Routing result

```text
GROWTH-CS2-001 = BLOCKED_BY_CONTINUITY_SEMANTICS
GROWTH-CONSERVATION-001 = BLOCKED
claim_allowed = false
```

No existing negative result is erased. No value of `c_s^2` is invented.

## Reproduction

```bash
python tools/rll_growth_continuity_semantics_gate.py --require-blocked
python -m pytest -q tests/test_rll_growth_continuity_semantics_gate.py
```

## Rollback

This is an additive successor gate. Rollback removes only the new gate/route
overlay and restores prior routing; the contradiction receipt and historical
sources remain preserved.

## R3

- **F_ok:** the continuity contradiction becomes executable and reconstructible.
- **F_gap:** physical semantics is deliberately unselected.
- **F_next:** choose exactly one semantics route with equations and falsifier;
  only then instantiate a versioned `GROWTH-CS2-001` candidate.
