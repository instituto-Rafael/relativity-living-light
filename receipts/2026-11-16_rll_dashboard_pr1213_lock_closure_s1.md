# Dashboard toolchain dependency closure — PR #1213 S1 (2026-11-16)

- mu_id: MU-RLL-DASHBOARD-PR1213-LOCK-S1-20261116
- source_dependency_head: 7e9aa0142663e2e7061aeda8caf2eef440511ed3
- npm_resolver_run: https://github.com/instituto-Rafael/relativity-living-light/actions/runs/43821967526
- isolated_diagnostic_branch: work/rll-dashboard-lockgen-diagnostic-20261116-v1@56b57036dc0d7adc5d74ddec5081de5ed88d519d
- resolver: Node 24; npm install --package-lock-only --save-dev --save-exact tailwindcss@3.4.17 jsdom@26.1.0 --legacy-peer-deps --ignore-scripts --no-audit --no-fund
- output_source: package and lock encoded in GitHub Actions log with explicit boundaries, decoded and validated before Git blob upload; output Git blobs: package 1761b834892394430c883d76a538272f027f33fb, lock 4d8c2cb3dee204f3af0cf6f4592209a6270fd9a0.
- baseline_dependencies: all previous production and dev direct dependencies preserved; added only two missing dev dependencies, Tailwind 3.4.17 and jsdom 26.1.0.
- actual_failure_sources: dashboard Vite/PostCSS cannot find tailwindcss; Vitest cannot find jsdom and reports no tests; previous build and tests FAILED in PR #1212.
- new tests: scoped dashboard Zustand state preference persistence, three behavioral tests; jsdom URL explicit to prevent opaque origin localStorage error.
- CI: dashboard pull_request branch filter expanded to dependabot/** for stacked PR #1213. Actual exact-head build, tests, security audit and type-check remain NOT_RUN until CI confirms.
- policy: do not suppress any failed jobs; do not auto-push npm artifacts; claim_allowed=false.
- rollback: reviewed successor or revert, preserve bot dependency updates.
