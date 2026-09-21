# RLL Manifold Index Scaffolding V1

Date: 2026-09-20  
State: GOVERNED_DRAFT  
Scientific effect: NONE  
Default: `claim_allowed=false`

## Purpose

The scaffold turns repository navigation into a recursively reconstructible manifold.

The central design is:

```text
TREE       = deterministic reconstruction skeleton
MANIFOLD   = semantic and relational topology
SUMMARY    = progressive compressed view
SOURCE     = authority anchor
OVERLAY    = append-only evolution
RECEIPT    = reconstruction evidence
```

An index may point to other indexes. Each subsystem may own a local manifold. The global root only needs enough information to reach the next index; it does not need to duplicate every child object.

## Formal model

```text
MΩI = (V, Es, Er, H, Σ, P, O, G)
```

- `V`: typed nodes.
- `Es`: structural edges for deterministic reconstruction.
- `Er`: semantic/relational edges for cross-tree navigation.
- `H`: optional hyperedges.
- `Σ`: multi-scale summary pyramid.
- `P`: provenance and source anchors.
- `O`: append-only overlays/supersession chain.
- `G`: gaps and reconstruction diagnostics.

Structural edges are acyclic. Semantic relations may contain cycles.

This distinction is essential: a concept may relate back to another concept without making the filesystem/index reconstruction cyclic.

## Existing assets reused

This scaffold does not replace the existing navigation layers. It references them:

- `data/knowledge_forest/rll_route_forest_blueprint.json`
- `data/knowledge_forest/rll_route_forest_overlay_20260731.json`
- `data/knowledge_forest/rll_route_flow_events.jsonl`
- `data/navigation/scientific_mechanisms.v1.json`
- `tools/build_knowledge_matrix.py`
- `AGENTS.md`

The current route forest is treated as a subordinate index and historical structural snapshot.

## Machine-readable contract

The root scaffold is:

`data/navigation/rll_manifold_index_scaffolding_v1.yml`

Its schema is:

`schemas/rll_manifold_index_scaffolding_v1.schema.json`

Validation is performed by:

`tools/validate_rll_manifold_index_scaffolding.py`

Tests:

`tests/test_rll_manifold_index_scaffolding.py`

## Recursive indexes

A root index should remain thin:

```text
MIDX:RLL:ROOT:v1
├── MIDX:RLL:ROUTE_FOREST:v1
├── MIDX:RLL:SCIENTIFIC_NAV:v1
├── MIDX:RLL:KNOWLEDGE_MATRIX:v1
└── MIDX:RLL:MIDDLEWARE_HOUSE:v1
    └── MIDX:RLL:MANIFOLD_DRIVE:v1
```

Each child may independently expose further indexes, summaries, relations and overlays.

An index stores references such as:

```text
child_id
locator
primary parent
summary pointer
source pointer
revision/hash
reconstruction order
```

It does not copy the child corpus by default.

## Summary pyramid

The summary hierarchy is progressive disclosure:

| Level | Role | Approximate target |
|---|---|---:|
| Σ0 | label | 12 tokens |
| Σ1 | micro orientation | 32 |
| Σ2 | brief selection context | 128 |
| Σ3 | module capsule | 512 |
| Σ4 | cross-child synthesis | 2048 |
| Σ5 | expanded reconstruction | context-dependent |
| Σ6 | source view | original references |

A higher summary may be derived from lower summaries, but must preserve a reversible provenance path to underlying nodes/sources.

If children disagree, the parent must preserve the disagreement as a typed relation rather than average it away.

## Reconstruction algorithm

Conceptually:

```text
resolve(root)
→ apply ordered overlays
→ traverse structural edges by explicit child order
→ resolve inheritance by reference
→ select semantic relations for requested view
→ choose summary level according to navigation budget
→ attach provenance and gaps
→ emit reconstruction receipt
```

A small query therefore does not require reading the whole corpus.

## Navigation budgets

Examples:

- `tiny`: root + Σ0/Σ1 + direct indexes.
- `small`: Σ2, depth 2.
- `medium`: Σ3 plus selected relation neighborhood.
- `large`: Σ4 with evidence/source pointers.
- `source`: Σ6 and exact source anchors.

Budget changes expansion only. It does not change truth or epistemic state.

## Structural invariants

The validator enforces:

1. root has no primary parent;
2. every non-root node has exactly one structural primary parent;
3. every structural child resolves;
4. structural graph is acyclic;
5. every node has summary orientation;
6. every node has source/index provenance;
7. semantic relation endpoints resolve;
8. reconstruction recipes point to existing roots and summary levels;
9. navigation cannot set `claim_allowed=true`.

A failed invariant emits a failed reconstruction receipt rather than silently repairing the graph.

## Drive scaffold

The documentary mirror is:

<https://drive.google.com/drive/folders/15dhrj0iJTIRID1UyuOKlN_XXCtIZk6GB>

It contains:

```text
00_ROOT_INDEX
01_SUMMARY_PYRAMID
02_NODE_MANIFESTS
03_RELATION_INDEXES
04_RECONSTRUCTION_RECIPES
05_OVERLAYS_AND_SUPERSESSION
```

Canonical Drive specification:

<https://docs.google.com/document/d/1grVcmNnOJZvxNN7BlyIpBE9DHbygRpK3LesK_EcfSIw/edit>

Summary pyramid specification:

<https://docs.google.com/document/d/1UOFfqfrHJFgj2pDFYg-2CIrMMjG4pS739C0BQrkqeFk/edit>

## Inheritance

Inheritance is referential, not copy-based.

Supported semantic inheritance relations include:

- `INHERITS`
- `SPECIALIZES`
- `GENERALIZES`
- `DERIVES_FROM`
- `IMPLEMENTS`
- `REPRODUCES`
- `EVIDENCE_FOR`
- `BLOCKED_BY`
- `SUPERSEDES`

This allows one concept to be reused across many modules without proliferating divergent copies.

## Append-only evolution

Base structural snapshots may remain immutable.

Changes can be represented through ordered overlays:

```text
ADD_NODE
ADD_EDGE
PATCH_METADATA
MOVE_PRIMARY_PARENT
ADD_SUMMARY
INVALIDATE_SUMMARY
SUPERSEDE_NODE
SUPERSEDE_EDGE
```

Historical reconstruction becomes:

`BASE + overlays[0..revision]`.

No silent deletion is required.

## Relationship to L9 and S7

Nodes can expose only relevant navigation dimensions:

- L — longitudinal
- O — orthogonal
- T — transversal
- P — provenance
- C — contextual
- R — relational
- I — indexical
- E — evidential
- A — adaptive

And one S7 scale:

`token → block → file → project → ecosystem → corpus → manifold`.

Unused dimensions remain absent or `TOKEN_VAZIO`.

## Boundary

A valid manifold means the navigation/reconstruction contract is internally coherent.

It does **not** mean:
- scientific claims are validated;
- references are automatically authoritative;
- a summary replaces original evidence;
- agreement between nodes/agents is independent confirmation.

## R3

`F_ok`: recursive index scaffold, schema, validator, tests and Drive mirror are materialized.  
`F_gap`: first runtime reconstruction receipt and integration with broader generated indexes are not yet terminal.  
`F_next`: run validator/tests in CI, then emit the first deterministic root reconstruction receipt and progressively bind additional local manifolds by reference.
