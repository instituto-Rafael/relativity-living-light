# RLL — Canonical Family Pipeline V1

**State:** `CANONICAL_PIPELINE / RECEIPT_CHAIN / FAIL_CLOSED`  
**Claim boundary:** `claim_allowed=false`  
**Route:** `SOURCE -> FAMILY EXECUTORS -> CROSS-FAMILY CONTRACT -> GATES -> RECEIPTS -> R3`

## Purpose

This pipeline makes the bounded mathematical families talk to one another without turning arithmetic or geometric coherence into an RLL physical claim. It composes typed set/void states; number theory, factorization and repunits; prime/base structure; modular/CRT coordinates; functional, factor-incidence and Cayley graphs; polygon/star-polygon geometry; prime/base abscissa curves; discrete graph-flow conservation; and continuity/Bernoulli/Venturi helpers under declared assumptions.

Canonical boundaries:

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
ZERO != EMPTY_SET != NULL != TOKEN_VAZIO
FORMAL_COHERENCE != PHYSICAL_BINDING
```

## Canonical route

```text
SOURCE_MIN
  -> source custody + SHA-256
  -> permutation/typed-void census
  -> set/number/prime/graph/fluid family bridge
  -> prime/base abscissa carrier
  -> CROSS-FAMILY CONTRACT
  -> 12 FAIL-CLOSED GATES
  -> CHILD RECEIPTS + SHA-256
  -> FINAL RECEIPT
  -> R3
```

Implementation: `tools/rll_canonical_family_pipeline_v1.py`  
CI: `.github/workflows/rll-canonical-family-pipeline-v1.yml`  
Schema: `schemas/rll_canonical_family_pipeline_receipt_v1.schema.json`

## Cross-family conversations

### Set <-> modular <-> abscissa

`0 mod m` is an occupied residue state. With `theta_m(n)=2*pi*(n mod m)/m`, zero residue maps to `(1,0)` and does not remove `x=n`.

### Number <-> prime <-> base

```text
R6=(10^6-1)/9=111111
111111=3*7*11*13*37
```

For the selected primes, the base-10 unit-prime carrier is exactly `(3,7,11,13,37)` and its joint period equals `111111`. This is base-dependent arithmetic, not a physical period.

### Number <-> graph

Factorization becomes a bipartite incidence graph `number <-> prime factor`, including `21 <-> {3,7}`, `42 <-> {2,3,7}`, and `1001 <-> {7,11,13}`.

### Repdigit <-> modular graph

Appending digit 7 modulo 3 gives one 3-cycle. Appending digit 3 modulo 7 gives one 6-cycle plus the fixed point 2. The gate verifies transition operators, not visual digit coincidence.

### CRT <-> product carrier

The complete 21-carrier round-trips through `(mod 3,mod 7)` and the complete 42-carrier through `(mod 2,mod 3,mod 7)`.

### Geometry <-> typed steps

`{5/1}!={5/2}` and `{12/1}!={12/5}`. Equal vertex count does not erase the star/polygon step.

### Graph <-> fluid

For directed fluxes, `balance(v)=incoming-outgoing`. The canonical junction has balance exactly zero. This zero means conservation, not missingness.

### Fluid formalism <-> physical boundary

Continuity and ideal Bernoulli/Venturi fixtures may pass under declared assumptions. They cannot synthesize an RLL fluid state. Expected boundaries remain:

```text
TOKEN_VAZIO_FLUID_BINDING
TOKEN_VAZIO_COSMOLOGY_BINDING
claim_allowed=false
```

## Twelve canonical gates

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

G11 and G12 PASS only when the pipeline correctly refuses physical promotion without the missing evidence contract.

## Receipt chain

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

The final receipt stores SHA-256 plus byte length of every JSON child receipt. The YAML validates it against the root structural schema, executes focused tests, enforces the exact receipt set, requires 12/12 gates PASS, and uploads the whole custody directory as a mandatory artifact with 30-day retention.

## Completion contract

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

Physical-model discovery is deliberately outside this closure. Any successor requires a separate preregistered observable, units, covariance, data provenance, falsifier and independent reproduction.

## R3

```text
F_ok:
  canonical cross-family orchestration + YAML + schema + tests + receipts +
  custody hashes + 12 fail-closed gates.

F_gap:
  no bounded implementation gap after a green canonical run;
  physical fluid/cosmology bindings remain intentionally TOKEN_VAZIO.

F_next:
  NONE for this bounded pipeline;
  any physical successor starts a new preregistered evidence route.
```
