# RLL ATLAS Continuous Evolution Ω6 V2 — current authority

State: `IMPLEMENTED_FAIL_CLOSED / claim_allowed=false / publication_ready=false`

Ω6 is an orthogonal successor that consumes, rather than replaces, the merged ATLAS G0–G7 gate, the merged session-evolution mesh, and the current workflow-inventory reconciliation.

## Authority chain

- `rll/lab` base: `b5ad6dc1afbddb930c7a526a152544665c2d36f2`
- tree: `ac055f5d0fa185e64ab22d777c6015b5f3b8a2eb`
- PR #780 / merge `75323d72...`: ATLAS G0–G7
- PR #785 / merge `7ade8090...`: session evolution mesh V2
- PR #786 / merge `b5ad6dc1...`: executable workflow inventory reconciled to 77

The six #785 fences remain authoritative: authority, non-regression, falsifiability, rollback, drift/freshness, independence.

## Ω6 complementary guardrails

1. `OMEGA6_PROVENANCE_LOCK` — immutable source/version/rights/content identity.
2. `OMEGA6_RECEIPT_CHAIN` — deterministic predecessor-linked receipt and SHA-256.
3. `OMEGA6_CUSTODY_DAG` — acyclic source → evidence → gate → receipt custody.
4. `OMEGA6_ADVERSARIAL_PARITY` — identical frozen comparison policy for RLL and baselines.
5. `OMEGA6_REPRO_REPLAY` — frozen runtime/seed/convergence/replay evidence.
6. `OMEGA6_INDEPENDENT_REPLICATION` — same-producer reruns never equal independent replication.

All six are `ACTIVE` and `claim_blocking=true`. IDs are disjoint from the #785 fence IDs.

## Gap reduction without false closure

- generic Bayes → `REDUCED`: real prior-locked two-seed Dovekie SN-only nested evidence exists; joint Bayes and independent replication stay open.
- ACT DR6 materialization/reference predicate → `RESOLVED`; LCDM posterior chain remains `OPEN_INTERNAL`.
- DESI generic reproduction → `REDUCED`; official joint/cross-block reference reproduction stays `OPEN_EXTERNAL`.
- DES Y6 3x2pt stays `OPEN_EXTERNAL`: availability is not executable custody.
- generic CLASS/CAMB perturbation gap → `REDUCED`: LCDM/CPL baseline is verified and RLL internal growth approximation exists; RLL perturbation closure and independent engine implementation remain open.
- the former session merge-tool boundary is historical `RESOLVED` because #780 merged canonically.

## G0–G7 projection

`G0=PARTIAL`, `G1=PARTIAL`, `G2=TOKEN_VAZIO`, `G3=TOKEN_VAZIO`, `G4=TOKEN_VAZIO`, `G5=PARTIAL`, `G6=PARTIAL`, `G7=BLOCKED`.

Maturity coverage: `4/21 = 0.190476`. This is contract coverage, not probability that RLL is correct.

## Continuous execution contract

Ω6 reuses `.github/workflows/rll-governance-quality-gate.yml`; no new workflow is introduced, so the reconciled workflow inventory remains 77.

Autonomous actions allowed: validation, classification, receipt generation, hashing, regression detection. Forbidden: automatic scientific claim promotion, force-moving maturity refs, deleting historical evidence, auto-merging unreviewed scientific changes.

Urgency can change probe order only. Truth/evidence thresholds are immutable under this contract.

## Session custody

The interaction trace stores user-visible directives and externally observable actions/results. Private reasoning is not serialized as provenance.

## R3

`F_ok`: #780/#785/#786 consumed; six complementary Ω6 guards; Bayes/ACT/CLASS-CAMB gaps narrowed; custody DAG and receipt chain materialized.

`F_gap`: G2/G3/G4, DESI joint reproduction, joint multi-probe Bayes, ACT LCDM posterior, DES Y6 executable custody, RLL perturbation closure/implementation, independent replication.

`F_next`: close the highest-value P0 evidence authorities with immutable receipts; append successors only after proof.
