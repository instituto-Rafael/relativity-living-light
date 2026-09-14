# Workflow Orchestrator Catalog

This directory centralizes the evolvable orchestration structure for GitHub Actions workflows.

- `session.yml` is the single orchestrator entry file (profiles, directories to load, and the single-flight execution policy).
- `workflows/` is the modular directory tree with nested manifests that replace direct listing in one monolithic catalog.
- `tools/workflow_orchestrator.py` reads `session.yml`, expands `workflow_catalog_dirs`, and dispatches workflows as one unified session.

## Schema Evolution

- `rll.workflow_orchestrator.catalog.v1`: monolithic `catalog.yml` with inline `workflows`.
- `rll.workflow_orchestrator.catalog.v2`: single entry (`session.yml`) + `workflow_catalog_dirs` that load nested manifest files from directories.

## Where operational learning belongs

Workflow manifests describe **execution**, not accumulated knowledge. New validated
knowledge belongs in the relevant domain registry or result artifact, with source,
checksum, method, metric, and epistemic state. The parent `session.yml` should
contain only profiles and execution policy; adding another YAML file for each
learning event is not required.

The orchestrator runs the selected manifests in ascending `stage` order and
waits at the stage barrier even when `--wait` is omitted. A failed workflow is
recorded in the summary and `--fail-fast` controls whether later stages are
skipped.
