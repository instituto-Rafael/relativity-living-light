# Gravitational Cascade Trigger Network

Status: `HYPOTHESIS_LAB_IMPLEMENTED_CLAIM_BLOCKED`  
Claim allowed: `false`

## Purpose

Turn the domino / billiard / mousetrap-with-ping-pong-balls intuition into a finite-speed threshold-network experiment. The computable question is: under what topology, reservoir, threshold, coupling and attenuation conditions can one finite perturbation unlock a multi-generation cascade without violating causality or energy bookkeeping?

## Energy boundary

The seed does not supply all later energy. Each activated node contains a pre-existing reservoir:

\[
E_{available}=E_{seed}+\sum_i E_{reservoir,i}.
\]

\[
Q_i(t)=\sum_k E_{k\to i}(t),\qquad Q_i\ge\Theta_i,
\]

\[
E_{release,i}=\eta_iE_{reservoir,i},\quad 0\le\eta_i\le1.
\]

Transmission is bounded:

\[
E_{ij}=E_{release,i}K_{ij}A(d_{ij}),\qquad \sum_jK_{ij}\le1.
\]

The effective laboratory attenuation is:

\[
A(d)=\frac{1}{1+(d/d_0)^\alpha}.
\]

It is not a universal GR law.

## Causality

\[
\Delta t_{ij}=d_{ij}/v_{prop},\qquad 0<v_{prop}\le c.
\]

## Cosmic-web translation

Possible coarse-grained mapping:

```text
node       -> halo / stellar system / compact-object environment / filament junction
edge       -> candidate causal coupling channel
threshold  -> source-specific instability threshold
reservoir  -> bounded local gravitational/rotational/magnetic/thermal energy
pulse      -> perturbation reaching another node
```

Visual similarity to a neural network or foam is topology only, not evidence of shared dynamics.

## Fission analogy boundary

Useful invariant: `one event -> several possible descendants -> descendants can trigger later descendants`.

Disallowed inference: gravity has the same neutron-multiplication mechanism as nuclear fission.

## Null tests before promotion

1. randomize event times;
2. randomize topology while preserving degree distribution;
3. remove the hypothesized coupling;
4. compare with independent coincident-event baselines;
5. vary attenuation and threshold distributions;
6. preserve total reservoir while redistributing it spatially;
7. reject inferred propagation above `c`;
8. verify outgoing energy never exceeds local release;
9. require an observable separating cascade causation from common-cause correlation.

## Execution

```bash
python3 scripts/strong_gravity/run_gravitational_cascade.py data/examples/strong_gravity/gravitational_cascade_mousetrap.example.json
```

Current state: implementation/test layer exists; concrete astrophysical coupling and observational validation remain `TOKEN_VAZIO`.
