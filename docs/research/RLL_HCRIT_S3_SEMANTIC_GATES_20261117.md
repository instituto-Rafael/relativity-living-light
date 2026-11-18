# RLL Ω · H-CRIT S3 — menor delta reversível de maior cobertura falsificadora

Date 2026-11-17 · `RESEARCH_SCOPED` · `claim_allowed=false` · `PROVIDER_CI=NOT_RUN` · `PHYSICAL_VALIDATION=NOT_RUN`.

## Authority and predecessor

- Producer: `instituto-Rafael/relativity-living-light`; predecessor commit `4bcfbfeb13e9e9d3948a0de85396ae08baaafe7d` from S2.
- Separate research branch `research/rll-hcrit-semantic-gates-s3-20261117` with only additive files. `main`, existing 72 analyses, production likelihood, DESI PR #1232, workflows and scientific results are preserved.
- Source of previous H-CRIT review in Mapa private branch; source evidence is not newly validated here.
- This gate is an identity and semantics **preflight**, not a new physical field theory, GRMHD calculation, TOV solution, phase diagram, nanoporous-gold simulation, or validation of the RLL cosmological model.

## Central oversight corrected

The same **scalar value** can mean different physical conditions. Values calculated from unlabeled matrices, unqualified chemical potentials, wavelength-averaged opacity, magnetostatic scalar pressure, or measured elastic modulus changes may be numerically valid and scientifically wrong when promoted into an unsupported application.

| Contract | Inputs needed | Rejected falsification case | What remains unknown |
| --- | --- | --- | --- |
| H40, G13 | labeled vector, two-axis covariance identity, units, separate source refs and SHA-256 strings | reorder only one axis or swap Lya `DM/DH`; reject non-SPD, duplicate ID and unit mismatch | external primary-source order, independent provenance proof |
| H18, G14 | `p + e- -> n + nu_e`; full rest-energy chemical potentials, composition/EOS | kinetic-only potential passed as rest-mass-inclusive; wrong reaction | reaction rate, neutrino transport, actual onset |
| H63, G14 | separate reaction species, integer stoichiometry, declared baryon and charge, same reference zero | nonconserving reaction or conflicting potential convention | kinetics and true chemical equilibrium |
| H34 / H70, G15 | photon wavelength or neutrino species, energy, EOS, composition and opacity model | wrong carrier or missing frequency/model | full radiative/neutrino transport |
| H45 / H46 / H47, G02-05 | pore geometry, before/after measured E, electrode potential, charge, adsorbate and temperature | no charge/adsorbate controls; stiffness attributed without evidence | causality, 3D morphology, measured response by potential |
| H48, G09-10 | 3-vector `B_T`; Maxwell stress tensor | same scalar pressure used despite different field orientations | spatial gradients and resulting forces |

## Commands to reproduce with data *synthetic* only

```sh
python -m unittest discover -s tests -p test_rll_hcrit_semantic_gates_v1.py -v
```

The previous H01–H72 registry remains a separate source file. It is type-checked by `audit_h01_h72_registry()`; it is not modified by S3. A complete test must execute that audit on the *actual* repository file, not only its 72-record synthetic fixture.

## Deliberate model selection: not first or last

`select_falsifiers(controls, target_risks)` picks the **highest marginal risk coverage per explicit ordinal effort**, tie-breaking by stable ID. This is a deterministic greedy heuristic that can be falsified with a better exact set-cover solution, not a proof of optimality and not a Six-Sigma statistical claim. Risks left uncovered are reported explicitly and do not become zero. A pre-publication negative test caught `false_pass` as uncovered; G16 (evidence-claim lock) was then added, and the 14 declared risk classes are now covered by the control *catalog*. This means designed coverage, not experimental closure.

## Anti-regression and acceptance

- 72 original IDs preserved; no new production parameters; zero I/O side effects in the module.
- 54 tests run locally from exact S3 file bytes with synthetic inputs before publication; CI remains `NOT_RUN`. `SCOPED_LOCAL_TESTS` does not imply physical validation or global `PASS`.
- Reject mismatched units, labels, repeated identity, invalid hash *format*, non-SPD covariance, missing model references, unknown reaction stoichiometry, missing nanogold confounders and fake `claim_allowed`.
- A provided SHA-256 string is **format-validated only**; this module does **not verify** the bytes or authenticity of the cited external source. The external order of DESI covariance is not independently proved.
- Recovery: leave S3 unmerged; append a successor if corrections are needed, preserving source refs and previous receipts. Never force-push, auto-merge, or promote a claim.

## R3

`F_ok=bounded semantic gates + adversarial local tests + manifest; F_gap=external truth data, provider CI, measured EOS/gold/ceramics and causal bridges not run; F_next=run full actual JSON audit, exact-head CI after approval, then one independently reproduced mechanism at a time.`
