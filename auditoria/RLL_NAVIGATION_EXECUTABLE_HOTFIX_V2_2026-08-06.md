# RLL Scientific Navigation — Executable Hotfix V2

Date: 2026-08-06

## Boundary

```text
claim_allowed=false
automatic_merge=false
source_run=31064223594
source_artifact_sha256=419ec4beca36ec978c2bd514090ed85aa26533af5a95f835e741a6557b845105
```

This change is an append-only successor to the artifact audit merged through PR #16. It does not rewrite the historical workflow receipt and does not promote RLL physical claims.

## Invariants implemented

1. Every absent `required_path` becomes a high-severity, zero-weight `TOKEN_VAZIO`.
2. Every absent registered `evidence_path` becomes a medium-severity, zero-weight `TOKEN_VAZIO`.
3. `NAVIGATION_MANIFEST.open_token_vazio_count` must equal the open ledger count.
4. `BUILD.log` and `WORKFLOW_RECEIPT.json` are created before the final checksum ledger.
5. `DEPENDENCY_GRAPH.json` V2 includes mechanisms, artifacts, expected runtime artifacts, claims, uncertainty nodes and required-evidence routes.
6. `F_gap` describes the unresolved state; `F_next` records the action, without duplicating both fields.
7. Tier 1 repository inventory no longer claims runtime execution merely from workflow-source presence.

## Local deterministic receipt

```text
pytest=8/8 PASS
schema_validation=PASS
simulated_registry_mechanisms=4
simulated_open_tokens=7
graph_nodes=62
graph_edges=58
environment=Linux x86_64 / Python 3
claim_allowed=false
```

The simulation used the four-mechanism registry snapshot available during local construction. The live branch registry later contained six mechanisms; therefore live repository counts are delegated to GitHub Actions and must not be inferred from the local simulation.

## Local file SHA-256

```text
tools/build_scientific_navigation_bundle.py cfa4289c920463244caed3e1e39b9fd4f59520c2168a705bde408d2f4e658ab1
tests/test_scientific_navigation_bundle.py 1ff0320eaaaac97462b321d973812da9bc8a110553013e9c5647fa0dc8a6b49f
.github/workflows/rll-scientific-navigation.yml 4cc66526d3de93a6b7127b10cce1aeb70a131a1c67c4241ea661c58a94c5cb72
```

## F_ok

- missing evidence paths are no longer silent;
- late workflow files enter the checksum ledger;
- exact manifest/ledger equality is enforced;
- graph structure exposes closure dependencies;
- original artifact success remains valid within its historical boundary.

## F_gap

- live GitHub Actions execution for this V2 is pending;
- the registered `model_comparison_real_fit_metadata.json` remains absent and should become an automatic evidence TOKEN_VAZIO;
- physical Termux/mobile receipt and independent scientific review remain open;
- runtime artifacts are declared but are not automatically treated as bound execution evidence.

## F_next

Run the PR workflow, inspect the emitted V2 artifact, verify the automatic evidence token and finalized checksums, then request human review. Do not merge from this receipt alone.
