# B10 Geophysical Systematics Bridge

**Date:** 2026-08-09  
**State:** `IMPLEMENTED_FAIL_CLOSED`  
**Claim boundary:** `claim_allowed=false`

## Purpose

RLL already consumes deterministic raw-channel receipts from the canonical `rafaelmeloreisnovo/Fisica` producer. This bridge adds the missing step between a valid local physical receipt and a scientifically controlled RLL *systematics diagnostic*.

It does not inject geophysical signals into the cosmological model. It asks a narrower question:

```text
can a synchronized environmental/geophysical record
be aligned to identified RLL observations
well enough to test an instrumental/environmental null hypothesis?
```

The bridge is therefore a contamination/null-model gate, not a new-physics gate.

## Chain

```text
Fisica raw channels
  -> deterministic geophysical receipt
  -> RLL receipt adapter
  -> LOCAL_CONTEXT_DATA_READY
  -> observation index + time/location join
  -> preregistered systematics metric
  -> SYSTEMATICS_DIAGNOSTIC_READY
```

The following transitions remain forbidden:

```text
local geophysical association -> cosmological evidence
systematics diagnostic -> RLL mechanism confirmation
diagnostic correlation -> residual correction
diagnostic correlation -> likelihood mutation
diagnostic correlation -> parameter mutation
synthetic fixture -> physical observation
```

## Contract

The executable implementation is:

```text
src/rll/geophysical_systematics_bridge.py
```

Example manifest:

```text
configs/rll_geophysical_systematics_link.example.json
```

Tests:

```text
tests/test_geophysical_systematics_bridge.py
```

A candidate link declares four groups.

### Provenance

Required custody fields:

- canonical Fisica repository;
- pinned 40-character producer commit;
- SHA-256 of the physical geophysical receipt;
- RLL preregistration identifier.

### Target observation index

The RLL dataset must expose a stable observation index hash plus explicit time and location bases. Without this mapping, local environmental measurements cannot be associated with cosmological observations.

This is a deliberate gate. Dataset-level cosmology without observation-level acquisition metadata remains `TOKEN_VAZIO` for this use.

### Join

The first supported join is:

```text
time_location_window
```

It requires a declared maximum time offset and counts of matched versus total observations. Zero matches becomes `NO_OVERLAP`, not success.

### Analysis discipline

Before a diagnostic can become ready, the contract requires:

- metric ID;
- baseline/null model;
- uncertainty model;
- multiple-testing control;
- falsifier;
- `residual_mutation_allowed=false`.

The bridge only establishes readiness to *test* whether an environmental variable is associated with RLL residual structure.

## State machine

```text
validation error
  -> BLOCKED

synthetic producer receipt
  -> TEST_FIXTURE_ONLY

valid but non-ready local receipt
  -> CONTEXT_ONLY

physical ready receipt + missing RLL alignment/preregistration
  -> TOKEN_VAZIO

complete join with zero matched observations
  -> NO_OVERLAP

complete physical join + preregistered analysis contract
  -> SYSTEMATICS_DIAGNOSTIC_READY
```

No state in this module authorizes cosmological likelihood or parameter mutation.

## Why this helps RLL

The useful role of the Fisica repository is now sharply constrained to three defensible functions:

1. **environmental null model** — test whether local electromagnetic, acoustic, stress or magnetic conditions coincide with an observational residual;
2. **instrumental veto/control** — identify acquisition windows that deserve independent review when synchronized environmental anomalies exist;
3. **negative evidence preservation** — retain null and no-overlap results instead of selecting only apparent correlations.

For Pantheon/SN, BAO, CMB or other compiled cosmology datasets, this bridge cannot operate until the corresponding observation-level acquisition metadata exists and is hash-pinned. A publication-level dataset identifier alone is insufficient.

## Next data-bearing step

The next valid input is not another theory document. It is an observation-index artifact for one RLL dataset containing, where legitimately available:

```text
observation_id
acquisition timestamp/time basis
observatory or instrument/site identifier
source dataset row/key
provenance hash
```

followed by a real `physical_measurement` receipt from Fisica covering an overlapping acquisition window.

Until both sides exist:

```text
classification = TOKEN_VAZIO or NO_OVERLAP
claim_allowed = false
```

## Boundary

This bridge improves falsifiability and systematics control. It does not increase the evidential support for RLL by itself and does not reinterpret terrestrial geophysics as a cosmological signal.
