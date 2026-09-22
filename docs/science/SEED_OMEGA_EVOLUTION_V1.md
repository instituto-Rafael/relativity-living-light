# RLL — SEED Ω Evolutionary Model Contract V1

**Date:** 2026-09-15
**Base authority:** `rll/lab`
**State:** `MODEL_CONTRACT / EXECUTION_TOKEN_VAZIO`
**claim_allowed:** `false`

## Purpose

Define a bounded evolutionary-model contract for scientific model seeds. The contract supports isolated lineages, typed transforms, recombination, mutation, recurrence diagnostics and multidimensional selection without equating computational evolution with biological evolution.

## State

`S_n=(G_n,X_n,E_n,M_n,P_n)`

where `G` is computational genotype, `X` realized state/phenotype, `E` environment, `M` append-only memory, and `P` provenance.

## Transition

`S_(n+1)=T(S_n, operator, environment, mutation, recombination)`.

All transition inputs are versioned. Missing inputs produce `TOKEN_VAZIO`, never implicit defaults.

## Operator algebra boundary

`DIRECT`, `INVERSE`, `REVERSE`, `ANTIDERIVATIVE`, `RECLUSIVE_CLOSURE`, `LOG`, `ITERATED_LOG`, `TANGENTIAL`, `ORTHOGONAL`, `TRANSVERSAL`, `LATERAL`, `RECURSIVE`, `PERMUTE`, `RECOMBINE`, `GEODESIC_STEP`.

Every operator must declare domain, codomain, preconditions and reversibility class.

`ANTIDERIVATIVE != UNIQUE_INVERSE` and `REVERSE != INVERSE`.

## Geometric scale

`q=sqrt(3)/2`.

`a_n=a_0 q^n`.

RLL must preserve the existing boundary: Euclidean contraction is not automatically a Poincare/hyperbolic geodesic. `GEODESIC_STEP` is enabled only with an explicit manifold, metric and exponential/retraction operator.

## Recombination

A child may inherit typed components from multiple parents only through a compatibility matrix:

`child = R(parent_1,...,parent_k; compatibility, weights, mutation)`.

Provenance records all parent IDs and transforms.

## Recurrence with memory

`X_(n+p)≈X_n` may hold while `M_(n+p)!=M_n`.

Therefore recurrence is measured separately on bounded projections and full append-only state.

## Search-space control

Finite generations may have combinatorially large candidate counts. The system must use bounded branching, predeclared stop rules and Pareto filtering rather than imply literal infinity.

## Evaluation

`Q=(coherence, novelty, reconstruction, evidence, robustness, cost)`.

Default selection is nondominated Pareto frontier. Any scalarization must declare weights before evaluation.

## Biological analogies

`DNA-like inheritance` and `water-like plasticity` are pedagogical analogies only.

`COMPUTATIONAL_GENOTYPE != BIOLOGICAL_DNA`.

`MODEL_PLASTICITY != WATER_PHYSICS`.

## Execution gate

An implementation may be promoted only after:

1. deterministic seed manifest;
2. parent lineage validation;
3. operator-domain validation;
4. deterministic replay under fixed seed;
5. mutation/recombination receipts;
6. negative tests;
7. independent rerun.

Until then:

`EVOLUTION_RUNTIME=TOKEN_VAZIO`
`SCIENTIFIC_MODEL_GAIN=TOKEN_VAZIO`
`claim_allowed=false`

## Producer route

The intended evidence producer is RafPolimata. No RafPolimata implementation is claimed by this contract.

## R3

**F_ok:** model contract and boundaries defined.
**F_gap:** executable producer, calibration, benchmark and independent reproduction remain `TOKEN_VAZIO`.
**F_next:** implement bounded deterministic evolution engine in RafPolimata and publish hash-bound receipts.


## Quiescent knowledge bank

The in-vitro model is a low-activity knowledge bank, not merely isolated execution.

[
activity(S_i)approx0

otRightarrow
S_i=emptyset.
]

Every preserved lineage may be reactivated later. No state is silently discarded because it is currently unexplained or apparently noisy.

## Non-linear lineage topology

The canonical topology is a temporal typed hypergraph:

[
mathcal H=(V,mathcal E,	au).
]

A child may have multiple parents, including an ancestor used by backcross. The graph remains temporally directed because every new child has a later generation/event timestamp.

[
LINEAGE
eq LINEAR_SEQUENCE.
]

## Latent relation gate

A relation may be absent from the current projection while still derivable from stored structure.

[
HIDDEN_IN_PROJECTION

eq
ABSENT_FROM_MODEL.
]

Control example:

[
h=(sqrt3/2)a
]

for an equilateral triangle.

Discovery of a latent relation must record the derivation and source state rather than relabel it as newly created information.

## Backcross operator

For current lineage (S_n), ancestor (A_k), and trait mask (M):

[
S_{n+1}=B(S_n,A_k;M).
]

Required receipt fields:

- current parent ID;
- ancestor ID;
- selected trait IDs;
- compatibility result;
- transform parameters;
- pre/post trait diff;
- deterministic seed;
- output hash.

Backcross creates a new node. It never rewrites the ancestor or current parent.

## Practice-theory residual

Define:

[
Delta_{PT}=d(O_{practice},P_{theory}).
]

Initial classification:

[
owner(Delta_{PT})=TOKEN_VAZIO_RESIDUAL_OWNER.
]

Allowed later classifications include measurement noise, model misspecification, discretization artifact, unmodeled structure, implementation gap, theory-only prediction, practice-only effect, contradiction and anomaly.

Hard invariant:

[
PRACTICE_THEORY_MISMATCH

eq
AUTOMATIC_NOISE_ASSIGNMENT.
]

## Additional operators

`INDIRECT`
`DERIVATIVE`
`BACKCROSS`
`QUIESCE`
`REACTIVATE`
`LATENT_RELATION_PROBE`
`NOISE_RECLASSIFY`

