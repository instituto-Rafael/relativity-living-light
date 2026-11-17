# RLL Ω · H-CRIT H01–H72 — dimensional and falsification kernel (S1)

- Status: **RESEARCH_BRANCH_ONLY**, `claim_allowed=false`, **observational validation=NOT_RUN**, **provider CI=NOT_RUN**, **device/GRMHD/EOS simulations=NOT_RUN**.
- Parent: [Mapa private H-CRIT source review](https://github.com/rafaelmeloreisnovo/Mapa/blob/research/hcrit-literature-20261117-s1/docs/research/HCRIT_PRESSURE_HYDROGEN_DEGENERACY_LITERATURE_20261117_S1.md) (private; do not copy full corpus).
- Existing routes, preserved: `docs/research/RLL_OBVIOUS_NEGLECTED_ATOMS_COSMOS_20261108.md`, `docs/research/RLL_EXTERNAL_EVIDENCE_DOSSIER_2026-09-06__plasma-seawater-materials-hydrogen.md`, `docs/research/RLL_ATLAS_FALSIFICADORES_TRANSVERSAIS_V1_20261108.md`.
- The first **48** H01–H48 are *registrations/typed reconciliations* of the conversation's formula inventory. **H49–H72** add tangible phenomena neglected by the first inventory. Their number is an index, not 72 independent scientific discoveries.

## Actual implementation vs blocked scientific modeling

1. `data/research/rll_hcrit_h01_h72_registry_v1.json`: 72 entries, exact IDs, explicit expression, measurable observable and falsifier, original/overlooked classification, optional scalar binding, and `TOKEN_VAZIO` for real observations.
2. `tools/rll_hcrit_physics_v1.py`: standard-library-only bounded **scalar diagnostics** for **26** kernels: thermal/magnetic/electric/radiation pressures, beta, plasma/cyclotron frequencies, Debye length, adiabatic ratio, classical shocks, Fermi kinetic energy, potential chemical margin, photon/molar energy, capillary pressure, nano area/volume, measured modulus shift, gravity scales, tidal force, optical depth, power, molar area, signed Coulomb force, gravitational redshift and SPD-aware chi². **These calculations do not predict phase diagrams or prove physics**.
3. `tests/test_rll_hcrit_physics_v1.py`: numerical fixtures and adversarial rejection of null/NaN/bool/negative inputs; counterexample for covariance axis inversion; non-SPD rejection; impossible static observer at horizon; fake PASS and data-0 substitution prohibited.

Do **not** claim all H01–H72 have numerical simulations. Each `execution=MODEL_REQUIRED` still needs its own model, data, assumptions, units and producer validation. The runnable kernels are intentionally scoped to scalar formulas and *not* nuclear/stellar EOS, Maxwell FEM, 3D multiphysics, chemistry kinetics, real magnetism or electronics experiments.

## Empirical adversarial boundaries

- **Hydrogen:** high-pressure molecular dissociation, conductivity and full atomization are distinct. Mazzola and Sorella 2015, https://doi.org/10.1103/PhysRevLett.114.105701 . Pressure is not a universal 'hydrogen explosion critical mass'.
- **Nanoporous gold:** dealloying Ag from AuAg produces a ligament/pore geometry; potential-dependent stiffening arises from excess surface electrons and adsorbate chemistry. Do not model electrons as bulk filling the voids. Mameka et al. 2014, https://doi.org/10.1016/j.actamat.2014.04.067 . Measured modulus shift formula alone predicts no field-driven stiffening.
- **Doped ceramics:** Fe doping can alter dielectric/ferromagnetic responses, but impurity phases, oxygen vacancies, strain and thermal drift must be controlled. Staruch et al. 2020, https://doi.org/10.1063/5.0002863 ; low-level Fe contamination, https://doi.org/10.1016/j.jallcom.2015.11.199 .
- **Black holes:** Schwarzschild radius is not a solid shell and a static emitter cannot be extended to or below the horizon. Pressure of proton, pressure of plasma and anisotropic nuclear stress cannot be silently interchanged.
- **Cosmology:** follow existing DESI covariance-binding gate and PR #1232. Permute both axes of C when reordering residual; χ² must be invariant for a consistent permutation. No H(z) or BAO likelihood modified.
- **Dimensional grammar:** Pa=J/m³=N/m²; 1 ym²=1e-48 m²; mol/m² is not pressure; energy J is not power W; angular frequency rad/s is not photon Hz; `TOKEN_VAZIO != 0`.

## Reconstruct and test

```sh
python -m unittest discover -s tests -p 'test_rll_hcrit_physics_v1.py' -v
python tools/rll_hcrit_physics_v1.py --registry data/research/rll_hcrit_h01_h72_registry_v1.json --audit
python tools/rll_hcrit_physics_v1.py --kernel ligament_A_over_V --input-json '{"ligament_d_m":2e-8}'
```

**Prerequisite for promotion:** EOS-specific observational data; appropriate error model and external independent review; exact-head CI; a numerical integration spec for the *producer* RLL module. Until then `claim_allowed=false`. No workflow changed, no PR/merge, no release, no migration, no automations, no Drive cursor advance. Rollback = leave this additive branch unmerged or write corrected successor; never rewrite historical receipts.

## R3
F_ok = scoped registration and bounded numerical functions implemented in branch; F_gap = EOS/chemistry/magnetism/stellar dynamics and observations are NOT_RUN; F_next = independently test source and reconcile first three falsifiers H05, H46, H40 using separate datasets and a reproducible receipt.
