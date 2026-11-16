# RLL PR #1200 — preflight de dependências S4

- mu_id: MU-RLL-PR1200-DEPENDENCY-PREFLIGHT-S4-20261116
- parent: bb960c78ce924dfa63a4af3bf9ce6525a70c3b0f
- source: https://github.com/instituto-Rafael/relativity-living-light/pull/1200
- destination: work/rll-pr1200-reconcile-stdlib-gates-20261116 ONLY
- script: tools/ci/rll_workflow_dependency_preflight.py
- tests: tests/test_rll_workflow_dependency_preflight.py
- source Git blob: 4be827074e3c22ba2bb3c4556e259450d6ac46a6
- test Git blob: 7621d471622127201a783dec6e4a02569ff20622
- local execution: `PYTHONPATH=. python -m unittest discover -s tests -p 'test_rll_workflow_dependency_preflight.py' -v` => 4 tests OK; `python -m py_compile` for both files => OK. Local fixture environment, not exact GitHub HEAD.
- byte integrity: uploaded Git object SHAs match locally tested Git object hashes for both files.
- scope: static literal local-script path checking, opt-in stdlib direct-import checking, missing file fails closed; no network; no modification by the scanner except optional explicit output path.
- limitations: no full YAML parse, no dynamic expression resolution, no recursive import/runtime closure, no scientific or CI pass claim.
- status: LOCAL_TESTED_SCOPED / EXACT_HEAD_CI_NOT_RUN / CLAIM_ALLOWED_FALSE.
- safe next: run scanner on exact branch checkout in CI, validate all exact-head workflow dependencies, then review pairwise semantic conflicts; do not merge to main/lab/integration/release.
- rollback: follow parent SHA; supersede by corrective follow-up commit; no history rewrite.
