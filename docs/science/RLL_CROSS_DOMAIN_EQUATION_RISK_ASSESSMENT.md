# RLL Cross-Domain Equation Intake — Preventive Risk Assessment

Status: `PRE_IMPLEMENTATION_REVIEWED`  
Decision date: `2026-07-20`  
Claim boundary: `claim_allowed=false`  
Scope: governance and validation only; no cosmological model code is changed by this assessment.

## Decision

The equations discussed across bioelectricity, electromagnetism, coupled oscillators, signal processing, geometry, fractals and neural attention may be useful as a reference catalogue, but they must not be inserted directly into the RLL cosmological likelihood, background evolution, MCMC, evidence or falsifier pipelines.

The safe implementation is a fail-closed intake contract that:

1. records each equation with domain, epistemic class, assumptions and limitations;
2. distinguishes mathematical validity from empirical relevance to RLL;
3. blocks direct coupling to cosmological inference paths;
4. requires a falsifier before any hypothesis can become test-ready;
5. preserves `claim_allowed=false` independently of catalogue completeness;
6. emits an auditable validation receipt.

## Risks observed before implementation

| ID | Risk | Severity | Preventive control |
|---|---|---:|---|
| `R-CDI-01` | Domain leakage: a valid equation in biology or signal processing may be presented as evidence for cosmology. | Critical | Non-cosmology entries are reference-only and direct model integration is forbidden. |
| `R-CDI-02` | Category error: `[E]` mathematical exactness may be confused with empirical confirmation. | Critical | Validator requires an explicit `epistemic_boundary` and blocks promotion by class alone. |
| `R-CDI-03` | Metaphor promotion: toroidal, golden-ratio or deterministic language may be converted into physical claims. | High | `[P]` entries cannot carry falsifiers, predictions or evidence effects; `[H]` entries require all three gates. |
| `R-CDI-04` | Unit and variable ambiguity may produce dimensionally invalid coupling. | High | Every record requires variable definitions, assumptions and dimensional notes. |
| `R-CDI-05` | Scope creep may alter `H(z)`, likelihood, priors, MCMC or Bayes evidence without an isolated experiment. | Critical | Protected path prefixes are declared and checked; integration remains blocked. |
| `R-CDI-06` | Citation laundering: an equation name may be treated as a verified source chain. | High | Source status is explicit; `TOKEN_VAZIO` remains acceptable but cannot support promotion. |
| `R-CDI-07` | Silent claim escalation through aggregate PASS counts. | Critical | Aggregation is non-compensatory; the global claim gate is constant false. |
| `R-CDI-08` | Irreversible or hard-to-review change. | Medium | Work is isolated on a dedicated branch and draft PR; no existing scientific result is rewritten. |
| `R-CDI-09` | A validator may report green while omitting semantic hazards. | High | Adversarial tests mutate domain, class, integration permission, source status and protected targets. |
| `R-CDI-10` | CI expansion may destabilize canonical workflows. | Medium | Reuse the existing schema-contract workflow; add one bounded step and one bounded artifact. |

## Protected scientific surfaces

The intake contract must not authorize writes or semantic promotion into these surfaces:

```text
src/rll/cosmology.py
src/rll/model.py
src/rll/likelihood.py
scripts/joint_mcmc.py
scripts/bayes_analysis.py
scripts/compute_bayes_factor_bic_proxy.py
results/ci/
data/real/cosmology/
```

A future experiment may read a quarantined equation only after a separate proposal defines:

- a cosmological mapping with units;
- a baseline and null model;
- a preregistered falsifier;
- an isolated output path;
- evidence provenance;
- rollback conditions;
- independent review.

## Safe acceptance criteria

Implementation is acceptable only when all conditions below hold:

- the schema validates under JSON Schema Draft 2020-12;
- all record IDs are unique;
- all records preserve `claim_allowed=false`;
- no non-cosmology record allows direct model integration;
- `[H]` records have falsifier, predicted observation and promotion gate;
- `[P]` records cannot affect evidence;
- protected targets are absent from integration targets;
- source gaps remain explicit;
- the validator exits non-zero under `--strict` on any violation;
- tests demonstrate fail-closed behavior.

## Rollback boundary

The change is additive. Reversal consists of removing the intake schema, registry, validator, tests, documentation and the bounded workflow step. Existing cosmological code and canonical result artifacts remain byte-independent from this feature.

## Conclusion

`APPROVE_FOR_QUARANTINED_IMPLEMENTATION` — governance-only, fail-closed, reversible, and without scientific claim promotion.
