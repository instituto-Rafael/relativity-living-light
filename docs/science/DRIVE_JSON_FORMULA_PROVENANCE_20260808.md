# Drive JSON Formula Provenance Intake — 2026-08-08

```text
status=OBSERVED_LIMITED
claim_allowed=false
scope=Google Drive JSON/JSONL formula indexing
policy=evidence-first / fail-closed / preserve-origin
```

## 1. Fato observado

The Drive snapshot contains two complementary JSONL layers:

- `NORMALIZED-UPLOADED-TXT-ALL-BATCHES.jsonl`: source-oriented normalized records with `formula_hashes`.
- `GRAPH-UPLOADED-TXT-ALL-BATCHES.jsonl`: graph nodes and edges, including nodes with `type="FORMULA"` and provenance relations such as `HAS_FORMULA` / `FROM_SOURCE`.

The downloaded snapshot used for this intake produced:

```text
normalized_sources          = 26
formula_references          = 324
formula_hashes_unique       = 320
graph_formula_nodes         = 198
graph_missing_formula_nodes = 122
graph_extra_formula_nodes   = 0
```

The machine-readable receipt is:

`data/provenance/drive_formula_index_20260808.json`

and its fail-closed validator is:

`tools/validate_drive_formula_index.py`.

## 2. Lacuna

The exact observed gap is

```text
320 unique normalized formula hashes
-198 graph FORMULA nodes
=122 missing graph nodes
```

This is an **indexing/materialization gap**.

It does **not** prove that 122 formulas are absent from the original corpus. The normalized layer already references those hashes. Therefore the correct state is:

```text
formula_exists_in_source_text = TOKEN_VAZIO until source text is reconstructed
graph_materialization         = MISSING for 122 hashes
claim_allowed                 = false
```

## 3. Invariants

The intake enforces:

1. preserve every 64-hex formula hash exactly;
2. preserve source identity (`source_id`, filename and source SHA-256);
3. never synthesize formula text from a hash;
4. never treat `[H]` / `FORMULA` as proof of mathematical validity;
5. distinguish `missing graph node` from `missing original formula`;
6. keep `claim_allowed=false` until the expression is reconstructed and classified.

## 4. Coherent insertion rule

A Drive-derived expression may enter `rll_equation_registry.yml` only after the following bridge exists:

```text
formula_hash
  -> source_id
  -> source_path/message pointer
  -> literal expression
  -> normalized expression
  -> domain/type/unit check
  -> classification
  -> proof/test receipt
```

Allowed classifications for reconstructed expressions:

```text
EXACT_IDENTITY
KNOWN_PHYSICS
KNOWN_STATISTICS
VALID_DEFINITION
VALID_WITH_ASSUMPTIONS
AUTHOR_MODEL
HEURISTIC
ANALOGY_ONLY
NOT_WELL_DEFINED
FAIL
TOKEN_VAZIO
```

A hash alone is never enough to choose one of these.

## 5. Priority reconstruction queue

The densest normalized sources in this snapshot are:

| source | formula refs |
|---|---:|
| `Auditoria de Arquitetura Matemática.txt` | 66 |
| `Análise técnica da imagem.txt` | 48 |
| `Espiral Longitudinal Ω.txt` | 31 |
| `Auditoria semântica e otimização.txt` | 28 |
| `Formalismo 7D e Problemas Matemáticos.txt` | 25 |
| `Cânone do Cosmos.txt` | 20 |
| `Recorrência e plasticidade cerebral.txt` | 19 |

These are retrieval priorities, not quality rankings.

## 6. Procedure for each recovered expression

For each `formula_hash`:

```text
FATO
  literal source expression + exact source pointer

LACUNA
  undefined symbols, missing units, missing domains, missing assumptions

INVARIANTE
  hash identity + source identity + literal expression

VARIANTE
  normalized notation or a separately labeled corrected form

PROVA
  symbolic identity, executable regression, dimensional check,
  likelihood test, empirical dataset or TOKEN_VAZIO

PARÁBOLA
  optional explanatory layer only; never evidence

RETROALIMENTAÇÃO
  registry entry / test / contradiction edge / blocked claim
```

## 7. Relation to existing RLL audits

Existing mathematical/scientific audits remain authoritative over semantic promotion. A newly recovered Drive formula must not override a prior `FAIL`, `TOKEN_VAZIO`, or `ANALOGY_ONLY` state merely because the same expression occurs many times.

Repetition is evidence of corpus prevalence, not evidence of truth.

## 8. Closure

```text
F_ok:
  Drive JSON/JSONL formula inventory materialized in repository
  source -> formula hash provenance preserved
  exact 122-node materialization gap recorded
  executable validator + regression tests added

F_gap:
  literal expression text for all 320 hashes not yet reconstructed
  122 graph nodes not yet materialized
  mathematical classification pending per expression

F_next:
  reconstruct literal formulas from message/source records
  deduplicate by normalized expression while preserving raw hashes
  classify and test one source family at a time
```
