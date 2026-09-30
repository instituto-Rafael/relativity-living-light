# RLL χ² Symbol Source Binding — 2026-09-06 V1

Status: `SOURCE_OBSERVED`
Scope: close only the previously open ambiguity `residual vs Jacobian` for the current Pantheon+ evidence runner.
No cosmological claim is promoted by this receipt.

## Source identity

- repository: `instituto-Rafael/relativity-living-light`
- observed source commit: `3b3a4597ee49f3b5a0f5014b051668a30504aa65`
- path: `products/rll-evidence-runner/src/rll_evidence/pantheon_fit.py`
- observation date: `2026-09-06`

## Binding observed in executable source

The implementation constructs the data-model difference, profiles the nuisance magnitude offset, and computes

```text
profiled_residual = difference - m_b_hat
weighted_residual = C^-1 * profiled_residual
chi2 = profiled_residual @ weighted_residual
```

Therefore, for this implementation and scope:

```math
chi^2 = r^T C^{-1} r.
```

The numerical derivative `d_residual` is used when constructing the optimizer gradient. It is not substituted for the residual vector in the χ² quadratic form.

## Closed gap

```yaml
claim_id: C-20260906-011
previous_state: OPEN_GATE / SUPERSEDED_INTERPRETATION
current_subclaim_state: SOURCE_OBSERVED
bound_semantics:
  chi2_operand: profiled_residual
  jacobian_role: numerical derivative used in gradient
claim_allowed:
  current_source_semantics: true
  statistical_correctness_beyond_source_inspection: false
  cosmological_validation: false
```

## Reciprocal provenance

```text
Mapa:C-20260906-011
  -> RLL source receipt (this file)
  -> executable source pantheon_fit.py@3b3a4597...
  <- papers evidence-alignment note §3.1
  <- Matem-tica formal-corrections note §9
```

The reciprocal direction is mandatory: consumers may cite this receipt, and this receipt records the upstream claim IDs/notes that required the inspection.

## Remaining TOKEN_VAZIO

- independent reproduction of the full Pantheon+ run;
- exact dataset/covariance hashes for any result not already accompanied by a receipt;
- runtime/device evidence where separately claimed;
- external-data validation of RLL.

These remain unresolved and are not inferred from source readability.

## Urgency

`P0-CLOSED`: symbol ambiguity in the current source.

`P1-OPEN`: deterministic reproduction with data hashes and command receipt.

## Non-regression invariant

`SOURCE_OBSERVED != TEST_PROVEN != RUNTIME_PROVEN != EXPERIMENT_PROVEN`.
