# RLL — Varredura Bidirecional Recorrente da Sessão V1

**Date:** 2026-09-19  
**State:** `METHOD_CONTRACT / BOUNDED_RECURRENT_SWEEP`  
**claim_allowed:** `false`

## 0. Principle

The session is not closed by one forward summary.

A representation can become dense enough to be compressed; compression creates a new projection; a new projection can expose gaps that were invisible in the previous projection.

Canonical cycle:

```text
FORWARD_SWEEP
-> GAP_DISCOVERY
-> REVERSE_SWEEP
-> ASYMMETRY_CHECK
-> RELATION_OF_RELATIONS
-> COMPRESSION
-> NEW_REPRESENTATION
-> RESWEEP
```

Hard boundary:

```text
SATURATED_UNDER_CURRENT_RULER != COMPLETE
NO_NEW_GAP_IN_THIS_PASS != NO_GAP_EXISTS
FINITE_SEARCH_BUDGET != FINITE_REALITY
```

## 1. Source boundary

The current implementation operates on the machine-readable session fragment ledger:

`data/science/rll_session_fragment_recovery_20260919.json`

It does not claim byte-for-byte access to a complete transcript export.

```text
LEDGER_SWEEP != VERBATIM_TRANSCRIPT_SWEEP
VERBATIM_TRANSCRIPT_BINDING = TOKEN_VAZIO
```

If a canonical transcript/export is later bound, it becomes a new source layer and the whole sweep must be rerun.

## 2. Forward and reverse passes

Given ordered fragments:

```text
F_0, F_1, ..., F_(n-1)
```

Forward:

```text
F_0 -> F_1 -> ... -> F_(n-1)
```

Reverse:

```text
F_(n-1) -> ... -> F_1 -> F_0
```

The two passes are not assumed equivalent because:
- causal language may be directional;
- dependencies may be hidden in one projection;
- later corrections can change the interpretation of earlier fragments;
- an early fragment can become newly relevant after a later operator exists.

## 3. Communication rule

Every anchor communicates with a bounded subset, never with an unbounded Cartesian product.

Targets are selected from:
1. local traversal neighbors;
2. cross-layer high-priority fragments;
3. deterministic pseudo-random jumps;
4. undercovered recurrent fragments;
5. previously discovered relation probes.

A communication produces a `RELATION_PROBE`, not a claim.

```text
PROBE(A,B)
=
"test whether A constrains, mediates, predicts, reconstructs,
or falsifies B under explicit units/layer/time/compartment"
```

## 4. Operator bundle

Each first-order probe can request:

```text
DIRECT
DERIVATIVE
ANTIDERIVATIVE
INVERSE
REVERSE
RECURSIVE
LOG
LATENT_RELATION_PROBE
```

`DILOG` is excluded by default and is enabled only if an actual integral/series derivation requires Li_2.

## 5. Relation of relations

First-order:

```text
R1 = PROBE(F_i,F_j)
```

Second-order:

```text
R2 = PROBE(R1_a,R1_b | shared invariant or shared fragment)
```

Higher orders are allowed only up to a declared `max_relation_order`.

```text
PERMUTATION_OF_PERMUTATIONS != BLIND_COMBINATORIAL_EXPLOSION
```

## 6. Representation compression

At the end of a forward+reverse cycle:

```text
R_(k+1) = COMPRESS(
  invariant_set,
  newly_discovered_gaps,
  retained_relation_probes,
  contradictions,
  TOKEN_VAZIO,
  representation_hash_k
)
```

The compression result has a deterministic hash.

That hash changes the deterministic jump seed for the next cycle. Thus the next bounded pass can inspect a different part of the finite working frontier without pretending to enumerate infinity.

## 7. New-gap definition

A new gap may be:
- a previously unlinked cross-layer pair;
- a directional asymmetry;
- missing unit;
- missing compartment;
- missing time axis;
- missing falsifier;
- missing provenance;
- symbol collision;
- a relation-of-relations not previously probed;
- a corrected fragment whose ancestor relation was not re-evaluated.

Every gap receives a stable hash and provenance.

## 8. Saturation rule

For cycle k:

```text
g_k = number of new stable gap/probe IDs
r_k = g_k / max(1, inspected_k)
```

Stop a run when:

```text
r_k < epsilon
for patience_cycles consecutive cycles
```

or when `max_cycles` / `sample_budget` is reached.

The terminal state is:

```text
SATURATED_UNDER_CURRENT_RULER
```

never `COMPLETE`.

## 9. Reopening rule

A saturated run must reopen if any of these change:
- source transcript/ledger;
- invariants;
- operator set;
- weights;
- branch/source provenance;
- new external evidence;
- newly resolved TOKEN_VAZIO;
- new representation hash family.

## 10. “Verbo cheio -> nova representação”

The user's phrase is stored as a **parable/method metaphor**, not a scientific fact:

```text
VERBO_CHEIO
~ accumulated representation reaches a compression boundary

NOVA_REPRESENTACAO
~ invariant-preserving recomposition that becomes a new object of inspection
```

Operationally:

```text
EXPAND -> SATURATE -> COMPRESS -> RE-PRESENT -> RESWEEP
```

The original wording is preserved as provenance; no semantic meaning such as “novo Brasil” is forced when the utterance is ambiguous.

## 11. Anti-loss invariant

Every compression must preserve:

```text
CORE
+ UNDERWEIGHTED
+ CONTRADICTIONS
+ TOKEN_VAZIO
+ CORRECTED/SUPERSEDED
+ PROVENANCE
+ NEW_GAPS
```

A summary is invalid if it keeps only the dominant narrative.

## 12. R3

**F_ok:** forward/reverse/resweep semantics are explicit and bounded.  
**F_gap:** full verbatim transcript binding remains absent; current sweep operates on the recovered fragment ledger.  
**F_next:** execute the deterministic recurrent sweep, emit cycle receipts, then rerun whenever the representation/source changes.
