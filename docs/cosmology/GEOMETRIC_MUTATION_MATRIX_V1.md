# Geometric Mutation Ω Matrix V1

Status: non-publishing frontier instrumentation.

## START HERE — route for humans and AI agents

Use this file as the canonical entrypoint for the V1 geometric mutation matrix.
Do not infer scientific validity from file presence, a green workflow name, or a
correlation alone.

Read and reconstruct in this order:

1. `data/contracts/geometric_mutation_matrix.v1.yml` — frozen mutation space, bounds, gates, and epistemic semantics.
2. `scripts/run_geometric_mutation_matrix.py` — deterministic generator, gate evaluator, aggregation, correlations, and bridge sensitivity.
3. `tests/test_geometric_mutation_matrix.py` — adversarial invariants that must pass before mutation shards run.
4. `.github/workflows/geometric-mutation-matrix.yml` — exact CI orchestration, sharding, environment capture, provenance, checksums, and artifact publication.
5. aggregate artifact — execution evidence for one GitHub execution identity. Read `PROVENANCE.json` before interpreting `summary.json` or `REPORT.md`.

Authority boundary:

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

A missing or unavailable state is `TOKEN_VAZIO`; it is never silently converted
to zero or PASS. `IMPLEMENTED_UNTESTED != PASS`.

## Purpose

Explore bounded mutations of geometry families, coordinate projections, fragment
dimensions, scales, and cross-domain sensitivity matrices without promoting a
geometric analogy into a physical claim.

The pipeline distinguishes four objects that must not be conflated:

1. intrinsic/geodesic distance inside a geometry;
2. extrinsic chord distance after an embedding/projection;
3. local dimensional measure change (length/area/volume proxy);
4. response of the existing RLL background model to a predeclared sensitivity projection.

## Epistemic boundary

- `claim_allowed=false`
- `publication_effect=NONE`
- `physical_wormhole_claim=false`
- cross-domain mapping is `SENSITIVITY_ONLY_NO_CAUSAL_CLAIM`
- high Pearson correlation in the receipt means sensitivity-transfer association only.

An extrinsic fold can place embedded coordinates closer together while the
intrinsic distance remains unchanged. The CI therefore forbids interpreting an
embedding shortcut as a physical wormhole or superluminal path.

## Mutation space

The frozen V1 contract enumerates:

- 4 geometry families: flat, spherical, hyperbolic, toroidal;
- 4 projections: identity, anisotropic, shear, extrinsic fold;
- 3 fragment dimensions: segment, triangle, tetrahedron;
- 3 scales;
- 4 deterministic mutations of the geometry→RLL sensitivity matrix.

Total: **576 predeclared cases**. The workflow shards them across four CI workers
and aggregates one receipt.

## Reconstruction without GitHub Actions

From the repository root, on the source commit intentionally being evaluated:

```bash
python -m pip install -r requirements/ci-frontier.txt
pytest -q tests/test_geometric_mutation_matrix.py
rm -rf /tmp/rll-gm-v1
python scripts/run_geometric_mutation_matrix.py \
  --contract data/contracts/geometric_mutation_matrix.v1.yml \
  --output-dir /tmp/rll-gm-v1/shard-0 \
  --shard-index 0 \
  --shard-count 1
python scripts/run_geometric_mutation_matrix.py \
  --contract data/contracts/geometric_mutation_matrix.v1.yml \
  --output-dir /tmp/rll-gm-v1/aggregate \
  --aggregate-root /tmp/rll-gm-v1
```

The local reconstruction reproduces the deterministic cases and scientific
gates. GitHub-specific execution identity (`run_id`, `run_attempt`, repository
ref and synthetic pull-request merge identity) exists only in the CI-generated
`PROVENANCE.json` and must remain `TOKEN_VAZIO` outside that execution context
rather than being invented.

## PR head versus execution SHA

For `pull_request` events, GitHub Actions normally checks out a synthetic merge
of the PR head with the target base. Therefore these identities are deliberately
separate:

