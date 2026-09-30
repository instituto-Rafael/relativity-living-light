# Drive formula graph reconstruction — Batch 1 — 2026-08-08

```text
status=OBSERVED_LIMITED
claim_allowed=false
route=audit/* -> rll/lab
source_snapshot=Drive NORMALIZED + GRAPH
source_literal=Auditoria de Arquitetura Matemática.txt
```

## Purpose

The original Drive snapshot contains 320 unique formula hashes, but only 198 materialized
`FORMULA` nodes. The provenance receipt therefore records 122 graph-node gaps.

This batch does **not** rewrite the Drive snapshot. It adds a supplemental, reproducible patch for
formula strings recovered from the original source material.

## Reconstruction rule

A formula is admitted to this patch only if all gates pass:

```text
source filename identified
-> literal formula recovered
-> SHA-256(literal UTF-8 formula) recomputed
-> hash exactly equals normalized formula_hash
-> hash belongs to original 122-node gap
-> claim_allowed remains false
```

No semantic approximation, LaTeX normalization, punctuation repair, Unicode substitution, or
"equivalent formula" is accepted. An algebraically equivalent expression with different bytes is
a different object for this custody layer.

## Batch 1 result

```text
original graph gap                 = 122
exact literal formulas recovered   = 18
remaining supplemental gap         = 104
```

All 18 come from the source:

```text
Auditoria de Arquitetura Matemática.txt
source_sha256 =
cb2c4adc80d9cf2525c32f2ce6df84a4baceaa43a47ce587fdcd057ad1b44243
```

Examples include:

```text
E(u,v)=1\iff\gcd(u,v)=1.
CMR\approx\frac1{\sqrt N}
\det A=0.
\delta(r-0.5)
```

Their presence in the corpus does **not** determine whether they are mathematically true,
physically meaningful, authorial definitions, counterexamples, or formulas being criticized by
the source document. That classification is a separate downstream gate.

## Files

- `data/provenance/drive_formula_graph_patch_20260808_batch1.jsonl`
- `tools/validate_drive_formula_graph_patch.py`
- `tests/test_drive_formula_graph_patch.py`

## Invariant

```text
hash match = identity/provenance evidence
hash match != theorem proof
hash match != physical validation
source occurrence != endorsement
```

## F_next

Continue source by source. Priority remains:

1. remaining formulas in `Auditoria de Arquitetura Matemática.txt`;
2. `Análise técnica da imagem.txt`;
3. `Espiral Longitudinal Ω.txt`;
4. `Auditoria semântica e otimização.txt`;
5. `Formalismo 7D e Problemas Matemáticos.txt`.

Each batch must reduce the supplemental gap only by exact byte-reproduced formula identities.
