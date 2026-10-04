# RLL — Canonical Family Pipeline V1

**State:** `CANONICAL_PIPELINE / RECEIPT_CHAIN / FAIL_CLOSED`  
**Claim boundary:** `claim_allowed=false`  
**Route:** `SOURCE -> FAMILY EXECUTORS -> CROSS-FAMILY CONTRACT -> GATES -> RECEIPTS -> R3`

## 0. Purpose

This pipeline makes the bounded mathematical families talk to one another without
turning arithmetic or geometric coherence into an RLL physical claim.

It composes:

- typed set/void states;
- number theory, factorization and repunits;
- prime/base multiplicative structure;
- modular/CRT coordinates;
- functional, factor-incidence and Cayley graphs;
- polygon/star-polygon geometry;
- prime/base abscissa curves;
- discrete graph-flow conservation;
- continuity and Bernoulli/Venturi helpers under declared assumptions.

The canonical physical boundary remains:

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
ZERO != EMPTY_SET != NULL != TOKEN_VAZIO
FORMAL_COHERENCE != PHYSICAL_BINDING
```

## 1. Canonical pipeline

```text
SOURCE_MIN
  |
  v
01 source custody + SHA-256
  |
  +--> permutation/typed-void census
  |
  +--> set/number/prime/graph/fluid family bridge
  |
  +--> prime/base abscissa carrier
  |
  v
CROSS-FAMILY CONTRACT
  |
  v
12 FAIL-CLOSED GATES
  |
  v
CHILD RECEIPTS + SHA-256
  |
  v
FINAL RECEIPT
  |
  v
R3
```

The implementation is `tools/rll_canonical_family_pipeline_v1.py`.
The CI orchestration is `.github/workflows/rll-canonical-family-pipeline-v1.yml`.

## 2. Cross-family conversations

### 2.1 Set <-> modular <-> abscissa

`0 mod m` is an occupied residue state. For a phase embedding,

```text
theta_m(n) = 2*pi*(n mod m)/m
```

a zero residue maps to `(cos 0, sin 0)=(1,0)`. It does not remove the
abscissa `x=n`.

### 2.2 Number <-> prime <-> base

For base 10,

```text
R6 = (10^6-1)/9 = 111111
111111 = 3*7*11*13*37
```

and the selected primes coprime to base 10 are exactly
`(3,7,11,13,37)`. Their joint prime carrier period equals `111111`.

This is an exact base-dependent arithmetic relation, not a physical period.

### 2.3 Number <-> graph

Factorization becomes a bipartite incidence graph:

```text
number node <-> prime-factor node
```

Examples include `21 <-> {3,7}`, `42 <-> {2,3,7}` and
`1001 <-> {7,11,13}`.

### 2.4 Repdigit <-> modular graph

Appending digit 7 modulo 3 gives one 3-cycle. Appending digit 3 modulo 7
gives a 6-cycle plus one fixed point. The pipeline verifies these from the
transition operators rather than from digit-shape inspection.

### 2.5 CRT <-> graph/product carrier

The 21-carrier is reconstructed from `(mod 3, mod 7)`.
The 42-carrier is reconstructed from `(mod 2, mod 3, mod 7)`.
Every state in each finite carrier is round-tripped by the gate.

### 2.6 Geometry <-> typed graph steps

`{5/1}` remains distinct from `{5/2}` and `{12/1}` remains distinct from
`{12/5}`. Equal vertex counts do not collapse polygon and star-polygon steps.

### 2.7 Graph <-> fluid conservation

For directed edge fluxes `q_e`, node balance is

```text
balance(v) = incoming(v) - outgoing(v).
```

The canonical fixture has `balance(junction)=0`.

That zero means conservation. It is not a missing measurement and not
`TOKEN_VAZIO`.

### 2.8 Fluid mathematics <-> physical boundary

The pipeline can verify a declared continuity fixture and ideal
Bernoulli/Venturi algebra. It cannot create a physical RLL fluid state.

The expected state is therefore:

```text
TOKEN_VAZIO_FLUID_BINDING
TOKEN_VAZIO_COSMOLOGY_BINDING
claim_allowed=false
```

A pipeline run **passes** the boundary gate when those claims remain blocked
until their independent physical contracts exist.

## 3. Gates

The final receipt requires all twelve gates to PASS:

1. `G01-SOURCE-CUSTODY`
2. `G02-CLAIM-BOUNDARY`
3. `G03-ZERO-TYPING`
4. `G04-REPUNIT-PRIME-BASE`
5. `G05-FUNCTIONAL-GRAPHS`
6. `G06-CRT-ROUNDTRIP`
7. `G07-ABSCISSA-ZERO`
8. `G08-GEOMETRY-STEPS`
9. `G09-GRAPH-FLOW-CONSERVATION`
10. `G10-CONTINUITY-FIXTURE`
11. `G11-FLUID-FAIL-CLOSED`
12. `G12-COSMOLOGY-FAIL-CLOSED`

`G11` and `G12` do not mean that a physical model passed. They mean that the
pipeline correctly refused to manufacture one.

## 4. Receipt chain

Every successful run emits exactly:

```text
01_source_receipt.json
02_permutation_void_receipt.json
03_family_receipt.json
04_prime_base_abscissa_receipt.json
05_cross_family_receipt.json
06_gate_receipt.json
07_final_receipt.json
R3.md
```

The final receipt contains the SHA-256 and byte length of each JSON child
receipt. This provides a deterministic custody edge from child evidence to
the final closure.

The final receipt validates against:

`schemas/rll_canonical_family_pipeline_receipt_v1.schema.json`

## 5. Final states

### `PASS_FAIL_CLOSED`

Means all implementation and invariant gates passed, all mandatory receipts
exist, their custody hashes were materialized, and physical claims remain
blocked where evidence is absent.

### `FAIL`

Means one or more required source, invariant, receipt, schema or boundary
gates failed. In strict mode the executor exits non-zero.

There is no state in which a numerical coincidence automatically sets
`claim_allowed=true`.

## 6. CI contract

The YAML:

`.github/workflows/rll-canonical-family-pipeline-v1.yml`

uses:

- read-only GitHub contents permission;
- pinned checkout/setup-python/upload-artifact actions;
- no persisted checkout credentials;
- deterministic Python 3.11;
- bounded `pytest` + `jsonschema` dependencies;
- strict pipeline execution;
- JSON Schema validation;
- focused integration tests;
- exact receipt-set verification;
- 12/12 gate verification;
- mandatory artifact upload;
- 30-day receipt retention.

It runs on relevant pull-request changes, on `rll/lab` after promotion, and
manually through `workflow_dispatch`.

## 7. Completion contract

The bounded engineering task is complete only when:

```text
workflow == success
focused_tests == success
schema_validation == success
receipt_set == complete
12/12 gates == PASS
artifact == uploaded
claim_allowed == false
fluid_binding == TOKEN_VAZIO_FLUID_BINDING
cosmology_binding == TOKEN_VAZIO_COSMOLOGY_BINDING
```

Physical-model discovery is not an unfinished item in this pipeline. It is a
different successor task that requires its own preregistered observable,
units, covariance, data provenance, falsifier and independent reproduction.

## 8. R3

```text
F_ok:
  canonical cross-family orchestration + YAML + schema + tests + receipts +
  custody hashes + 12 fail-closed gates.

F_gap:
  no bounded implementation gap after a green canonical run.
  physical fluid/cosmology bindings remain intentionally TOKEN_VAZIO.

F_next:
  NONE for this bounded pipeline.
  any physical successor starts a new preregistered evidence route.
```
