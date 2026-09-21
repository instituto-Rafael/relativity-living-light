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


## Provider rerun addendum — 2026-09-21T04:53:25-03:00

**GitHub Actions run:** `35575013496`  
**Job:** `106254785513` — `success`  
**Head:** `6acf4cce54fb63e7a572a8c533d26df082ff8710`  
**Artifact:** `10627720366` — `rll-language-g123-20260921`  
**Artifact digest:** `sha256:dc418b94a4a4b87a60ba1448166bc0820fb40686b738a961368022c670666e82`

Provider summary:
- G1 = `PASS`;
- G2 strong_claim_pass = `False`;
- G3 = `PASS` under the corrected preregistered gate;
- UDHR = `ANALYSIS_RUN`.

Corrected G3 evidence observed in the provider log:
- independent-language shuffle: canonical beats 32/32, fraction 1.0, gate_pass_95pct=true;
- label permutation using the existing label multiset: canonical beats 32/32, fraction 1.0, gate_pass_95pct=true;
- workflow-level G3 status = PASS, which also requires the common-order family gate to pass.

Academic boundary: this restores `G3=PASS_CORRECTED_SCOPE` only for the declared corpus, zstd-19 metric, seed, 32 permutations per family and corrected null construction. It does not establish a universal semantic law, decipherment, physical entropy claim, or authorship.

Final bounded state for this branch:

```text
G1 = PASS
G2 = FAIL_STRONG_CLAIM
G3 = PASS_CORRECTED_SCOPE
UDHR reconstruction/control = EXECUTED_WITHIN_SCOPE
claim_allowed = false
science_global = TOKEN_VAZIO
decipherment = TOKEN_VAZIO
authorship = TOKEN_VAZIO
```

F_ok = corrected G3 rerun reproduced by GitHub Actions; artifact materialized with digest; G1 PASS and G2 FAIL preserved.  
F_gap = no global semantic/physical/authorship inference; overall PR merge readiness is not inferred from this one scientific workflow.  
F_next = keep PR #940 isolated for review; merge only by explicit human decision after reviewing unrelated repository-wide checks.  
