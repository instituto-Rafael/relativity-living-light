# Relativity Living Light — Federated Repository Contract v1

**Federated role:** scientific claim validation, real-data workflows, falsification and evidence custody.  
**Local authority remains:** canonical RLL documents, claim-gated architecture, traceability map, real-data workflow, datasets/results and evidence ledgers.

## Concrete interface

```text
input: atomic scientific claim + model version + real dataset + statistical protocol
output: VERIFIED | TESTED | PARTIAL | TOKEN_VAZIO | CONTRADICTION | BLOCKED
```

The federation may route evidence and display status. It cannot validate a physical claim, select a preferred model or transform authorial anteriority into empirical confirmation.

## Non-negotiable invariants

1. Metaphor, mathematical definition, implementation, fit result and physical interpretation remain separate layers.
2. Real-data claims use the repository's canonical real-data workflow and identify dataset version/checksum.
3. Synthetic/mock/fixture/demo data cannot support real-data claims.
4. Priors, likelihood, parameters, seed, convergence checks and comparison baseline are explicit.
5. A lower chi-square alone does not prove a theory; complexity penalties/evidence and uncertainty remain visible.
6. Historical tags prove chronology/content, not physical truth.
7. Missing external metadata, dataset, execution or review is `TOKEN_VAZIO`.

## Ordered gates

```text
claim_atomic
model_version
dataset_identity
checksum
preprocessing
likelihood_and_priors
baseline
execution
convergence_or_optimizer_diagnostics
results_artifact
falsifier_evaluated
independent_review_status
```

## Fail-safe

On data, checksum, convergence or workflow failure:

- stop claim promotion;
- preserve logs and partial diagnostics separately;
- do not substitute synthetic or older data;
- mark the result `BLOCKED` or `TOKEN_VAZIO`;
- keep the previous verified ledger entry unchanged.

## Failover

There is no automatic failover that preserves a scientific claim. Alternate compute/storage may rerun the same frozen protocol, but a different dataset, likelihood or model version is a new experiment.

## Rollback

Rollback anchor:

```text
claim ledger entry + model commit + dataset checksum + workflow version + result artifact hashes
```

Rollback restores the prior claim state; it does not delete contradictory evidence.

## Watchdog

The workflow watchdog bounds runtime and records timeout, last checkpoint and sampler/optimizer state. Timeout is `BLOCKED`; it cannot be reported as convergence. Data-download watchdogs preserve source URL/identifier and checksum status without caching unverified bytes as canonical.

## Blind tests

- hide model labels during metric comparison;
- choose one held-out dataset partition by recorded seed;
- inject a checksum mismatch;
- rerun with shuffled row order where the likelihood should be order-invariant;
- include one known-invalid/synthetic fixture and require rejection from the real-data lane;
- evaluate a contradiction fixture and require claim demotion.

## Temporal refusal

“Current evidence”, “latest data” and “confirmed” require exact dates, dataset releases, commits and artifacts. A later document modification time is not evidence that an older result was rerun.

## Federated output

```text
F_ok: claim gates with reproducible evidence
F_gap: missing data/protocol, non-convergence, contradiction or external review gap
F_next: one bounded falsification or replication action
rollback_anchor: ledger + model/data/workflow/artifact identities
```
