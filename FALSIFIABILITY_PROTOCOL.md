# FALSIFIABILITY_PROTOCOL

This protocol defines explicit conditions under which Relativity Living Light (RLL) is weakened or rejected, without altering the project's scientific claims.

## 1) Scope
- Applies to claims presented as empirical/model-performance statements.
- Does not invalidate conceptual exploration by itself.

## 2) Pre-registered minimum conditions for a valid real-data claim
A real-data claim is valid only if all are satisfied:
1. Required real datasets are present and checksum-verified.
2. Commands and parameters are reproducibly specified.
3. Outputs include machine-readable metrics.
4. Comparison baseline (ΛCDM) is run on equivalent data and preprocessing.

## 3) Weakening conditions (claim must be downgraded)
Any of the following weakens strong model-preference claims to exploratory status:
- Missing or unverified required input files.
- Partial-real pipeline used as if full-real evidence.
- Non-reproducible command path or undocumented manual intervention.
- Metric reporting without uncertainty/context.

## 4) Rejection conditions (claim must be rejected)
Reject a specific empirical claim if any condition holds:
- Reproducible reruns fail to recover reported metrics within declared tolerance.
- Data leakage, target leakage, or post-hoc tuning invalidates comparison fairness.
- ΛCDM baseline is absent, incompatible, or measured under different protocol.
- Statistical evidence reverses the claimed direction (e.g., RLL no longer preferred under declared metric set).

## 5) Explicit prohibition
- Do **not** state that RLL outperforms/beats ΛCDM unless real-data metrics in this repository support that statement under reproducible conditions.

## 6) Recommended reporting template
- Claim category: conceptual / mathematical / synthetic / partial-real / real-validated.
- Dataset manifest + SHA256.
- Exact command(s).
- Metric table with uncertainty.
- Pass/fail against falsifiability criteria above.

## 7) Geomagnetic pole-dynamics specialization

The bounded geomagnetic adapter is governed by `docs/RLL_GEOMAGNETIC_POLE_DYNAMICS_ATLAS.md`, implemented by `data/pipelines/geomagnetism/pole_dynamics_gate.py`, and sourced by `data/contracts/geomagnetic_pole_dynamics.v1.json`.

Additional invariants:
- The magnetic dip pole is a field-defined zero/minimum of horizontal magnetic field, not a material object following an orbital trajectory.
- WMM/IGRF/CHAOS coefficients must be versioned and checksum-bound before any result is called real-data evidence.
- The Canada/Siberia flux-lobe interpretation requires a source-traced field decomposition; a generic two-source sensitivity calculation is not evidence that a specific lobe caused a measured displacement.
- A frozen-flux residual is a test of an advection-only model and must not be uniquely labelled magnetic diffusion without independent separation of model error, unresolved flow and external contamination.
- The CHAOS-8 `m=13`, approximately `200 km/yr` to `T≈8.42 yr` derivation is a kinematic consistency calculation; overlap with an independently reported 8–9 year acceleration-period peak does not establish common modal identity.
- `sqrt(3)/2` is pre-registered and must not be fitted to geomagnetic observations. The tested scalar observable must be declared before evaluating the ratio residual.
- A golden-ratio/quarter-turn spiral test requires a pre-registered projection center and angle definition; otherwise it remains disabled.
- Post-hoc choice among step length, curvature, osculating radius, projection center, smoothing window or epoch to maximize a RAFAELIA match invalidates the match.
- Synthetic mechanics validate implementation only. Missing official coefficients, hashes, uncertainty-aware trajectory outputs or independent reproduction remain `TOKEN_VAZIO`.
- A local geomagnetic pattern or geometric match does not imply an RLL cosmological-background modification or an RLL-over-ΛCDM preference.