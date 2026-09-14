# RLL Cross-Domain Equation Intake Contract

Status: `QUARANTINED_REFERENCE_LAYER`  
Schema: `rll.cross_domain_equation_intake.v1`  
Claim boundary: `claim_allowed=false`

## Purpose

This layer receives equations from adjacent domains without allowing them to alter RLL cosmological inference. It preserves useful mathematics while preventing category errors, metaphor promotion, dimensional leakage and citation laundering.

The registry is not a unified theory and is not evidence for RLL. A record marked `[E]` means the mathematical relation is exact within its declared assumptions; it does not mean the relation is empirically relevant to cosmology.

## Components

```text
docs/science/RLL_CROSS_DOMAIN_EQUATION_RISK_ASSESSMENT.md
docs/science/RLL_CROSS_DOMAIN_EQUATION_INTAKE.md
data/contracts/cross_domain_equation_intake.v1.json
schemas/rll_cross_domain_equation_intake.schema.json
tools/validate_cross_domain_equation_intake.py
tests/test_cross_domain_equation_intake.py
artifacts/cross-domain-equation-intake/
```

## Epistemic classes

| Class | Meaning | Promotion effect |
|---|---|---|
| `[E]` | Exact mathematical identity or established relation under stated assumptions | None |
| `[M]` | Scientific or computational model with domain-dependent assumptions | None |
| `[H]` | Testable hypothesis requiring falsifier, predicted observation and promotion gate | None until independent evidence |
| `[P]` | Analogy or symbolic representation | Permanently none |

## Fail-closed invariants

1. Global and per-record `claim_allowed` are always false.
2. Direct model integration is always false.
3. No quarantined equation may affect cosmological evidence.
4. Non-cosmology records are reference-only or out-of-scope.
5. Protected RLL scientific paths cannot be integration targets.
6. `[P]` records cannot become test targets.
7. `[H]` records without falsifiers are invalid.
8. Source uncertainty remains explicit as `TOKEN_VAZIO`.
9. PASS counts cannot compensate for one failed boundary.
10. A green receipt validates governance structure, not physical truth.

## Protected paths

The registry currently protects the cosmology model, likelihood, MCMC, Bayes, canonical CI results and real cosmology data. This prevents an equation catalogue from silently changing evidence-bearing code.

## Execution

```bash
python tools/validate_cross_domain_equation_intake.py --strict --write-report
PYTHONPATH=src:. python -m pytest -q tests/test_cross_domain_equation_intake.py
```

The validator writes:

```text
artifacts/cross-domain-equation-intake/validation.json
artifacts/cross-domain-equation-intake/VALIDATION.md
artifacts/cross-domain-equation-intake/CHECKSUMS.sha256
```

## Current state

All initial records are quarantined. Primary-source chains remain `TOKEN_VAZIO` until verified inside the repository. No record is `READY_FOR_TEST`, no integration target is active and no RLL scientific claim is promoted.

## Promotion protocol

A record can only move toward an isolated test through a separate reviewed change that provides:

- verified primary-source chain;
- dimensional mapping;
- isolated non-cosmology target;
- baseline and null model;
- preregistered falsifier;
- predicted observation;
- uncertainty model;
- rollback path;
- independent review.

Even then, promotion affects only the isolated experiment. It cannot alter RLL cosmological claims without passing the independent cosmology falsifier contract.
