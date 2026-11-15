# RLL Ω — Current-state authority graph V2 · 15/11/2026

**Status:** `PROPOSED / HOLD` · `claim_allowed=false` · `auto_merge=false` · `publication_effect=NONE`.

**Source:** provider GitHub branch metadata, per-ref `.github/workflows` directory and immutable compare results, read on 15 November 2026. **Machine twin:** [RLL_CURRENT_STATE_AUTHORITY_GRAPH_20261115_V2.json](../../data/governance/RLL_CURRENT_STATE_AUTHORITY_GRAPH_20261115_V2.json). This record **supersedes only the outdated point-in-time graph** [V1 of 2026-09-11](RLL_CURRENT_STATE_AUTHORITY_GRAPH_20260911.md) without erasing it. It does not assert a live runtime after the stated observation.

## Authority / branches

| Branch | Exact provider HEAD | Workflow YAML/YML entries | Provider `protected` |
|---|---|---:|---|
| `main` | `0f1dc947c150c67626b173b23db7d6cd98670343` | 135 | true |
| `rll/lab` | `80d839b8758c475b0a4bbb1dc519664fcc16082d` | 120 | false |
| `rll/integration` | `2f30179ebebf91e7514ffdffb61609a3cf12ef0b` | 107 | false |
| `rll/release` | `2cb3e3e88677ea9ac1f263377114b539db7bc47f` | 69 | false |

These are **four distinct reference-specific directory counts**, not a single global inventory nor proof of protection rules; `protected=false` is a provider metadata observation, not admin readback of all rulesets.

| Left → right | Commits unique to left | Unique to right | Merge base | Ancestry |
|---|---:|---:|---|---|
| `main` → `rll/lab` | 1,388 | 736 | `c5d1f5b4ef249f7b59043ae1325b4d7a0d6637a1` | two-sided DIVERGED |
| `rll/lab` → `rll/integration` | 585 | 1 | `de4099bbbb7c5adeb21eeeabc220aa803aaa5011` | two-sided DIVERGED |
| `rll/integration` → `rll/release` | 1,473 | 0 | `2cb3e3e88677ea9ac1f263377114b539db7bc47f` | LEFT_AHEAD |
| `rll/lab` → `rll/release` | 2,057 | 0 | `2cb3e3e88677ea9ac1f263377114b539db7bc47f` | LEFT_AHEAD |

**Do not bulk-merge.** Path intersection for the **current** `main`/`rll/lab` snapshots = `TOKEN_VAZIO_NOT_FULLY_MATERIALIZED` (the September document's 168 overlaps are historical). Commit distance is not a dominance or quality metric; check exact tree content and tests before selecting a batch. Existing `tools/branch_divergence_inventory.py` performs read-only local Git comparisons. This PR **adds** `topology_status` to disambiguate one-sided from two-sided, while retaining its legacy `status` field and old `--fail-if-diverged` behavior.

## Layers and permitted claims

| Layer | Canonical producer/contract | Work/evidence boundary | Issue |
|---|---|---|---|
| Exact mathematical | Poincaré 7D and formula corpus | exact math not physical coupling; paired Euclidean×Hyperbolic baseline pending | [#863](https://github.com/instituto-Rafael/relativity-living-light/issues/863), [#793](https://github.com/instituto-Rafael/relativity-living-light/issues/793) |
| Empirical cosmology | governed data contracts / `rll_state_reconciliation_20261115.v1.json` | independent CMB/DESI covariance and reproduction not shown | [#732](https://github.com/instituto-Rafael/relativity-living-light/issues/732) |
| Operational branches | `tools/branch_divergence_inventory.py`, branch genealogy V2 | audit only; no force push or auto merge | [#860](https://github.com/instituto-Rafael/relativity-living-light/issues/860), [#861](https://github.com/instituto-Rafael/relativity-living-light/issues/861), [#868](https://github.com/instituto-Rafael/relativity-living-light/issues/868), [#869](https://github.com/instituto-Rafael/relativity-living-light/issues/869) |
| Workflows and agent | `.github/workflow-contract.yml`, Secretary agent + seven guards | workflow directory list ≠ regenerated canonical inventory; Actions ≠ Copilot Cloud Agent | [#865](https://github.com/instituto-Rafael/relativity-living-light/issues/865), [#864](https://github.com/instituto-Rafael/relativity-living-light/issues/864) |
| External settings | `rll_agent_authority.v1.json` | branch metadata ≠ authenticated admin protection/ruleset readback | [#964](https://github.com/instituto-Rafael/relativity-living-light/issues/964) |
| Real-data runtime | `rll-real-data-orchestrator.yml` | post-hotfix target jobs still unobserved; do not infer >=1 jobs from syntax | [#876](https://github.com/instituto-Rafael/relativity-living-light/issues/876) |

## Branches/PRs: smallest safe forward-port

- [PR #1203](https://github.com/instituto-Rafael/relativity-living-light/pull/1203), HEAD `d2e57f84322ae20449eadde27f9dceadd65ea49d`: JSON audit metadata gate; independently green on its prior exact HEAD; remains draft/unmerged.
- [PR #1204](https://github.com/instituto-Rafael/relativity-living-light/pull/1204), HEAD `02b53049b3474091332b8fa0d976de5a12e0a0ea`: Secretary Actions runtime correction; independently green on its prior exact HEAD; remains draft/unmerged.
- Both started at `rll/lab@80d839b8758c475b0a4bbb1dc519664fcc16082d`. Their changed-file sets are disjoint in the observed PRs, **but sequential integration requires fresh CI on the actual combined candidate**. No autonomous PR merge.
- [PR #1200](https://github.com/instituto-Rafael/relativity-living-light/pull/1200) directly proposes `rll/lab -> main`, contrary to the governed promotion topology; GitHub reports `mergeable_state=dirty`. Retain draft/HOLD; do not resolve by overriding history.
- [PR #1151](https://github.com/instituto-Rafael/relativity-living-light/pull/1151) (Gradle Action) has one unique head commit and is 52 commits behind `rll/lab`. Review the one-file delta on a **new** work branch and current action policies rather than rewriting a Dependabot ref.

## Negative controls and rollback

A graph with a mismatched exact HEAD, incorrect ahead/behind orientation, false CI/runtime claims, or `claim_allowed=true` must **FAIL**. The graph's static tests confirm internal consistency, not provider freshness; live provider requery is mandatory before any promotion. No branch was rebased, merged, deleted, renamed, or force-updated as part of this document.

**F_ok:** immutable SHA/compare + directory-count snapshots observed. **F_gap:** current path-overlap materialization, external settings authority, physical data, global inventory and post-hotfix runtime remain unresolved. **F_next:** run static regression and exact-head CI, then prepare one selective reviewable batch through `work/* -> rll/lab`, preserving negative evidence and all old commits.

`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM` · `IMPLEMENTED_UNTESTED ≠ PASS`.
