# RLL input/index/evidence hotfix — producer receipt

μID: MU-RLL-INPUT-INDICES-EVIDENCE-20261118-S1
Source/predecessor: instituto-Rafael/relativity-living-light@ac833cb1278ffde951e602dd70df4c11bcda6ac0.
Kind: IMPLEMENTED_TESTED_LOCAL_SCOPED; claim_allowed=false.
Branch: hotfix/rll-input-indices-evidence-20261118. Date in identifier uses UTC.
Authority: explicit user request for RLL hypothesis orchestration and input/index hotfix.
Scope: producer software only; no federation checkpoint advance.

## Reproduced baseline failures

- Empty evidence with declared S5 still emitted PASS for P0 through P4.
- subdata([-1,0]) silently selected the last observation followed by the first.
- subdata([0,0]) accepted a repeated observation (double counting).

## Delta and falsifiers

- Router exposes declared stage separately from check execution. This router runs no scientific checks; stage reached now yields TOKEN_VAZIO_CHECK_EXECUTION. Filename lists and high declared stages cannot promote PASS.
- Reject duplicate/unknown/missing passes, stage aliases/reordering, duplicate fragment IDs, null/empty queue entries, string evidence, claim policy drift.
- DESI subsets require nonempty one-dimensional unique integer indices in range. Prediction vectors require equal observable/redshift lengths and finite parameters. Replacement observations must match the full source vector.
- CSV schema/row length and canonical index text validated; covariance empty/short rows fail with a typed ValueError.
- Valid permutations retain the same permutation for observations, labels and both covariance axes.
- Source observations, covariance bytes, baseline chi2 expectations and historic receipts unchanged.

## Execution / evidence

Command: `/tmp/rll-hotfix-tests/bin/python -m pytest -q tests/test_frontier_research_composition.py tests/test_rll_desi_adversarial.py tests/test_rll_repository_pat_assurance.py tests/test_frontier_possibility_ladder.py tests/test_theory_practice_calibration.py`.
Result: 67 passed, 7 subtests passed; one environment warning from anyio importing deprecated pytest CallSpec2. Exit 0. This is a focused suite, not the full repository suite.
CLI frontier receipt: FIXED_POINT, 2 iterations, 5 items, 45 TOKEN_VAZIO outcomes; fixed_point_scope=DECLARATION_EVALUATION_ONLY; scientific_checks_execution=NOT_RUN. Repeated evaluation is not scientific hypothesis evolution.
PAT static validator: PASS_STATIC; actual PAT authentication/permissions NOT_EXECUTED. No real secret was read or printed; connector authorization was used for GitHub operations.
Environment: Linux-6.18.57-x86_64-with-glibc2.41, Python 3.12.14. NumPy/SciPy/PyYAML are existing project dependencies; isolated test environment adds pytest for verification only. No dependency manifest changed.

| Tested source | SHA-256 of local bytes |
|---|---|
| `scripts/run_frontier_research_orchestrator.py` | `0f57beb69a267c394fd94cdb9ba3e4e445b44f07d27d0e452b4fe51409b4415f` |
| `scripts/rll_desi_adversarial.py` | `77f13346d561e1ea2631ddfb2eb31c292ebbe1e645689a08455d61c587655aba` |
| `tests/test_frontier_research_composition.py` | `9c5ec0e33ff390de8ffb5fcd11de0886c4b8e80c5ed0445bb76d64e68ea2f439` |
| `tests/test_rll_desi_adversarial.py` | `89f920e55911932c3ca52eb4da03eae7f9a6522498dd4b72b275661124a8e944` |

## Promotion boundary / next gate

Observed ruleset 23116926 is active but has required_approving_review_count=0, no required_status_checks entry, five always-bypass actors, current_user_can_bypass=always. Scope of observation is that ruleset, not proof of absence of every provider protection.
Keep branch-only: no PR, merge, release, manual workflow dispatch, permission/settings change or scientific claim promotion. CI exact HEAD, independent review and negative provider enforcement test remain TOKEN_VAZIO. GITPAT is referenced only by the existing manual read-only assurance workflow; runtime binding is not proven here. The available connector does not expose workflow dispatch.
Rollback: leave branch unmerged, or reviewed successor revert; no deletion/rewrite of history. Future evidence belongs in a successor receipt.
F_ok: three reproduced failure mechanisms fixed; focused software controls executed locally.
F_gap: full suite/CI exact HEAD, device execution, independent review, scientific validation, PAT runtime and provider promotion enforcement.
F_next: review exact commit, execute focused CI through an authorized runner, then assess promotion under enforceable checks.
