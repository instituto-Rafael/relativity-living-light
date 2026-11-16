# RLL PR #1200 — reconciliação de workflows S2 (2026-11-16)

- μID: MU-RLL-PR1200-3WAY-WORKFLOW-20261116-S2
- parent receipt: receipts/2026-11-16_rll_pr1200_lab_main_reconciliation_scope_v1.md
- source: https://github.com/instituto-Rafael/relativity-living-light/pull/1200
- ancestor: c5d1f5b4ef249f7b59043ae1325b4d7a0d6637a1
- main inspected: ac833cb1278ffde951e602dd70df4c11bcda6ac0
- base of this delta: 7bfc14718f5ae7b48f1999a1cca99f56c71af321
- target branch only: work/rll-pr1200-reconcile-stdlib-gates-20261116
- kind: THREE_WAY_NONOVERLAP_LINE_HUNK_FORWARDPORT
- changed workflow paths:
  - .github/workflows/ci-scientific-skills.yml (blob bba7c3e0089888ea47effeaa61f41d636bb3ba00)
  - .github/workflows/python-tests.yml (blob aa7607aacb8fc8b3940de05f1fbcba48deb0b3f4)
  - .github/workflows/rll-governance-quality-gate.yml (blob f5e8e0bf7c577e1083d8cb4591e72fd510155740)
- delta: forward-port line hunks from main absent in lab for three workflows, preserving lab's nonoverlapping changes and pinned artifact Actions.
- control: base-to-main and base-to-lab line-hunk collision check returned zero overlaps for all three files; no global ours/theirs or history rewrite; new blob SHA from GitHub.
- validation: static three-way line-level merge and blob creation; exact-head Python tests, actionlint, scientific CI and Android execution remain NOT_RUN; YAML semantic/regression validation remains TOKEN_VAZIO.
- status: IMPLEMENTED_UNTESTED / REVIEW_ONLY; claim_allowed=false.
- rollback: leave parent branch commit untouched in history and revert through reviewed successor commit if CI finds regression; do not modify main, lab, integration, release.
- next: check exact-head diff/CI and reconcile remaining overlapping semantic conflicts separately.
