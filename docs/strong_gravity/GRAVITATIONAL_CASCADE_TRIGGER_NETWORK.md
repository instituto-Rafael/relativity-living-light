# Gravitational Cascade Trigger Network — hypothesis laboratory

Status: `HYPOTHESIS_LAB_IMPLEMENTED_CLAIM_BLOCKED`  
Claim allowed: `false`

## 1. Purpose

This module turns the domino / billiard-ball / mousetrap-with-ping-pong-balls intuition into a finite-speed threshold-network experiment.

The central question is not whether the whole Universe *does* undergo a gravitational avalanche. The computable question is narrower:

> Under what network density, local stored-energy, coupling, attenuation and threshold conditions can one finite perturbation unlock a multi-generation cascade without violating causality or energy bookkeeping?

This is an implementation of a hypothesis laboratory, not a physical confirmation.

## 2. The important energy distinction

The mousetrap analogy contains the conservation rule naturally.

A ping-pong ball that hits the first armed trap does not provide the energy carried by every later moving trap. Each trap already stores elastic potential energy.

The model therefore separates:

\[
E_{\rm seed}
\neq
E_{\rm cascade,total}.
\]

Instead:

\[
E_{\rm available}
=
E_{\rm seed}
+
\sum_i E_{\rm reservoir,i}.
\]

A node activates when accumulated incoming perturbation crosses its threshold:

\[
Q_i(t)=\sum_k E_{k\rightarrow i}(t),
\qquad
Q_i\ge\Theta_i.
\]

After activation it releases only a bounded fraction of energy that was already stored locally:

\[
E_{\rm release,i}=\eta_i E_{\rm reservoir,i},
\qquad 0\le\eta_i\le1.
\]

The released energy is distributed among outgoing edges; an implementation must not duplicate one local release into several full-strength copies.

## 3. Propagation and attenuation

Every edge has a distance, coupling and causal delay:

\[
\Delta t_{ij}=\frac{d_{ij}}{v_{\rm prop}},
\qquad
0<v_{\rm prop}\le c.
\]

The laboratory attenuation is:

\[
A(d)=\frac{1}{1+(d/d_0)^\alpha}.
\]

and a transmitted pulse is:

\[
E_{ij}
=
E_{\rm release,i}K_{ij}A(d_{ij}).
\]

For energy bookkeeping:

\[
0\le K_{ij}\le1,
\qquad
\sum_j K_{ij}\le1.
\]

`alpha=2` provides an inverse-square-like far-field envelope, but this function is an effective network kernel. It is **not** declared to be a universal gravitational-wave or Newtonian field law.

## 4. Three regimes

### Subcritical

The seed activates one or a few nodes, but transmitted pulses remain below neighbouring thresholds.

\[
S\sim O(1).
\]

### Near critical

Several nodes are close to instability and the branching pattern becomes sensitive to topology, timing, reservoir distribution and small perturbations.

### Supercritical network realization

A large fraction of the finite graph activates:

\[
S/N\rightarrow 1.
\]

This is called an `avalanche` only as a property of the implemented network realization. It is not automatically a claim about the cosmic web.

## 5. Cosmic-web translation

A possible coarse-grained mapping is:

```text
node  -> halo / stellar system / compact-object environment / filament junction
edge  -> candidate causal coupling channel
threshold -> source-specific instability threshold
reservoir -> bounded local gravitational / rotational / magnetic / thermal reservoir
pulse -> perturbation that can reach another node
```

The visual similarity between a cosmic-web illustration and a neural graph is topological only. Similar appearance does not establish the same dynamics.

Likewise, gravitational attraction does not mean that a remote event instantaneously pushes or releases all matter everywhere. Any physical candidate must identify the actual carrier and respect its causal propagation.

## 6. Relation to the RLL reverberation layer

The previous strong-gravity expansion introduced a response decomposition of the form:

\[
h_{\rm obs}
=
h_{\rm direct}
+h_{\rm ring}
+h_{\rm tail}
+h_{\rm memory}.
\]

The cascade network adds a second axis:

\[
\text{one local response}
\rightarrow
\text{possible threshold crossing in another prepared subsystem}
\rightarrow
\text{new local response}.
\]

Therefore a future source-specific model can compose:

\[
\boxed{
\mathcal C_g
=
\mathcal N_{\rm threshold}
\circ
\mathcal R_g
}
\]

where `R_g` is the local gravitational response operator and `N_threshold` is the network activation operator.

The composition remains `TOKEN_VAZIO` physically until the coupling is derived for a concrete astrophysical class.

## 7. Why the nuclear-fission analogy is limited

The useful invariant is:

```text
one event -> multiple possible descendants -> descendants can trigger later descendants
```

The disallowed inference is:

```text
gravity has the same microscopic multiplication mechanism as neutron-induced fission
```

Nuclear fission has a known microscopic reaction and a measurable neutron multiplication factor. This network currently has only a generic threshold law. A physical RLL cascade would need its own derived microscopic or macroscopic trigger mechanism.

## 8. Measurements emitted by the implementation

- `avalanche_size`;
- `active_fraction`;
- `max_depth`;
- `duration_s`;
- `total_seed_j`;
- `total_released_j`;
- activation times and accumulated triggers;
- `branching_potential` as a first-generation diagnostic.

`branching_potential > 1` is not sufficient evidence of a physical avalanche.

## 9. Null and adversarial tests required before physical promotion

1. Randomize event times while preserving rates.
2. Randomize network topology while preserving degree distribution.
3. Remove the hypothesized coupling channel.
4. Compare against independent coincident-event baselines.
5. Vary attenuation and distance uncertainty.
6. Vary threshold distributions.
7. Preserve the same total reservoir while redistributing it spatially.
8. Check whether inferred propagation exceeds `c`.
9. Check whether outgoing energy exceeds the local release.
10. Require an observable that distinguishes cascade causation from common-cause correlation.

## 10. Execution

```bash
python3 scripts/strong_gravity/run_gravitational_cascade.py \
  data/examples/strong_gravity/gravitational_cascade_mousetrap.example.json
```

The CLI emits a deterministic JSON receipt with an input SHA-256 and `claim_allowed=false`.

## 11. Promotion ladder

```text
P0 analogy
-> P1 threshold network implemented
-> P2 concrete astrophysical node class
-> P3 GR/MHD coupling derived
-> P4 observable + null models
-> P5 real-data test
-> P6 independent replication
```

Current state:

```text
P1 = implemented
P2..P6 = TOKEN_VAZIO
claim_allowed = false
```

## R3

`F_ok`: finite-speed cascade, attenuation, thresholds, local reservoirs and receipts are implemented.  
`F_gap`: no source-specific astrophysical coupling has yet been derived.  
`F_next`: bind one concrete source class to threshold, reservoir, coupling and falsifiable observable.
