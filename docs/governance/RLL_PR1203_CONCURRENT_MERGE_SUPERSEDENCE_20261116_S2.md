# RLL — Concurrent merge supersession receipt S2

**Observation:** live GitHub provider, 2026-11-16 UTC (PR event timestamp exact).  
**Predecessor:** `data/governance/rll_pr_merge_readiness_20261115.v1.json` and `docs/governance/RLL_MAIN_LAB_ORG_HOTFIX_TRIAGE_20261115_V1.md`, left unchanged as historical frozen observations.  
**Scope:** correction of PR counts and target branch HEAD only; does NOT certify or modify scientific code.  
**Claim:** `claim_allowed=false`.

## Provider observation

- [PR #1203](https://github.com/instituto-Rafael/relativity-living-light/pull/1203) is now **MERGED**. GitHub reports merged_at=`2026-11-16T02:12:19Z`.
- GitHub merge commit: `5025f160d1f2ddaafcbbd8b23e5f2d9bc1018928`.
- Predecessor lab: `a464f6c53482a5bbf60fbdd319a32d19feb5239e`.
- New observed lab: `5025f160d1f2ddaafcbbd8b23e5f2d9bc1018928`.
- GitHub compare from frozen lab: 3 commits ahead, 0 behind, changing only `.github/workflows/rll-json-dedup-gate.yml` and `docs/science/RLL_JSON_BYTES_EVIDENCE_AFTER_1195_20261115_V2.md`.
- Current main observed: `ac833cb1278ffde951e602dd70df4c11bcda6ac0`.
- Updated main→lab compare: lab 741 commits ahead, 1392 behind; the two histories remain diverged.
- GitHub open PR search now returns **11** PRs; former 12-count is historically accurate only for the earlier snapshot.
- This audit did **not** merge PR #1203, rebase either branch, dispatch Actions, or approve a scientific claim.

## Concurrency and preservation gates

The offline gate in `tools/ci/rll_pr_merge_guard_offline_v1.py` is **snapshot-only**. Its input is frozen and MUST NOT be used as current merge permission. Existing PR approvals, required checks, head SHA, current base HEAD, nested/stacked ancestry, exact tree diff and rollback must be reread immediately before a future merge.

This new observation **supersedes the current-state interpretation** of the frozen 12-PR snapshot but does not delete or rewrite it. A new machine-readable live snapshot would need to exclude merged PR #1203 and pin lab at `5025f160...`, then be subjected to the same read-only gate.

The review branch for this audit is intentionally based on old lab `a464f6c...`, so it is now behind lab by three commits. Do **not** force-push, reset, mass-merge or say it is synchronized with latest lab.

## R3
- **F_ok:** exact provider merge timestamp/SHA, two changed paths, 12→11 PR correction, branch divergence rechecked.
- **F_gap:** whole-suite tests and fresh required checks for remaining 11 PRs; content-specific three-way conflict work; user-specified `org` has no literal GitHub branch at this repository.
- **F_next:** one controlled successor hotfix candidate per independently failing contract, with frozen parents and evidence; do not merge from this stale audit snapshot.

No deletes, no access change, no main/lab/release modifications in this S2 receipt.
