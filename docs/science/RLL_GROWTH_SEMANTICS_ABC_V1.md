# RLL Growth Semantics A/B/C Comparator V1

**Date:** 2026-09-13  
**State:** `COMPARISON_EXECUTABLE / NO_PHYSICAL_WINNER`  
**Claim allowed:** false

## Purpose

Execute the three semantics routes under the same gate without choosing one by
preference.

### A — conserved effective fluid

Keep the versioned `rho_s(a)` and impose separate conservation:

[
p_{cons}=-ho_s-rac13rac{dho_s}{dln a}.
]

The executable comparator checks the residual and also records the canonical
kinetic-sign diagnostic (1+w_{cons}).

**Result:** survives the present mathematical gate. This does not establish a
canonical scalar, a rest-frame sound speed, or observational viability.

### B — interacting sector

Keep the historical documented pressure and reconstruct the background source:

[
rac{Q_s}{H}=Omega_{s0}ho_{c0}f'(1-a^{-3}).
]

An equal-and-opposite receiver closes the background accounting formally.

**Result:** the source relation survives algebraically, but the route remains
physically blocked because the receiving sector, covariant (Q^mu), momentum
transfer and perturbations are not implemented.

### C — phenomenological background

Keep the logistic (E^2(a)) only as a background map.

**Result:** operationally coherent and already compatible with the repository's
claim boundary, but it intentionally leaves physical `c_s^2` and new-sector
perturbations as `TOKEN_VAZIO`.

## Comparison result

There is **no unique physical winner** from current evidence.

Operational order:

```text
A_TEST_FIRST
→ B_IF_INTERACTION_IS_CHOSEN_OR_A_FAILS
→ C_SAFE_BACKGROUND_FALLBACK
```

Why A first? It introduces the fewest new structures before the next falsifier:
the pressure required by continuity is already determined by the versioned
density. That is an engineering/scientific-effort priority, not evidence that A
is the true ontology.

## Next gate after A

Do not promote A directly. Test:

1. transition regularity;
2. pressure perturbation/entropy closure;
3. gauge choice;
4. super-horizon initial conditions;
5. conservation residual;
6. then only a versioned `GROWTH-CS2-001` candidate.

B and C remain live rollback/fallback branches.

## R3

- **F_ok:** A, B and C are now executable/comparable under one contract.
- **F_gap:** none has enough evidence to become selected physical semantics.
- **F_next:** falsify A first because it is the smallest evidence-changing route; if it fails, move to B; C remains the safe non-microphysical boundary.
