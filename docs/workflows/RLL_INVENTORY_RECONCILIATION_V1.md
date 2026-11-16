# RLL inventory reconciliation route v1

Status: PENDING_CI — append-only documentation route.

The previous research-fragment integration is already merged into rll/lab. The repository's own tools/docs_inventory.py reports the tracked checkout as larger than the committed generated inventory. This branch asks CI to regenerate the six official outputs from the exact merge-base checkout.

## Scope

- source: tools/docs_inventory.py and the tracked checkout at this branch;
- artifacts: docs/DOCUMENTATION_FULL_INVENTORY.md, docs/REAL_NUMBERS_REPORT.md, docs/YML_WORKFLOWS_INDEX.md, data/results/repo_inventory.json, data/results/repo_inventory.tsv, data/results/repo_inventory_summary.json;
- rule: generated output only; no scientific claim, no deletion, no Pages publication;
- next gate: compare the generated outputs with the committed files in the Six Sigma inventory workflow.

This route preserves the distinction SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
