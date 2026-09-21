# ADDENDUM — MU-RLL-G123-G3-METHOD-CORRECTION-20260921

**Autor:** RAFAEL MELO REIS  
**Estado:** `PROPOSED_CORRECTION / RERUN_REQUIRED / claim_allowed=false`  
**Parent:** `MU-RLL-G123-SEED-COMPRESSION-NULL-20260921`  
**Source PR:** #939 (merged)  
**Correction branch:** `audit/g123-null-gate-correction-20260921`

## Reason for supersession

Post-run review identified methodological confounds in the original G3 implementation:

1. null-family `scope` strings changed measured serialized metadata;
2. label "permutation" replaced labels with new random strings instead of permuting the existing labels;
3. generated-label uniqueness used set iteration, weakening deterministic replay;
4. the implemented pass condition used a plus-one Monte Carlo p-value instead of the preregistered "canonical beats >=95% of each null family" criterion.

Therefore the earlier G3 PASS is not used as final academic evidence until a corrected provider rerun completes.

## Bounded correction

- keep serialized scope/metadata constant across null families;
- permute the existing reference labels, preserving their exact multiset;
- remove set-derived generated labels;
- gate directly on the preregistered >=95% beat fraction;
- ties are not counted as canonical wins;
- retain empirical p-value as descriptive output only.

## Unchanged states

- G1 reconstruction: prior PASS is not modified by this correction.
- G2 strong compression claim: prior FAIL is preserved.
- UDHR reconstruction/control: prior result is not promoted beyond its executed scope.
- universal semantics, physical interpretation, decipherment and authorship remain `TOKEN_VAZIO`.
- `claim_allowed=false`.

## Gate

`G3 = REVIEW_REQUIRED / INCONCLUSIVE` until corrected GitHub Actions provider evidence is observed.

## R3

F_ok = branch-isolated correction materialized; G1 PASS preserved; G2 FAIL preserved.
F_gap = corrected G3 provider rerun and final artifact/receipt.
F_next = run pull-request CI on this branch, inspect artifact and only then append a successor receipt.
