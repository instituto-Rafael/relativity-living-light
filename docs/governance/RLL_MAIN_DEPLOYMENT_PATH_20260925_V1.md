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

Two narrow scientific/governance gaps are current resolved facts and must not
be reopened:

- H0 primary-source provenance: `RESOLVED`;
- diverged/descendant ref semantic review: `RESOLVED`.

The external GitHub settings record needs a temporal distinction. The
2026-08-08 probe is preserved append-only as a historical
`RESOLVED_NEGATIVE` observation. It is **not** projected forward as the
current provider state.

A new live observation from GitHub Platform Assurance V2, run
`36169792228`, job `108186255604`, artifact `10879902755`, reports:

```text
state = PARTIAL_EXTERNAL_SETTINGS_OBSERVED
branch_count = 4
branch_metadata_complete = true
protection_detail_complete = false
rulesets_observed = true
resolution_eligible = false
claim_allowed = false
```

Therefore:

```text
HISTORICAL_NEGATIVE_OBSERVATION != CURRENT_PLATFORM_STATE
WORKFLOW_SUCCESS != EXTERNAL_ENFORCEMENT_RESOLVED
```

The current P0 successor
`TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT` remains open because the current
authority is incomplete, not because the August state is assumed to persist.

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

This is an external platform authority boundary, not something repository
files can self-certify. The current live probe has complete branch metadata but
incomplete protection detail and is not resolution-eligible. A fresh complete
observation is required before the path may call `main` protected.

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

**F_ok:** historical V4 evidence preserved append-only; the 2026-09-25 live
platform observation is separately recorded; 12 open successor obligations are
routed; urgency, branches, receipts, dependencies and promotion topology are
explicit.

**F_gap:** current GitHub protection detail is incomplete and not
resolution-eligible; the Six Sigma derived documentation inventory is stale on
`rll/lab`; scientific/external/physical/human execution receipts remain open;
license authority and README rendering remain separate necessary points.

**F_next:** keep PR #991 draft while current platform authority and derived
inventory drift remain unresolved; execute ready Wave 1 work without claiming
main deployment; then advance only resolved deltas one edge at a time with
fresh receipts.
