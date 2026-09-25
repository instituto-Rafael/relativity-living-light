# RLL Main Deployment Path V1 — 2026-09-25

**state:** `IMPLEMENTED_DRAFT / LAB_ENTRY`  
**claim_allowed:** `false`  
**publication_effect:** `NONE`

## Objective

Move RLL work toward `main` without bypassing the repository's existing
maturity topology or erasing negative evidence, narrow resolutions, provenance,
receipts, gaps or `TOKEN_VAZIO`.

The canonical route is:

```text
work/feature/science/research/engineering/governance/hotfix
  -> rll/lab
  -> rll/integration
  -> rll/release
  -> main
```

A feature/research branch must not jump directly to `main`.

## Current reconciled state

The current authority is the append-only V4 TOKEN_VAZIO reconciliation, not the
older 14-item registry alone.

Three historical gaps are already facts and must not be reopened:

- H0 primary-source provenance: `RESOLVED`;
- diverged/descendant ref semantic review: `RESOLVED`;
- external GitHub settings uncertainty: `RESOLVED_NEGATIVE`.

The last item is important: the settings were observed, and the observation
reported no branch protection/rulesets. The uncertainty closed as a negative
fact and produced the P0 successor
`TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT`.

## Current open denominator

The deployment registry contains exactly **12** open successor obligations:

- **P0: 5**
- **P1: 5**
- **P2: 2**

No resolved token is counted again.

## Execution waves

### Wave 0 — control plane

`TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT` is first because repository-local
YAML cannot prove server-side enforcement. Configure and then re-observe
rulesets/branch protection, required checks/reviews and bypass boundaries.

Until a fresh receipt proves this state, the deployment program does not call
`main` protected.

### Wave 1 — parallel uncertainty reduction

Run in parallel where resources permit:

- RLL perturbation closure;
- ACT DR6 LCDM posterior reproduction;
- H0 full-Boltzmann inference integration;
- DESI DR2 official joint reproduction;
- DES Y6 3x2pt materialization/reference reproduction;
- physical Termux execution.

Each item has its own branch name, receipt and closure conditions in
`data/governance/RLL_MAIN_DEPLOYMENT_PATH_20260925_V1.json`.

### Wave 2 — dependency-unlocked execution

Only after Wave 1 dependencies close:

- CLASS/CAMB dual RLL implementation after perturbation closure;
- real joint multi-probe Bayesian evidence after DESI + ACT + H0 gates.

### Wave 3 — independent/human authority

Independent replication is not satisfied by internal CI or another run by the
same production chain. It requires an independent operator/repository and
preserved disagreement if reproduction fails.

UTM185 physical replay and matched real-model ablation remain separate P2 work.

## Required promotion receipt per edge

Every edge must preserve:

```text
source head
base head
changed files
test status
workflow architecture/docs status
provenance/evidence files
negative evidence
TOKEN_VAZIO + F_next when still unresolved
claim_allowed=false
post-decision receipt
```

A PASS at one edge is not authority for the next edge without a fresh receipt.

## Necessary points outside the 12-token queue

### NP-001 — P0 GitHub enforcement

This is an external platform action, not something repository files can
self-certify.

### NP-002 — P1 license authority contradiction

The 2026-09-25 license reconciliation on `main` correctly preserves
`canonical_repository_license = TOKEN_VAZIO_CONTRADICTION`. Do not silently
rewrite it while promoting scientific work.

### NP-003 — P2 README rendering hotfix

The observed `main` README blob
`67b6c5579dea603d3e36620c154e57c45546eeb8` still contains literal
`\\n\\n` in the license notice. Fix it surgically on a dedicated hotfix
branch; do not mix the documentation correction with scientific semantics.

## What reaches main

A work item reaches `main` only when its own evidence/closure gates pass and
the chain has advanced successively through lab, integration and release.

```text
BRANCH_EXISTS != IMPLEMENTED
IMPLEMENTED != TESTED
TESTED != EVIDENCED
EVIDENCED != SCIENTIFIC_CLAIM
```

External, physical and human requirements stay open until their actual authority
exists.

## R3

**F_ok:** V4 state reconciled; 12 open successor obligations routed; narrow
resolutions and negative settings evidence preserved; urgency, branches,
receipts, dependencies and promotion topology are explicit.

**F_gap:** GitHub platform enforcement, six Wave-1 execution/materialization
items, dependency-unlocked CLASS/CAMB and multi-probe work, independent
replication, physical execution and two editorial/legal necessary points.

**F_next:** land this contract in `rll/lab` after gates; execute Wave 0 and
Wave 1; promote only resolved deltas one edge at a time with fresh receipts.
