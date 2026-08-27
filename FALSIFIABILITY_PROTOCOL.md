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

## 7) Mpemba-horizon / strong-gravity specialization

Governed by `docs/RLL_MPEMBA_HORIZON_ATLAS.md`, implemented by `data/pipelines/strong_gravity/mpemba_horizon_falsifier.py`, evidenced by `data/contracts/mpemba_horizon_falsifier.v1.json`, and regression-tested by `tests/strong_gravity/test_mpemba_horizon_falsifier.py` under the repository's canonical Python-test CI.

Additional invariants:
- Schwarzschild/Hawking/Bekenstein identities are analytic/semi-classical results, not direct astrophysical Hawking-radiation observations.
- Static Schwarzschild/Tolman quantities must not be silently re-labelled as freely falling local measurements.
- Any relativistic-jet route requiring causal transport of matter or information from inside an event horizon to infinity is rejected.
- EHT synchrotron, polarization and plasma observables must not be promoted to Hawking thermometry.
- Holographic, Unruh or other quantum Mpemba results are theory precedents and must not be promoted to an astrophysical black-hole Mpemba detection.
- Internal RAFAELIA/Exacordex entropy analogies remain symbolic hypotheses until an explicit units/dimensions map, Bekenstein-Hawking area-law recovery, Schwarzschild first-law recovery, observer/covariance treatment and independent prediction close the bridge.
- Post-hoc unit adjustment or numerical/constant matching cannot close a physical-equivalence gate.
- Symbolic cyclic-time/direct-inverse operators remain `ANALOGY_ONLY` unless a covariant dynamical model produces operational, quantitative predictions that survive GR/cosmological null comparisons.
- A real-data Mpemba claim requires a predeclared state/observable, equilibrium target, distance functional or admissible family, far/near ordering, crossing rule, first-passage threshold, covariance/uncertainty treatment, null competitors, hold-out/look-elsewhere controls and independent reproduction.
- Synthetic crossings demonstrate only the detector/gate logic; they do not constitute natural evidence.
- Missing real trajectories, file-level checksums, covariance-aware inference or independent reproduction keeps the astrophysical claim at `TOKEN_VAZIO`.
- Failed claim fragments are quarantined from descendants while provenance remains append-only.
- A local strong-gravity anomaly does not imply an RLL cosmological-background modification or an RLL-over-ΛCDM preference.
- New independent falsifiers are appended to the registry; no finite list is represented as all logically possible falsifiers.
