# RLL — Main/Lab/Org PR reconciliation: frozen provider audit and fail-closed hotfix gate V1

Scope date: 2026-11-15, live GitHub provider inspection (not a time-continuous monitor).
Authority: instituto-Rafael/relativity-living-light; no merge, no force push, no workflow dispatch, no security settings mutation.
Status: DOCUMENTARY_AUDIT + REVIEW_BRANCH_GUARD_IMPLEMENTED_UNTESTED; claim_allowed=false.

## Canonical refs (exact freeze)
- main ac833cb1278ffde951e602dd70df4c11bcda6ac0 PROTECTED
- rll/lab a464f6c53482a5bbf60fbdd319a32d19feb5239e NOT PROTECTED
- rll/integration 2f30179ebebf91e7514ffdffb61609a3cf12ef0b
- rll/release 2cb3e3e88677ea9ac1f263377114b539db7bc47f
- org / rll/org: neither verified as a literal branch; `org` GET returned 404. An organization owner is not a branch.
- merge-base main...lab c5d1f5b4ef249f7b59043ae1325b4d7a0d6637a1; lab is 738 ahead and 1392 behind main. Compare file list capped at 300; not exhaustive.
- lab...integration diverges historically (1 integration-only, 587 lab-only), but GitHub comparison currently returns 0 changed files. Verify actual tree identity before treating this as ancestry-only.
- lab...release: release is an ancestor, 2059 commits behind lab; do not rewrite release without targeted gates.

## Twelve PRs triaged; no merge cleared
- #1200 lab→main: 653 changed paths, GitHub mergeable_state=dirty; direct global merge blocked.
- #1203 JSON metadata, #1204 Actions/agent credentials boundary, #1205 branch graph: unstable, submit-gradle failing; #1205 includes generated inventory outputs and code, not docs-only.
- #1206 one-line Gradle version: dirty, submit-gradle failing; superseded in stacked #1207/#1208; avoid duplicate cherry-pick.
- #1207 stacked PR1203-1206: dirty, android and Gradle failures.
- #1208 integration-history two-parent work branch: 25 changed files (including Gradle and workflows), unstable, six-sigma-real-data-controls fails; 0-file historical integration comparison does NOT authorize merging all 25 changes.
- #1209 Android signed APK receipts: dirty, test fails. #1210 inventory parity: dirty, test+six-sigma fail.
- #1211 main→lab Rx fabric: dirty, 159 changed files and seven failing checks; do not hide failures with CI exclusions.
- #1212 Dependabot dashboard: 5 changed files, unstable, seven failing checks; #1213 is a stacked draft branch based on #1212, not a main branch PR.

## Root causes read directly from job logs
- PR #1211 Rx gate: `import_workflow_no_requests_install`. Pytest: 4 failed, 2435 passed; expected 120 workflows but observed 122, Android signing assertion expected four `if` guards but found six, inventory parity assertion missing expected exact phrase. Distinguish stale test literal from actual policy regression before changing tests.
- PR #1212 dashboard: missing jsdom for Vitest; missing tailwindcss for PostCSS; ESLint TypeScript source parsed as plain JS. Need align package manifests and lockfile, valid TS ESLint parser/config, then rerun exact-head dashboard workflow.
- Root Gradle workflow: `gradle-wrapper.jar` absent in both main and lab at observed ref; do not bypass or forge missing binary. Reconcile wrapper provenance/checksum before declaring Gradle valid.
- PR #1208 six-sigma-real-data-controls failure: source log requires scoped investigation before merge; do not reinterpret as global PASS.

## Proposed hotfix priority: smallest reversible deltas
1. P0: Resolve #1211 import dependency contract and workflow count drift on isolated candidate; use `git merge-tree`/3-way checkout of verified parents. No deletion or replaced data.
2. P0: Fix review candidate's Android-signing guard invariant and inventory parity check, preserving both functionality and evidence. Avoid updating expected counts blindly.
3. P1: Regenerate or restore Gradle wrapper from verified upstream Gradle distribution with wrapper checksum, binary provenance and license; validate on a fresh environment. Never skip failing job.
4. P1: Dashboard #1212/#1213: address missing jsdom/tailwindcss/TypeScript lint config as a separate tested PR. Ensure dependency lock and tests; never auto-merge security dependencies on partially failing workflow.
5. P1: Review #1208 ancestry-only merge in separate two-parent branch, compare tree OIDs, then isolate any conflicting app/science/workflow changes.
6. P2: Gradual path-by-path reconciliation main↔lab, retaining Rx, Android, data/CI evidence and scientific baselines. No whole-tree checkout or blind ancestry union.

## Offline audit gate
- Code `tools/ci/rll_pr_merge_guard_offline_v1.py`: read-only snapshot validator, emits BLOCKED reasons; never invokes merge or network. Input is `data/governance/rll_pr_merge_readiness_20261115.v1.json`; tests `tests/test_rll_merge_readiness_guard_v1.py`.
- Run `python -m unittest discover -s tests -p 'test_rll_merge_readiness_guard_v1.py' -v` on this branch; `python tools/ci/rll_pr_merge_guard_offline_v1.py --snapshot data/governance/rll_pr_merge_readiness_20261115.v1.json`.
- Important limitation: this is FROZEN data, not live CI status. Re-read head SHA, base SHA, all required checks, exact diff, review, permission, rollback and deployment effects immediately before any future merge.
- Even if future snapshot returns HUMAN_REVIEW_ONLY, automatic_merge_allowed remains false.

R3: F_ok = provider facts + non-mutating gate staged. F_gap = full conflicts/hotfix CI not yet reproduced on new branch. F_next = execute offline gate tests, triage four #1211 regression failures, then stage a single minimal candidate hotfix and rerun only necessary checks.
Rollback: no changes to main/lab; new review branch may be superseded without deleting any source or history. No RLL science or claims promoted.
