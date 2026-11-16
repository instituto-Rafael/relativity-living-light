# RLL — Academic False-Positive Gate V1 — Receipt

Date: 2026-10-04
State: IMPLEMENTED_UNTESTED
Claim: `claim_allowed=false`
Base: `rll/lab@d8ba8fb3d8fa10bab3fcc190fcc749dec91ba3b6`
Branch: `audit/academic-false-positive-gate-v1-20261004`

## Intent

Prevent a technically successful or numerically favorable screening result from being promoted into an academic/scientific claim without confirmatory controls.

Invariant:

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
screening_positive != confirmatory_ready != scientific_truth
TOKEN_VAZIO != 0
IMPLEMENTED_UNTESTED != PASS
```

## Source minimum / authority

RLL producer authority:
- `instituto-Rafael/relativity-living-light`
- existing `docs/RLL_ROBUST_FIT_CHECKLIST.md`
- existing `tools/validate_claim_allowed_gate.py`
- existing `tools/rll_atlas_evolution_gate.py`

Mathematical source routes consulted without importing a physical claim:
- Google Drive `START HERE — MATEMÁTICA E GEOMETRIA — EXPRESSÕES`, document `1GjCnyvGoZJLxTLdr9vlZ7aK1maOpScilzTmZLWETwwg`;
- `rafaelmeloreisnovo/Matem-tica-/docs/formal/PITAGORAS_BHASKARA_ISOSCELES_POINCARE_CROSSWALK_V1.md`;
- `rafaelmeloreisnovo/Matem-tica-/papers/2026-08-18_omega7_modular_geodesic_toroidal_focus.md`.

## Materialized delta

- unbiased sample variance `s^2=sum((x-xbar)^2)/(n-1)` and estimated variance of the mean `s^2/n`;
- independent difference-of-means variance `s1^2/n1+s2^2/n2`;
- OLS line plus residual dispersion;
- dispersion buffer `z*s` typed as `STATISTICAL_ANALOGY_ONLY`, not a cosmological law;
- rational geometry sidecar preserving primitive ratio plus GCD scale, so `77/33` retains scale 11 and `777/333` scale 111 instead of collapsing into bare `7/3`;
- modular signatures over `{3,5,7,10,14,30,50,70}`, where numeric zero is a residue, not `TOKEN_VAZIO`;
- Pitagorean difference identity and signed quadratic/Bhaskara discriminant classifier;
- 30-degree isosceles and circular-section projections while keeping `sqrt(3)/2*r` distinct from `3/2*r` constructions;
- ideal Venturi/Bernoulli reference model typed `REFERENCE_MODEL_ONLY`;
- `(3/2)^n`, `pi*phi`, `ln(ln(999))`, `sqrt(3)/2`, `sin(30)` retained as `EXPLORATORY_FEATURE_ONLY` with no equality or physical binding inferred;
- fail-closed confirmatory gate requiring preregistration, frozen primary metric, negative controls, complete baselines, robust fit, uncertainty, ablation, holdout/external validation, external backend/equivalent, independent replication, complete provenance, no post-hoc parameter change, plus a declared multiplicity policy.

## Academic false-positive boundary

AIC/BIC/chi2 or any geometric/modular coincidence may nominate a candidate for confirmation. They do not independently establish physical truth.

A positive RLL claim is blocked unless confirmatory evidence is materialized. P-values, information criteria, modular matches, geometric similarity and regression fit are different evidence classes and are not interchangeable.

## Known residual gap

The legacy in-memory function `data/pipelines/structure_d/synthetic_real_boundary.py::enforce_claim_boundary` can still return `claim_allowed=true` from favorable RLL-vs-LCDM information-criterion thresholds alone. V1 adds a repository-level validator that rejects serialization/promotion without `confirmatory_evidence`, but the legacy function itself still requires a successor refactor to make the in-memory boundary equally fail-closed.

Nested technical readiness flags named `claim_allowed`, such as covariance readiness, remain a semantic-collision risk and should later be renamed to scope-specific readiness flags without rewriting historical artifacts.

## Evidence target

CI must execute:

```text
PYTHONPATH=src python -m unittest tests.test_academic_false_positive_gate -v
PYTHONPATH=src python tools/validate_academic_false_positive_gate.py
```

Until CI executes on the exact branch head:

```text
state = IMPLEMENTED_UNTESTED
claim_allowed = false
```

## R3

```text
F_ok   = anti-false-positive statistical/geometric diagnostics and confirmatory validator materialized
F_gap  = exact-head CI receipt; legacy in-memory claim promotion; scoped readiness naming
F_next = execute PR CI; fix any failure; then refactor in-memory claim promotion as a separate reversible successor
```
