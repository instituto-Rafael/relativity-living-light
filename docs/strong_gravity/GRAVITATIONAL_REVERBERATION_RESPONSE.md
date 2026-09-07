# Gravitational Reverberation Response — bounded signal reference

Status: `SIGNAL_REFERENCE_IMPLEMENTED_CLAIM_BLOCKED`  
Claim allowed: `false`

## 1. Purpose

This module formalizes the previous session expansion:

```text
impulsive event
-> direct disturbance
-> damped modal response / ringdown
-> long tail / backscatter-like reference
-> persistent memory offset
```

The implementation is intentionally a **signal-level response operator**. It is not a solution of the Einstein equations, not numerical relativity and not an astrophysical waveform fit.

## 2. Decomposition

The implemented reference is:

\[
h_{\rm obs}(t)
=
h_{\rm direct}(t)
+h_{\rm ring}(t)
+h_{\rm tail}(t)
+h_{\rm memory}(t).
\]

### Direct pulse

\[
h_{\rm direct}
=A_d\exp\left[-\frac12\left(\frac{\Delta t}{\sigma_d}\right)^2\right].
\]

### Damped modes

\[
h_{\rm ring}
=\sum_n
A_n e^{-\Delta t/\tau_n}
\cos(2\pi f_n\Delta t+\phi_n).
\]

For the chosen exponential convention the diagnostic quality factor is:

\[
Q_n=\pi f_n\tau_n.
\]

The code does **not** derive `f_n` or `tau_n` from mass/spin. Those quantities must come from an explicit source model or validated waveform/NR calculation.

### Tail reference

\[
h_{\rm tail}
=A_t\left(1+\frac{\Delta t}{\tau_t}\right)^{-p}.
\]

This is a bounded power-law tail reference. It is not automatically a specific Price-tail derivation and does not imply an exotic gravitational echo.

### Memory reference

\[
h_{\rm memory}
=\Delta h\left(1-e^{-\Delta t/\tau_m}\right).
\]

The term approaches a persistent offset and therefore provides an operational representation of the session's "event -> oscillation -> decay -> memory" chain.

## 3. Retarded causality

For an observer a distance `d` from the source:

\[
t_{\rm ret}=t_{\rm obs}-\frac{d}{v_{\rm prop}},
\qquad
0<v_{\rm prop}\le c.
\]

All response components are exactly zero before the retarded event time.

## 4. Connection to the cascade network

The intended composition is:

\[
\boxed{
\mathcal C_g
=
\mathcal N_{\rm threshold}
\circ
\mathcal R_g
}
\]

where:

- `R_g` = this reverberation response operator;
- `N_threshold` = `gravitational_cascade_network.py`.

However, the composition is **not numerically wired** yet.

Reason:

\[
\boxed{
\text{strain-like response amplitude}
\not\equiv
\text{Joule-valued trigger energy}
}
\]

A universal conversion factor would be fabricated physics. Therefore:

```text
strain_to_trigger_energy = TOKEN_VAZIO
```

A future bridge must derive that mapping for a concrete astrophysical source class, detector/interaction geometry and stress-energy model.

## 5. What the signal analogy preserves

The following analogical vocabulary is useful when carefully bounded:

```text
acoustic impulse      -> gravitational disturbance reference
ringing               -> damped modes
reverberation         -> delayed/decaying response and curvature-tail reference
beat                  -> interference of multiple supplied modes
memory after the hit  -> persistent offset
```

The following is not allowed:

```text
vacuum is an acoustic material medium
sound pressure = spacetime pressure
all cosmic structures resonate with the same transfer function
```

## 6. Example execution

```bash
python3 scripts/strong_gravity/run_gravitational_reverberation.py \
  data/examples/strong_gravity/gravitational_reverberation.example.json
```

The example deliberately uses synthetic modal frequencies and amplitudes. It is a deterministic reference for code/testing, not a source fit.

## 7. Required promotion path

```text
synthetic response
-> source class selected
-> mass/spin/geometry declared
-> GR/NR mode spectrum supplied
-> propagation/lensing model supplied
-> detector response supplied
-> injection/recovery
-> real-data comparison
-> independent replication
```

Until that route is completed:

```text
new gravitational physics claim = blocked
astrophysical validation = false
RLL cosmology modification = false
```

## R3

`F_ok`: direct + ringdown + tail + memory and retarded causality are executable.  
`F_gap`: source-derived amplitudes/modes and strain-to-cascade-energy mapping are absent.  
`F_next`: bind one concrete source class, then test the response against a known GR baseline before any RLL-specific residual is introduced.
