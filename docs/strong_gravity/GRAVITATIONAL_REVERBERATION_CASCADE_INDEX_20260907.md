# Gravitational Reverberation + Cascade Index — 2026-09-07

Authority: `instituto-Rafael/relativity-living-light`  
Base route: `work -> rll/lab -> rll/integration -> rll/release -> main`  
Claim allowed: `false`

## Layer A — reverberation

```text
data/pipelines/strong_gravity/gravitational_reverberation_response.py
data/contracts/gravitational_reverberation_response.v1.json
data/examples/strong_gravity/gravitational_reverberation.example.json
scripts/strong_gravity/run_gravitational_reverberation.py
tests/strong_gravity/test_gravitational_reverberation_response.py
docs/strong_gravity/GRAVITATIONAL_REVERBERATION_RESPONSE.md
```

Core:

\[
h_{obs}=h_{direct}+h_{ringdown}+h_{tail}+h_{memory}
\]

with retarded causality `t_ret=t_obs-d/v_prop`, `0<v_prop<=c`.

Focused tests written: **6**.

## Layer B — threshold cascade

```text
data/pipelines/strong_gravity/gravitational_cascade_network.py
data/contracts/gravitational_cascade_trigger_network.v1.json
data/examples/strong_gravity/gravitational_cascade_mousetrap.example.json
scripts/strong_gravity/run_gravitational_cascade.py
tests/strong_gravity/test_gravitational_cascade_network.py
docs/strong_gravity/GRAVITATIONAL_CASCADE_TRIGGER_NETWORK.md
```

Core:

\[
Q_i(t)=\sum_kE_{k\to i}(t),\qquad Q_i\ge\Theta_i
\]

\[
E_{release,i}=\eta_iE_{reservoir,i}
\]

\[
E_{ij}=E_{release,i}K_{ij}A(d_{ij}),\qquad \sum_jK_{ij}\le1
\]

\[
\Delta t_{ij}=d_{ij}/v_{prop},\qquad v_{prop}\le c.
\]

Focused tests written: **7**.

## Existing avalanche distinction

`session_multiscale_avalanche.py` remains the owner of its existing Townsend/plasma avalanche and finite candidate-permutation logic. This new cascade layer is network-level threshold propagation between pre-loaded reservoirs and does not replace it.

## Composition boundary

Formal target:

\[
\mathcal C_g=\mathcal N_{threshold}\circ\mathcal R_g.
\]

Current state:

```text
strain/response -> Joule trigger map = TOKEN_VAZIO
composition executed                 = false
cosmic-web causal cascade proven     = false
astrophysical source fit             = false
numerical relativity solution        = false
RLL cosmology modification           = false
claim_allowed                        = false
```

This prevents an arbitrary gain from turning a gravitational-wave-like signal amplitude into cascade energy.

## Physical promotion ladder

```text
P1 executable reference layers
-> P2 concrete astrophysical node/source class
-> P3 source-derived GR/NR/MHD coupling and bounded reservoirs
-> P4 distinguishable observable + null models
-> P5 injection/recovery and real-data comparison
-> P6 independent replication
```

Current state: `P1`; `P2..P6 = TOKEN_VAZIO`.
