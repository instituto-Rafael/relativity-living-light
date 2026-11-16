# RLL PR #1216 — workflow-count contract reconciliation S7

- mu_id: MU-RLL-PR1216-WORKFLOW-CONTRACT-S7-20261116
- parent: 3367ca3ed288034c1facd393ee29864b8936cff7
- observed_source: GitHub recursive HEAD tree `618e5080bb03ab3efef1fdd9eb111ed5ec7bce13` (untruncated)
- actual_workflow_count: 122; regex top-level `.github/workflows/*.{yml,yaml}`; distinct path count=122
- previous_contract_count: 120; change to 122, timestamp 2026-11-16
- GitHub exact-head PR #1216 checks: WF_COUNT_MISMATCH caused failures in workflow contract sync (V1/V2), architecture parse, branch maturity.
- source contract blob before: b66249957355b251c0fc4f615770dc47164c766d
- resulting contract blob: 72b8b2506ea14732fd1f0a162488268c7b69e479
- gate: only repository-tracked workflow path count aligned with stated source_of_truth: executable_files; no test weakening
- validation: GitHub tree metadata, checks logs and blob readback. Exact-head CI rerun after this commit NOT_RUN at receipt creation.
- status: IMPLEMENTED_UNTESTED / CLAIM_ALLOWED_FALSE; no scientific claims
- rollback: previous blob preserved; corrective successor on review branch, no rewriting history
