# Hypothesis Instability Orchestrator V1

Status: `IMPLEMENTED_TRIAGE / claim_allowed=false`

## Purpose

Turn the authorial instability-topology idea into a fast, fail-closed routing layer for formula/hypothesis work.

The orchestrator does **not** decide whether a hypothesis is true. It decides whether a candidate is cheap enough and closed enough to deserve an expensive shadow-model execution.

Invariant:

```text
formula != mechanism != implementation != execution != evidence != claim
TOKEN_VAZIO != 0
barometer != probability
barometer != likelihood
barometer != evidence
```

## Components

```text
data/contracts/hypothesis_instability_barometer.v1.yml
    declarative graph, weights, thresholds and candidate states

tools/hypothesis_instability_barometer.c
    deterministic integer barometer and graph-tension engine

.github/workflows/hypothesis-instability-orchestrator.yml
    GitHub Action compiler, runner, artifact producer and generated matrix router
```

## Barometric topology

Each hypothesis is a node `i` with ten gap coordinates:

```text
formal
dimensional
mechanism
observable
data
covariance
nested_limit
stability
falsifier
reproduction
```

Each coordinate is mapped only for routing:

```text
CLOSED       -> 0
PARTIAL      -> 500
OPEN         -> 1000
TOKEN_VAZIO  -> 1000 + unknown counter
```

Let `w_k` be the YAML weight and `s_ik` the routing state value.

Intrinsic pressure:

\[
P_i = \left\lfloor
\frac{\sum_k w_k s_{ik}}{\sum_k w_k}
\right\rfloor.
\]

For an edge `i--j` with coupling weight `e_ij`, local topology tension is:

\[
T_i = \left\lfloor
\frac{\sum_j e_{ij}|P_i-P_j|}{\sum_j e_{ij}}
\right\rfloor.
\]

The fast barometer is:

\[
B_i = \left\lfloor\frac{3P_i+T_i}{4}\right\rfloor.
\]

This deliberately gives more weight to unresolved properties of the node than to disagreement with neighbors while still exposing instability gradients in the graph.

## Routes

The V1 contract uses:

```text
B <= 360                         -> EXECUTE_SHADOW
360 < B <= 690                   -> FORMALIZE_FIRST
B > 690                          -> BLOCKED_UNSTABLE
TOKEN_VAZIO count >= 4           -> BLOCKED_TOKEN_VAZIO
```

Thresholds are operational policy and may be versioned. Changing a threshold does not change scientific evidence.

## Initial candidate set

The first graph uses the seven candidates already prioritized by the governed DESI 50-hypothesis intake:

```text
H03 H46 H08 H29 H40 H05 H01
```

The YAML does not promote any of them. Initial CLOSED/PARTIAL/OPEN/TOKEN_VAZIO states encode routing distance to an executable test, not probability of truth.

## Fast-path behavior

```text
YAML graph
  -> compile tiny C binary with -O3
  -> one-pass parse
  -> integer pressure computation
  -> graph tension computation
  -> barometer.json
  -> matrix.json
  -> GitHub dynamic matrix only for EXECUTE_SHADOW candidates
```

Expensive likelihood or raw-data work is intentionally outside the first job. The barometer exists to avoid spending compute on candidates that still have basic formal, physical or evidentiary gaps.

## Generated evidence

Each run emits:

```text
results/hypothesis-instability/barometer.json
results/hypothesis-instability/matrix.json
results/hypothesis-instability/summary.md
route-<HYPOTHESIS_ID>.receipt
```

The result JSON includes a FNV-1a 64-bit fingerprint of the routing configuration for cheap change detection and custody correlation. FNV is used only as a fast configuration fingerprint, not as a cryptographic evidence hash.

## G1 / source-material boundary

G1/source material can provide candidate observations, relationships and falsifiers, but a media article is not promoted to primary scientific evidence. The correct route is:

```text
source observation
  -> candidate node/edge
  -> primary-paper/data pointer
  -> formal/physical closure
  -> shadow execution
  -> evidence gate
```

This keeps the author's instability topology useful for discovery without allowing contextual similarity to become a scientific claim.

## Extension contract

To scale from the seven priority nodes to all 50 governed hypotheses:

1. preserve `H01..H50` IDs from the canonical intake;
2. add only declared gap states;
3. use `TOKEN_VAZIO` for unknown states;
4. add graph edges only with an explicit relation class;
5. never encode probability-of-truth as a barometer weight;
6. route expensive cosmology only after the cheap gate;
7. preserve the canonical intake as source authority.

## Claim boundary

```text
implemented_C_barometer        = true
implemented_YAML_contract      = true
implemented_Action_router      = true
scientific_validation          = false
hypothesis_confirmation        = false
RLL_claim_promotion            = false
claim_allowed                  = false
```
