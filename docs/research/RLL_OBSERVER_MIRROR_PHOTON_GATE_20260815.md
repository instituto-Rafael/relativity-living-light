# RLL Observer / Mirror / Photon Gate — 2026-08-15

Status: `GOVERNED_PROXY_GATE`

Claim boundary:

- `claim_allowed_dark_energy_photon_literal=false`
- `claim_allowed_dark_matter_unseen_matter_default=false`

This note cross-links the RLL stellar-light ledger with the session's observer/mirror/camera intuition.

## 1. Repository cross-check

A direct search in `instituto-Rafael/relativity-living-light` did not surface an existing named implementation for:

- `photon mirror observer light redshift dark energy dark matter Olbers`
- `energia escura matéria escura fóton luz observador espelho`

Therefore this gate is added as a new governed layer, cross-linked to the already-added stellar-light ledger and homeostatic-field gate, rather than as a replacement of an existing named module.

## 2. Session intuition preserved

A photon emitted by a star is not identical to the final registered image.

Between emission and measurement there may be:

- propagation delay;
- geometric dilution;
- redshift;
- absorption/scattering;
- mirror/reflection transformation;
- camera gain/sensor registration;
- observer-frame interpretation.

In RLL language:

```math
I_{measured}
=
\mathcal{O}_{frame}
\left[
\mathcal{R}_{mirror}
\left(\gamma_{source}\right)
\right]
```

Where:

- `gamma_source` is the emitted photon/light ledger component;
- `R_mirror` is reflection/path/frame transformation;
- `O_frame` is camera/observer registration;
- `I_measured` is the observed image or signal.

## 3. Difference between camera and external observer

The camera is a local registration endpoint. The external observer is a frame that interprets the same event from another geometry.

```math
I_{camera} \neq I_{external}
```

This is not a contradiction. It means measurement depends on path, frame, and registration channel.

## 4. Stellar ledger connection

This gate extends `RLL_STELLAR_LIGHT_LEDGER_OLBERS_BOUNDARY_20260815.md`.

The previous ledger states:

```math
observed\ light \neq emitted\ light\ at\ source\ time
```

The present gate adds:

```math
observed\ image \neq untransformed\ photon\ ledger
```

Therefore:

```math
L_{observed}
=
T_{observer}\circ T_{mirror}\circ T_{space}\left(L_{emitted}\right)
```

The relevant accounting is not only source luminosity; it is source luminosity after cosmological and local optical transformations.

## 5. Gate equation

The proxy script uses:

```math
F_{received}
=
\frac{L}{4\pi d^2(1+z)^2}
```

and then applies a mirror/camera/frame transform:

```math
I_{measured}=F_{received}\cdot T_{mirror}\cdot G_{camera}
```

The gate checks whether measured/observed light is path-transformed and separated from emitted source luminosity, not whether photons literally are dark energy.

## 6. Classification

The script reports:

- `FORTE_PROXY_ONLY` if the synthetic or supplied ledger shows strong observation/source separation and nonzero registered signal;
- `NEUTRO_ALTO_PROXY_ONLY` for partial but coherent separation;
- `FRACO_PROXY_ONLY` when the ledger does not support a path-dependent observation channel.

## 7. RLL cross-link stack

```math
stellar\ source\ ledger
\to
space/redshift/dilution
\to
mirror/camera/observer\ transform
\to
\Phi_\gamma(t)_{usable}
\to
homeostatic\ field\ gate
```

This creates a controlled route from the user's photon/reflection intuition into the RLL buffer model.

## 8. Invariants

- `observed_light != emitted_light_at_source_time`
- `observed_image != untransformed_photon_ledger`
- `photon != dark_energy_literal`
- `unseen_source_matter != dark_matter_by_default`
- `camera_register != external_observer_frame`
- `TOKEN_VAZIO` is mandatory for unobserved source/remnant paths

## 9. Next falsification gates

1. Replace synthetic rows with real optical/astronomical ledger rows.
2. Track emitted luminosity, received flux, redshift, distance, absorption and instrumental registration separately.
3. Compare observer/camera/mirror transformations against a no-transform baseline.
4. Only then connect residuals to RLL dark-matter/dark-energy observables.
