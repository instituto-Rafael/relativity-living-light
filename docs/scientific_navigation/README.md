# RLL Scientific Navigation Bundle V1

## Status

```text
implementation = claim_bounded_navigation
scientific_validation = false
claim_allowed = false
```

## Purpose

This layer reduces repository uncertainty without reducing scientific depth. It inventories registered mechanisms, preserves their authority boundaries, hashes located evidence, emits one capsule per mechanism and consolidates unresolved questions as typed `TOKEN_VAZIO` records.

It does **not** declare RLL true, superior, peer reviewed or experimentally confirmed.

## Canonical flow

```text
concept or mechanism
→ authority path
→ required repository sources
→ located evidence + SHA-256
→ allowed and blocked claim language
→ typed uncertainty
→ required closure evidence
→ evidence capsule
→ navigation bundle
→ human review
```

## Core files

| Path | Role |
|---|---|
| `data/navigation/scientific_mechanisms.v1.json` | Registry of mechanisms, authorities, claims and seed uncertainties |
| `schemas/rll_evidence_capsule.v1.schema.json` | Structural contract for one mechanism capsule |
| `schemas/rll_token_vazio.v1.schema.json` | Structural contract for one unresolved uncertainty |
| `tools/build_scientific_navigation_bundle.py` | Read-only builder and hasher |
| `tests/test_scientific_navigation_bundle.py` | Fail-closed regression tests |
| `.github/workflows/rll-scientific-navigation.yml` | Orchestrates validation, build and artifact publication |

## TOKEN_VAZIO contract

A `TOKEN_VAZIO` is not a decorative label and is never converted to zero evidence.

Every record carries:

```text
identifier
uncertainty type
mechanism
source paths
state
severity
claim weight = 0
blocked claims
affected artifacts
required evidence
resolution evidence
F_next
```

Promotion is allowed only when the required evidence is materialized, linked and reviewed. A workflow success does not close a scientific uncertainty by itself.

## Evidence capsule

Each mechanism emits:

```text
capsules/<mechanism_id>/CAPSULE.json
```

The capsule records:

- commit and authority path;
- repository inputs;
- inventory execution state;
- allowed limited statements;
- blocked statements;
- located artifacts and SHA-256;
- open uncertainty count;
- `F_ok`, `F_gap` and `F_next`;
- `claim_allowed=false`.

For workflow mechanisms, `METADATA_READY` means the workflow source and registered repository objects were inspected. It does not mean a fresh workflow run was executed. Runtime artifact contents require a concrete run receipt.

## Bundle outputs

```text
INDEX.md
NAVIGATION_MANIFEST.json
TOKEN_VAZIO_LEDGER.jsonl
CLAIM_MATRIX.csv
MECHANISM_MATRIX.csv
DEPENDENCY_GRAPH.json
RECEIPT.json
F_OK_F_GAP_F_NEXT.md
capsules/*/CAPSULE.json
CHECKSUMS.sha256
```

Recommended review order:

1. verify `CHECKSUMS.sha256`;
2. read `NAVIGATION_MANIFEST.json`;
3. rank `TOKEN_VAZIO_LEDGER.jsonl` by severity and dependency;
4. inspect blocked claims in `CLAIM_MATRIX.csv`;
5. open only the capsules affected by the current delta;
6. choose one uncertainty closure operation;
7. rerun and compare the next bundle.

## Local execution

```bash
python -m pytest -q tests/test_scientific_navigation_bundle.py

python tools/build_scientific_navigation_bundle.py \
  --root . \
  --output artifacts/rll-scientific-navigation
```

Strict repository-source mode:

```bash
python tools/build_scientific_navigation_bundle.py \
  --root . \
  --output artifacts/rll-scientific-navigation \
  --strict
```

Strict mode fails only when a registered **required repository path** is absent. Open scientific uncertainties remain explicit records and do not make the bundle disappear.

## Extension rule

To add a mechanism:

1. register one stable `mechanism_id`;
2. identify its authority file;
3. separate required sources from optional evidence;
4. state limited allowed language;
5. state blocked language;
6. add typed uncertainties with closure evidence;
7. add or update tests;
8. review the generated capsule before merge.

Do not place scientific meaning solely in the workflow YML. YML orchestrates execution; registries, schemas, code, evidence and review establish meaning.

## Current seed scope

V1 federates four surfaces already present in the repository:

- canonical real-data execution;
- Tier 1 scientific skills;
- central traceability map;
- textual result manifest.

Future expansion should add one mechanism at a time, preferably after it already emits a stable receipt and checksum set.

## Final invariant

```text
missing evidence → TOKEN_VAZIO with closure route
contradictory evidence → preserve contradiction
located file → hash and classify
CI success → operational evidence only
scientific claim → remains blocked until its own gate is satisfied
```
