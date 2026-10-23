# RLL research intake — Σ_RAFAELIA v1.1, triangular torus and typed void

**Date:** 2026-10-23. **Source author / scope:** Rafael Melo Reis (∆RafaelVerboΩ); AI-assisted mathematical audit.  
**State:** BRIDGE_ONLY / NOT_COUPLED / NO_PHYSICAL_CLAIM / NON_PROMOTABLE_DRAFT. `claim_allowed=false`, `release_allowed=false`.

## Route and producers

- Formal mathematical producer: `rafaelmeloreisnovo/Matem-tica-` PR [#78](https://github.com/rafaelmeloreisnovo/Matem-tica-/pull/78), which supplies a stdlib-only oracle and explicit finite tests.
- Scientific discussion: `rafaelmeloreisnovo/papers` PR [#147](https://github.com/rafaelmeloreisnovo/papers/pull/147).
- RLL canonical branch route: WORK -> `rll/lab` -> integration -> release -> main, independently governed; existing PR #1124/#1125 and their inventories are **not changed by this delta**.
- Prior RLL note `docs/research/OMEGA7_MODULAR_GEODESIC_TOROIDAL_FOCUS_20260818.md`; do not replace its modular `7/14/10` focal hypotheses with this unrelated mapping.
- Source of 200 expressions and seven operators: author's 2026-10-23 B/C formulation; **no assertion of 200 new results**.

## Optional adapter contract (not an activated adapter)

```text
input  = ObservedState(lift[N,d], mask[N], source SHA, units, geometry ID)
         + separately measured U[N,d] + n + declared parameters
output = FormalResult(projected[N,d], lift_next[N,d], mask_next[N],
                      finite_gate_receipt, warnings, claim_allowed=false)
```

The triangular quotient has basis `B=[[1,0.5],[0,sqrt(3)/2]]`; a *lifted* computational transition is `Z_(n+1)=(q^n Z_n R_n^T+F_leq(n)U_n)E_n^T`. The `P_Λ` operation selects a representative of `R²/BZ²`; unlike a physical transport operator, `q=sqrt(3)/2` is **not** intrinsically well-defined on the quotient without selecting the lift. No input-to-observable map for an RLL spacetime/optical/cosmological quantity has been specified.

`TOKEN_VAZIO != 0`: a tagged missing entry must not become observed zero or physical density/energy. Token `t_empty` is a *display placeholder*, never observed forcing; the only admissible forcing is separately sourced and measured `U`. Missing rows forbid observed forcing until observation/custody is established. Masked outputs retain missing status. This bridge adds neither model parameter to a fit nor changes RLL science defaults.

## Eight gating requirements before future physical coupling

1. **Source and authority:** immutable mathematical SHA, independent review, reconciled PR #78/#147 state.
2. **Geometry:** identify whether the RLL observable is on a flat quotient, a curved embedded torus or spacetime; metric and units are required.
3. **Observability:** define an actual physical scalar/vector target and its data custody; `TOKEN_VAZIO_OBSERVABLE` until measured.
4. **Null baseline:** compare with identity, square lattice, triangular lattice without forcing, and null model at same degrees of freedom.
5. **Convergence:** scoped nonautonomous stability proof under bounded `E_n`, `U_n`, no point-fixed claim from idempotence.
6. **Numerical gate:** deterministic positive/negative fixtures, overflow/roundoff/mask adversarial checks, exact-head CI.
7. **Independent review:** domain scientist checks source, physical identifiability, statistical methodology, held-out predictions.
8. **Provider/release:** branch policies, RLL exact-head CI and external governance; current unrelated CI gaps persist.

The parametrization `Φ_ethica` is neither an ethical guarantee nor a physical constraint derived from measurements. Historical calendars and sacred narratives from the 200-expression corpus are not inputs to RLL field equations.

## R3, provenance and rollback

F_ok: boundary documented without touching physics code, workflow inventories, datasets, coefficients or model claims. F_gap: `TOKEN_VAZIO_OBSERVABLE`, `TOKEN_VAZIO_PHYSICAL_COUPLING`, `TOKEN_VAZIO_INDEPENDENT_REVIEW`, `TOKEN_VAZIO_EXACT_HEAD_CI`, `TOKEN_VAZIO_PROVIDER_AUTHORITY`. F_next: wait for mathematical unit gate receipts, then design **one falsifiable RLL observable** with external baseline; do not auto-integrate. Rollback by reverting this one research note on its branch while retaining provenance in Git history. SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM; claim_allowed=false.
