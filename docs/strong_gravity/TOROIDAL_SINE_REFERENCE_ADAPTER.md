# Toroidal sine-reference scientific adapter

## Authority

`instituto-Rafael/relativity-living-light`

Canonical governance remains in `rafaelmeloreisnovo/RafGitTools`. This RLL
adapter owns only the scientific formulas, bounded diagnostics, sources,
falsifiers and claim boundaries.

## Scope

The adapter combines two independent structures:

1. toroidal coordinates with inner and outer phases;
2. a bounded sinusoidal reference signal.

\[
\begin{aligned}
x&=(R+r\cos\theta)\cos\phi,\\
y&=(R+r\cos\theta)\sin\phi,\\
z&=r\sin\theta,\\
s(t)&=A\sin(2\pi ft+\phi_0).
\end{aligned}
\]

The geometry is used to test closure and recurrence. The sine is used to test
phase and tracking error. Neither one establishes physical confinement by
itself.

## Diagnostics

\[
\Delta\phi=
\operatorname{atan2}
\left[
\sin(\phi_{\rm obs}-\phi_{\rm ref}),
\cos(\phi_{\rm obs}-\phi_{\rm ref})
\right]
\]

\[
L_\phi=\frac{1+\cos\Delta\phi}{2}
\]

\[
e_{\rm RMS}
=
\sqrt{
\frac{1}{N}
\sum_i
(s_{{\rm obs},i}-s_{{\rm ref},i})^2
}
\]

\[
e_N=e_{\rm RMS}/A
\]

The geometric path metric is:

\[
G_{\rm path}
=
\sum_i
\left(
\frac{\|\mathbf x_i-\mathbf x_{i-1}\|}{R}
\right)^2.
\]

It is dimensionless. It is **not** heat, thermodynamic energy, jet power or
stress-energy.

## Research support

Phase-matched modulation improved the efficiency of a specific neoclassical
magnetic-island stabilization experiment in ASDEX Upgrade. That result
supports source-specific phase control, not universal sine stabilization.

ITER's official system description separates the toroidal field used for
confinement from poloidal fields used for shaping and stability. This prevents
the adapter from treating one toroidal field or one waveform as sufficient.

Modern fast-ion transport and magnetic-surface robustness studies further show
that frequencies, resonances and rotational transform can alter transport or
surface robustness. Frequency matching can therefore stabilize, destabilize or
redistribute transport depending on the governed system.

## Boundaries

```text
pure sine universally stabilizes systems          = false
toroidal coordinates prove a physical torus       = false
tokamak experiment equals black-hole accretion    = false
synthetic phase lock proves plasma confinement    = false
dimensionless path metric is physical energy      = false
MAD or jet confirmed                              = false
Friedmann background modified                     = false
new force discovered                              = false
claim_allowed                                     = false
```

## Files

```text
data/contracts/toroidal_research_cycle_adapter.v1.json
data/pipelines/strong_gravity/toroidal_sine_reference.py
data/results/strong_gravity/toroidal_sine_reference_baseline.json
data/results/strong_gravity/toroidal_sine_reference_validation_receipt.json
tests/strong_gravity/test_toroidal_sine_reference.py
docs/strong_gravity/TOROIDAL_SINE_REFERENCE_ADAPTER.md
```

No new workflow YAML is required. The existing Python test infrastructure is
sufficient for this bounded adapter.
