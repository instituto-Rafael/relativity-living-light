# RLL Workflow Orchestrator

The v3 session catalog separates the exhaustive workflow inventory from the allowlisted dispatch manifests. The inventory glob is read-only; dispatch is restricted to manifests under `workflows/tower/` and `workflows/research/`.

Execution is sequential, fail-fast, and single-flight. The profile budgets below sum child workflow timeouts. `full_session` covers bounded governance and real-data workflows; the longer deterministic and frontier checks stay isolated in `science_shadow_session`.

| Profile | Selected scope | Maximum budget |
|---|---|---:|
| `quick_session` | structural, contract, regression, governance | 120 min |
| `transit_refactor` | bounded operational tower | 190 min |
| `real_data_session` | real-data custody and metadata audits | 185 min |
| `full_session` | tower plus real-data profile; excludes science shadow | 305 min |
| `science_shadow_session` | deterministic pipeline and frontier contract | 190 min |
| `literature_session` | academic package intake and Jekyll preview | 15 min |
| `pages_preview_session` | Jekyll preview artifact | 15 min |

The parent job has a 360-minute ceiling. The largest configured profile leaves 55 minutes of headroom. Research-fragment outputs are artifacts only; this catalog does not grant Pages deployment permission or promote scientific claims.

## Catalog evolution

- `rll.workflow_orchestrator.catalog.v3` keeps inventory and execution separate and fails closed on invalid manifests.
- New validated knowledge belongs in domain registries or result artifacts with source, checksum, method, baseline, and epistemic state. Session YAML describes routing and capacity.
- A workflow manifest requires an explicit ID, file, stage, specialty, timeout, dispatch inputs, default-deny override allowlist, `claim_allowed: false`, and `publication_effect: NONE`.
