# RLL Fork Authority & Lineage — 2026-08-27 V1

**status:** AUDIT / APPEND_ONLY  
**claim_allowed:** false  
**canonical_repository:** `instituto-Rafael/relativity-living-light`  
**workspace_fork:** `rafaelmeloreisnovo/relativity-living-light`

## 1. Authority rule

The Instituto repository is the canonical scientific authority for RLL. The personal repository is a convenience/access/workspace fork and may contain candidate contributions, experiments, receipts, or temporary integration work.

Invariants:

`FORK_COMMIT != CANONICAL_SCIENTIFIC_STATE`

`AHEAD_COUNT != SAFE_UPSTREAM_DELTA`

`WORKSPACE_PASS != CANONICAL_REPRODUCTION`

`FORK_HISTORY != AUTHORITY_OVERRIDE`

A contribution becomes canonical only after it is reconciled against the current Instituto lineage, tested under the applicable gate, and accepted through the Instituto review/merge path.

## 2. Observed snapshot

At the observed comparison:

- canonical main: `a88d184a73ba2ffeebfc7245f630b72ea3f81bca`;
- workspace main: `c8c1ba72ed27ce5f8972ffa6d80864f0e4fe8f4a`;
- merge base: `3191a1d289db28b09b155b4b9eba62a32ad90005`;
- workspace relative to canonical main: **54 commits ahead / 922 commits behind**;
- relation: `DIVERGED`.

Therefore the 54 commits MUST NOT be bulk-merged, force-synced, or interpreted as one coherent upstream patch.

## 3. QCD primordial reconciliation

The personal fork materialized PR #25 (`RLL: materializar QCD Primordial Gate + PSPI de proveniência`). This is useful historical/candidate lineage, but the Instituto subsequently materialized a deeper canonical QCD/primordial sequence through PRs #770, #771 and #772 on the Instituto integration line, including stronger provenance, g-star treatment, B/P boundaries, BBN+CMB gates, and preserved `FULL_RLL_PRIMORDIAL_VERDICT=TOKEN_VAZIO` / `claim_allowed=false` boundaries.

Classification for the personal QCD block:

`PERSONAL_PR25_QCD -> SUPERSEDED_AS_DIRECT_UPSTREAM_CANDIDATE_BY_CANONICAL_DESCENDANTS`

This classification means **do not cherry-pick PR #25 wholesale**. It does not erase the personal history. Any individual file/idea still missing from the canonical lineage must be proven missing by path/blob/semantic comparison before transplantation.

## 4. Non-regressive upstream procedure

For each workspace-only candidate:

1. bind `source_repo/ref/path/blob`;
2. locate current Instituto authority for the same topic;
3. classify as `ALREADY_CANONICAL | CANONICAL_DESCENDANT_EXISTS | UNIQUE_CANDIDATE | CONFLICTING | TOKEN_VAZIO`;
4. for `UNIQUE_CANDIDATE`, transplant only the minimal coherent delta onto a branch created from the current Instituto authority;
5. execute domain-specific tests/falsifiers;
6. persist stdout/stderr/exit status, hashes and receipt where applicable;
7. open a draft Instituto PR;
8. never update canonical claims solely because the workspace version passed.

## 5. Current candidate families from the 54-ahead comparison

The comparison exposes candidate surfaces including strong-gravity/Floquet material, ARM32 evidence/indexes, navigation/route-forest changes, Sigma-E/fission material-field documentation, Tier-17 skills, workflow changes, and QCD primordial files.

Except for the QCD family classified above, these remain:

`TOKEN_VAZIO_NOT_YET_SEMANTICALLY_RECONCILED`

Filename presence or absence alone is not enough to promote them.

## 6. Gap contract

### `TV-RLL-FORK-54-BULK-TRIAGE-20260827`

- `source_pointer`: `rafaelmeloreisnovo/relativity-living-light@c8c1ba72ed27ce5f8972ffa6d80864f0e4fe8f4a`
- `missing_field`: per-candidate canonical-equivalence/descendant classification
- `blocking_dependency`: current Instituto path/blob/semantic comparison
- `evidence_needed`: source blob + canonical candidate blob + lineage + test/receipt where executable
- `falsifier`: canonical equal/newer implementation already covers the candidate semantics
- `next_probe`: bulk classify the 54-ahead changed paths by topic and canonical descendant
- `owner_authority`: `instituto-Rafael/relativity-living-light`
- `urgency`: P1
- `closure_gate`: every candidate is classified and every `UNIQUE_CANDIDATE` has an Instituto PR/receipt or explicit defer reason
- `claim_allowed`: false

### `TV-RLL-FORK-MAIN-DRIFT-PREVENTION-20260827`

- `source_pointer`: personal fork governance
- `missing_field`: server-side prevention of accidental canonicalization in the fork
- `blocking_dependency`: branch protection/ruleset authority if available
- `evidence_needed`: observed enforcement configuration or equivalent provider gate
- `falsifier`: fork main remains freely promotable without any failing authority guard/server policy
- `next_probe`: merge/review the fork-side authority guard and inspect server enforcement separately
- `owner_authority`: repository administration
- `urgency`: P1
- `closure_gate`: fork workflow plus provider-side enforcement observed, or documented residual risk if provider enforcement is unavailable
- `claim_allowed`: false

## 7. Memory projections

- **L / longitudinal:** personal fork remains historical contributor lineage; Instituto remains canonical evolution line.
- **O / orthogonal:** candidate code must be validated against current Instituto tests and evidence independently of fork success.
- **T / transversal:** Mapa/consumers should point to Instituto producer refs, using fork refs only as provenance for candidate contributions.
- **C / contextual:** 54-ahead is meaningful only together with 922-behind and merge-base `3191a1d...`.
- **P / permanent:** preserve both repositories and receipts; never erase the fork history to make the graph look linear.

## 8. F_next

Bulk-first classify the non-QCD 54-ahead surfaces. Prioritize executable/evidence-bearing families before documentation-only families. For each unique candidate, create the smallest Instituto branch/PR that can be tested without importing stale history.

**F_ok:** canonical authority resolved; dangerous `54 ahead => safe upstream` inference rejected; QCD direct cherry-pick prevented because canonical descendants already exist.  
**F_gap:** non-QCD 54-ahead candidates remain individually unreconciled; server-side fork drift prevention remains partially open.  
**F_next:** classify 54-ahead by topic → canonical path/blob/semantic comparison → transplant only proven unique deltas → tests/receipts → Instituto draft PR.
