# RLL PR1216 — exact-head Python regression S8 (2026-11-16)

- mu_id: MU-RLL-PR1216-PYTEST-S8-20261116
- parent: d53a93b7947f2f3bece211b7b62fa9b5ab28a754
- provider_run: https://github.com/instituto-Rafael/relativity-living-light/actions/runs/43814469195
- result_before: 2448 passed / 2 failed / 56 subtests passed; failures tracked in two existing test contracts.
- failed_1: tests/test_rll_android_signing_if_context.py expected 4 signed release guards, actual Android workflow has 6 explicitly guarded signing steps. The guarded steps were observed by static source readback; no secrets context is permitted in any GitHub Actions if.
- fixed_1: enumerate 6 exact required signing step names and assert each immediately guarded, assert total signing guards matches enumeration, preserve no-secrets-in-if assertion. No production workflow change.
- failed_2: tests/test_rll_inventory_parity_main_lab_merge.py expected lowercase substring, but workflow source uses same clause with uppercase initial letter. Apply casefold to check meaning and add explicit absence of git push in workflow step. No production workflow change.
- source blobs:
  - tests/test_rll_android_signing_if_context.py: 0569b7931b58123f92a7d515388d9d04444ed6f4
  - tests/test_rll_inventory_parity_main_lab_merge.py: 24b6f71bb9e67c94c9fcff78071179a1ea32f822
- status: REVIEW_BRANCH_WRITTEN / CI_EXACT_HEAD_NOT_YET_RUN; claim_allowed=false.
- falsifier: exact-head CI must run both previously failing tests and full suite. No merge before it passes.
- rollback: return to parent commit through corrective successor; no force, no deletion.
