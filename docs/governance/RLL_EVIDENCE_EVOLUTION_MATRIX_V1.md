# RLL Evidence Evolution Matrix V1

**Date:** 2026-09-13  
**State:** DRAFT_AUDITABLE  
**Claim allowed:** false

## Purpose

Add one thin control projection over existing RLL ledgers. It does not replace
`RLL_GAP_RETROFEEDBACK_V2.json`, `RLL_GAP_DECOMPOSITION_V1.json`, receipts,
or producer-specific scientific artifacts.

Each major active RLL lane must expose seven guards:

1. provenance;
2. context;
3. evidence;
4. contradiction;
5. uncertainty;
6. reproduction;
7. rollback.

## Why this is an evolution

RLL already tracks source/evidence/falsifier/rollback across many gaps. The
remaining risk is uneven visibility: one lane may be strong in provenance but
weak in explicit reproduction; another may preserve evidence but hide a
contradiction in prose. This projection makes the same seven questions
machine-readable across major domains without duplicating the full gap ledger.

## Current seven workstreams

| Domain | Current state | Main evolution |
|---|---|---|
| background | EVIDENCED_FOCUSED | preserve flat closure and historical path |
| CMB | VERIFIED_LIMITED | keep bounded CAMB benchmark reproducible |
| growth | NEGATIVE_EVIDENCE_DECOMPOSED | resolve continuity semantics first; then GROWTH-CS2-001 |
| real_data | VERIFIED_LIMITED | preserve provenance supersession and rerun successor later |
| inference | BLOCKED_BY_DEPENDENCY | no MCMC/model-selection promotion yet |
| magneto_plasma | TOKEN_VAZIO_FORMALIZATION | require equations, units, observable and falsifier |
| literature | POLICY_IMPLEMENTED_WITH_OPEN_GAPS | primary-source verification before write integration |

## Fail-closed rules

- projection never promotes `claim_allowed=true`;
- negative evidence is preserved;
- contradiction is not silently deleted;
- reproduction procedure must be explicit even when blocked;
- rollback must have an anchor and a reversible procedure;
- contextual corpus is not physical evidence;
- source-reported evidence is labeled as source-reported unless independently rerun.

## Best next scientific delta

`GROWTH-CS2-001`.

The current negative sweep already blocks silently inheriting
`c_s^2=c_a^2` as a universal/default perturbation policy. The next useful
change is one versioned rest-frame sound-speed/entropy candidate with explicit
stability, causality and conservation falsifiers.

That candidate must not be promoted as a derived RLL property.

## Validation

```bash
python tools/validate_rll_evidence_evolution_matrix.py
python -m unittest -v tests.test_rll_evidence_evolution_matrix
```

## R3

- **F_ok:** seven major lanes are projected onto the same seven guards.
- **F_gap:** growth, successor fit, inference, magneto-plasma and literature runtime/license gates remain open.
- **F_next:** implement the smallest evidence-changing growth child, then recompute the projection.
