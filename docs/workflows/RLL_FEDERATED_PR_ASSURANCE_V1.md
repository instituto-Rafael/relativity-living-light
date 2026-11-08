# RLL · Federated PR Assurance V1 (point-in-time, fail-closed)

## Contract
**SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM.** This is a frozen, read-only metadata snapshot of *some* open PRs. No automation may assert current GitHub state from it. It cannot authorize merging, physical Android readiness, science, or a Bayesian posterior.

Inventory as of 2026-11-08: **53** open PRs across owned `rafaelmeloreisnovo` repositories + **4** in `instituto-Rafael` = 57. **Three external FirebirdSQL contributions are separate**; none is claimed to be owned. This contract documents **12 directly examined** high-impact PRs, not all 57. Sources are linked to exact PR HEAD and sampled GitHub Actions runs.

## Typed rules / evidence gates

- `DEVICE_E2E_MISSING` = P0; a signed debug APK/upload is not evidence of OAuth consent, paginated Drive traversal, resume, storage, or device usability.
- `BOOTSTRAP_REAL_ARM_FAIL` = P0; bootstrap producer must emit immutable digest and consumer must actually install/run it.
- `REMOTE_ARTIFACT_QUOTA` = P1; `PASS_SCOPED` KAT and local SHA256 summary do **not** close provider artifact custody. Upload remains required.
- `CI_FAILURE`, `ANDROID_BUILD_FAILURE`, `BRANCH_MATURITY`, and `EXTERNAL_PROTECTION_PARTIAL` remain P1 until producer owner/settings evidence exists.
- `DEPENDENCY_MIGRATION_REVIEW` is P2 independently; when a build fails, highest associated priority takes precedence.
- If head SHA/CI head mismatch, incomplete source, missing typed gap, unsafe secret/network capability or attempted merge promotion occurs, fail the contract immediately.

## Executable entrypoints (stdlib only)

```sh
python tools/ci/rll_federated_pr_assurance_v1.py --require-schema --output results/audit/rll_federated_pr_assurance_v1.json
python -m unittest discover -s tests -p 'test_rll_federated_pr_assurance_v1.py' -v
python tools/ci/rll_federated_pr_assurance_v1.py --as-of 2026-11-20 --require-schema
```

First command verifies structure and emits a JSON receipt. The last command emits `snapshot_freshness=STALE`, not an invented refresh. `--require-closure` intentionally refuses to promote unresolved open PRs. The tests target tampered SHAs, priority downgrades, missing evidence, quota confusion, false physical readiness, duplicate entries, foreign repositories, source URLs, unsafe CI networking and stale state.

## CI integration / rollback

Exactly one **early offline step** is added to the pre-existing `.github/workflows/python-tests.yml` which is invoked on PRs; no new top-level YAML. No GitHub token is consulted by the script, no secrets read, no external API requests, no app binaries generated. GitHub PR branch topology, scientific gates and `main` remain unchanged. Roll back by reverting this additive PR.

## Next closing evidence

Owner-approved quota restoration + receipt upload for ZIPRAF; real Motorola OAuth/Drive metadata pagination and recovery receipts for RmrCti; producer-driven bootstrap and consumer APK for Termux; scoped Android build matrix for Vectra/UserLAnd; actual owner-governed maturity and branch protection readback for RLL; fresh snapshots anchored to exact HEAD for the remaining 45 PRs. Never assume an API gap is zero.

R3 = <typed risk and receipt schema, unmeasured E2E+provider authority+remaining PRs, next owner-specific repair and exact-ref CI>.