- `pull_request_head_sha` — the authorial/source head proposed by the PR;
- `pull_request_base_sha` — the target base used for integration context;
- `github_event_sha` — GitHub's event SHA, normally the synthetic merge commit;
- `execution_checkout_sha` — `git rev-parse HEAD` inside the actual job.

The provenance identity gate requires `execution_checkout_sha == github_event_sha`.
For a pull request it additionally requires both PR head and base SHAs to be
present. A PR-head SHA must never be relabeled as the execution SHA, and a
synthetic merge SHA must never be relabeled as the authorial PR head.

## Receipts and provenance

The aggregate artifact contains:

- `PROVENANCE.json` — repository/event identity, execution checkout SHA, PR head/base SHAs when applicable, run identity, hashes of contract/runner/tests/requirements/workflow/navigation, gate result, case count, and non-claim semantics;
- `cases.jsonl` and `cases.csv` — complete case-level evidence;
- `summary.json` — gate, bridge-sensitivity, and correlation summary;
- `cross-correlations.csv` — thresholded sensitivity-transfer associations;
- `REPORT.md` — human-readable summary;
- `CLAIM_BOUNDARY.txt` — explicit non-publication/non-causality boundary;
- `python-version.txt` and `pip-freeze.txt` — execution environment capture;
- `CHECKSUMS.sha256` — integrity digests for the aggregate files.

Artifact retention is finite. Expiration means the old execution bytes are no
longer directly available; it does **not** convert the old receipt to FAIL or
PASS. Reconstruct from the intended historical identity and compare the new
receipt. The PR body is the durable pointer to the latest validated run and
artifact digest; never substitute a receipt produced for a different execution
identity.

Bridge-choice spread is reported per response metric. It measures dependence on
the arbitrary sensitivity projection and is not a physical uncertainty estimate.

## Gate ladder

A run is eligible to be called `PASS` for this instrumentation only when all of
the following are true in the same execution:

1. contract loads with the required non-claim semantics;
2. adversarial invariant tests pass;
3. every mutation shard completes successfully;
4. aggregate gate is `PASS` with zero recorded gate failures;
5. provenance identity gate is `PASS` and the execution checkout SHA equals GitHub's event SHA;
6. for PR events, both PR head and base SHAs are present and independently typed;
7. aggregate checksums are produced and verify;
8. repository governance/maturity checks required by the target branch are green.

A green geometric-mutation gate does not grant a physical claim. It establishes
only that the predeclared sensitivity experiment executed consistently.

## Urgency and gap classification

`P0 — integrity`: provenance identity mismatch, checksum failure, missing PR
head/base identity on a PR run, missing aggregate, forbidden physical shortcut
claim, or baseline/invariant failure. Stop promotion and correct before
interpretation.

`P1 — reproducibility`: dependency/environment mismatch or expired artifact when
an exact historical execution must be audited. Re-run the intended historical
source/integration context and compare receipts; do not rewrite the historical
result.

`P2 — scientific extension`: Fisher/Mahalanobis metrics, permutation nulls, FDR,
persistent topology, or physically derived adapters. These are valuable future
work but are **outside V1** and must not be smuggled into a V1 integrity hotfix.

## Promotion rule

A correlation discovered by this CI cannot by itself enter a physical claim.
Promotion requires a domain adapter with a physical derivation or independent
observational likelihood, plus the existing RLL frontier gates.

The route remains:

`feature/* -> rll/lab -> rll/integration -> rll/release -> main`

Do not bypass the branch-maturity gate to make a green scientific job appear
promoted.

## Rollback

This V1 unit is intentionally isolated. If a change to the matrix, contract,
runner, tests, workflow, or this navigation document regresses its gates:

1. preserve the failed run and its receipt as evidence;
2. identify the first causal commit on the feature/lab route;
3. revert that commit or restore the last known-good versions of these V1 files;
4. rerun the same gate ladder on the resulting execution identity;
5. record the successor receipt rather than overwriting the failed history.

No rollback may alter a historical receipt to make it appear successful.