# RLL Scientific Infinity & Open Evolution Protocol

**Status:** structural method, claim-bounded  
**Date:** 2026-07-17  
**Scope:** convert symbolic infinity into finite, measurable and auditable scientific operations.

## 1. Boundary

The repository may represent mathematical limits, potentially unbounded research programs and open-ended evolutionary searches. Every concrete run remains finite:

\[
\mathrm{Run}_N=(\text{code},\text{inputs},\text{seed},\text{budget},\text{outputs},\text{hash}),\qquad N<\infty.
\]

This protocol does **not** establish that the physical Universe is infinite, that a process can compute without limit, that novelty proves intelligence, or that RLL is cosmologically valid.

## 2. Vocabulary

| Code | Meaning | Scientific use |
|---|---|---|
| `infinity_math` | formal mathematical infinity | limits, cardinality, series, asymptotics |
| `infinity_potential` | process without a fixed final horizon | future observations, iterative refinement |
| `infinity_physical` | physically infinite space/time/density | hypothesis; remains `TOKEN_VAZIO` without evidence |
| `infinity_computational` | non-termination or unbounded state space | risk requiring budgets and cycle detection |
| `infinity_evolutionary` | sustained production of non-repeating novelty | measurable research hypothesis |
| `TOKEN_VAZIO` | missing or non-demonstrated information | explicit epistemic state, never positive evidence |

The classes are intentionally non-equivalent:

\[
\infty_M\neq\infty_P\neq\infty_F\neq\infty_C\neq\infty_E\neq\varnothing.
\]

## 3. Seven analytical operators

The earlier symbolic seven-axis map is preserved, but translated into operational language:

| Axis | Operational meaning | Minimum measurement |
|---|---|---|
| accumulation | aggregate versioned evidence | source count, covariance, duplicate control |
| differential | sensitivity to parameters/data | derivative, finite difference, Fisher/Jacobian |
| inverse | infer parameters from observations | likelihood, priors, degeneracy report |
| progression | add data or model capability | state delta and versioned result |
| recursion | feed measured output into next cycle | iteration budget, state digest, rollback |
| contradiction | expose failing predictions | unresolved contradiction count and falsifier |
| decomposition | separate signal, residual and noise | residual model, covariance, filter/deconvolution |

The word “antiderivative” may remain as didactic symbolism; code and papers must use the operational term actually implemented.

## 4. Guarded cycle

`src/rll/scientific_infinity.py` defines:

- `InfinityClass` — prevents semantic collapse of distinct infinities;
- `GuardPolicy` — maximum iterations, timeout, convergence, novelty, evidence, duplication and contradiction gates;
- `EvolutionObservation` — one measured state;
- `assess_evolution` — returns a finite decision;
- `evolution_score` — evidence-weighted novelty with duplication/contradiction penalties;
- `stable_digest` — deterministic SHA-256 state identity.

Allowed decisions:

```text
continue
converged
cycle_detected
budget_exhausted
TOKEN_VAZIO
```

No structural decision promotes `claim_allowed=true`.

## 5. Evolution score

For cycle `n`:

\[
E_n=\frac{B_nR_nV_n}{1+\lambda D_n+\mu C_n},
\]

where:

- `B_n` = measured novelty;
- `R_n` = feedback quality;
- `V_n` = evidence strength;
- `D_n` = duplication ratio;
- `C_n` = unresolved contradictions.

This is a governance score, not a cosmological observable. It cannot be inserted into a physical likelihood without a separate derivation and validation.

## 6. Stop and gap rules

A run must stop or downgrade when:

1. `iteration >= max_iterations`;
2. `elapsed_seconds >= timeout_seconds`;
3. a previous `state_digest` repeats;
4. duplication exceeds the configured threshold;
5. evidence is below its floor;
6. unresolved contradictions exceed the policy;
7. objective convergence occurs with negligible novelty.

Weak evidence or unresolved contradiction maps to `TOKEN_VAZIO`, not to confirmation or refutation.

## 7. Machine contract

- Schema: `schemas/scientific_infinity_cycle.schema.json`
- Example: `schemas/examples/scientific_infinity_cycle.example.json`
- Validator: `scripts/validate_scientific_infinity_cycle.py`
- Tests: `tests/test_scientific_infinity.py`
- CI: `.github/workflows/validate-schema-contracts.yml`

The schema requires `mode=finite_budgeted` and `claim_allowed=false`.

## 8. RLL application

Recommended use in future RLL pipelines:

```text
observation
→ stable digest
→ novelty/evidence/duplication/contradiction metrics
→ finite guard decision
→ result artifact
→ independent scientific likelihood/falsifier
```

The finite guard does not replace MCMC convergence diagnostics, nested-sampling error estimates, physical stability tests, covariance checks, peer review or independent replication.

## 9. Claim boundary

Allowed:

> The run explored an open-ended research space under finite budgets and recorded convergence, cycling, budget exhaustion or an evidence gap.

Blocked:

> The run proves physical infinity, unlimited computation, consciousness, universal evolution or RLL validity.

## 10. Retroalimentação

- `F_ok`: symbolic infinity now has a typed, finite and testable computational translation.
- `F_gap`: physical infinity and open-ended evolution remain hypotheses unless independently measured.
- `F_next`: attach the guard artifact to long-running search/optimization pipelines without replacing their domain-specific scientific diagnostics.
