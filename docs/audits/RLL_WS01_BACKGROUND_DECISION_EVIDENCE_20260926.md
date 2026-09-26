# RLL WS01 background decision evidence — 2026-09-26

## Scope

This delta attacks the evidence gap behind `RX-PHYSICS-CANONICAL-V2` without selecting scientific semantics from preferred fit quality.

It measures:

- sensitivity of H(z) to the two reproducible radiation-density conventions, `Omega_r=9.0e-5` and `9.18e-5`;
- row counts, hashes and redshift overlap of the two existing H(z) surfaces;
- deterministic distance-integral convergence under step refinement;
- an independent stdlib trapezoid cross-check against the existing Simpson implementation.

## Fail-closed boundary

This delta does **not** promote either H(z) surface, does **not** promote a growth proxy, and does **not** declare `RX-PHYSICS-CANONICAL-V2` closed.

`growth_mode` remains `TOKEN_VAZIO_UNTIL_WS06`.

Exact bibliographic row provenance and inclusion/exclusion authority for the 28-vs-33 H(z) surfaces remain required. Equality of redshift values is not sufficient evidence of source identity.

## Executor

`tools/rll_ws01_background_decision_evidence.py --write`

Output:

`artifacts/science/background/RLL_WS01_BACKGROUND_DECISION_EVIDENCE_V1.json`

The artifact is evidence for a later versioned scientific decision, not the decision itself.

## Falsification / stop rules

The delta must remain blocked if numerical refinement is unstable, the independent integrator disagrees beyond a preregistered tolerance, dataset provenance is ambiguous, or a downstream scientific dependency remains unresolved.

`claim_allowed=false`.
