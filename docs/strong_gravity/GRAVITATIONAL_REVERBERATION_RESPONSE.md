# Gravitational Reverberation Response

Status: `SIGNAL_REFERENCE_IMPLEMENTED_CLAIM_BLOCKED`  
Claim allowed: `false`

## Response

\[
h_{obs}=h_{direct}+h_{ring}+h_{tail}+h_{memory}.
\]

Direct causal reference:
\[
h_{direct}=A_d\exp[-\tfrac12(\Delta t/\sigma_d)^2].
\]

Damped modes:
\[
h_{ring}=\sum_n A_ne^{-\Delta t/\tau_n}\cos(2\pi f_n\Delta t+\phi_n),\qquad Q_n=\pi f_n\tau_n.
\]

Tail reference:
\[
h_{tail}=A_t(1+\Delta t/\tau_t)^{-p}.
\]

Persistent memory reference:
\[
h_{memory}=\Delta h(1-e^{-\Delta t/\tau_m}).
\]

Retarded causality:
\[
t_{ret}=t_{obs}-d/v_{prop},\qquad 0<v_{prop}\le c.
\]

All components are zero before the retarded event time.

## Cascade boundary

The intended future composition is:
\[
\mathcal C_g=\mathcal N_{threshold}\circ\mathcal R_g.
\]

It is deliberately not wired numerically because:

```text
strain-like response amplitude != Joule-valued trigger energy
strain_to_trigger_energy = TOKEN_VAZIO
```

A universal gain would fabricate physics. A source-specific GR/NR/MHD/stress-energy bridge is required.

## Boundaries

- not an Einstein-equation solver;
- not numerical relativity;
- supplied modes are not automatically black-hole QNMs;
- power-law tail does not imply exotic echoes;
- persistent offset is a signal-level memory representation;
- no RLL cosmology modification is authorized.

## Execution

```bash
python3 scripts/strong_gravity/run_gravitational_reverberation.py data/examples/strong_gravity/gravitational_reverberation.example.json
```

Current state: direct/ringdown/tail/memory + causality implemented; source-derived spectra and strain-to-cascade bridge remain `TOKEN_VAZIO`.
