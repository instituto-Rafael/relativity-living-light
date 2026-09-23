# RLL — Geometry Crosswalk: 251 Expressions × DESI DR2 × Pantheon+ × LCDM × RLL — V1

**Date:** 2026-09-21  
**Author:** RAFAEL MELO REIS  
**State:** \`CROSSWALK_MATERIALIZED / FULL_EXPRESSION_IMPORT_PASS / SCIENTIFIC_CLAIM_BLOCKED\`

## 0. Correction to prior state

Previously the RLL invariant atlas **referenced** the upstream range \`MF-0001..MF-0251\`, but did not contain a verbatim machine-readable record for every MF item.

That gap is now closed by:

\`data/governance/RLL_SESSION_FORMULA_REGISTRY_MF0001_MF0251_V1.json\`

Import check:

\[
\boxed{251/251\ \text{IDs imported; 0 missing; 0 duplicates}.}
\]

Test-routing matrix:

\`data/governance/RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json\`

Current routing counts:

- 144 deterministic numeric/symbolic;
- 16 structural assertions;
- 33 hypothesis/model falsifiers;
- 11 boundary guards;
- 47 provenance/context-only.

Cosmology routing:

- 130 geometry-diagnostic candidates;
- 44 negative-control/no-cosmology items;
- 5 domain-separation controls;
- 72 no-direct-binding items.

Every expression is therefore inside the RLL test surface, but **not every expression is a numeric equation**.

## 1. Cosmological geometry layer

For a background model with

\[
E(z)=\frac{H(z)}{H_0},
\]

define the radial Hubble distance

\[
\boxed{D_H(z)=\frac{c}{H(z)}}.
\]

Dimensionless radial comoving coordinate:

\[
\chi(z)=\int_0^z\frac{dz'}{E(z')}.
\]

For flat FLRW:

\[
\boxed{D_M(z)=\frac{c}{H_0}\chi(z)}.
\]

Then

\[
\boxed{D_A(z)=\frac{D_M(z)}{1+z}},
\qquad
\boxed{D_L(z)=(1+z)D_M(z)}.
\]

Distance duality:

\[
\boxed{D_L=(1+z)^2D_A}.
\]

For flat FLRW, the differential geometry also gives

\[
\boxed{\frac{dD_M}{dz}=D_H}.
\]

This identity is a direct candidate for model-space geometric testing of LCDM and RLL.

## 2. DESI DR2 BAO geometry

The committed DESI DR2 primary vector contains 13 observables:

- one isotropic \(D_V/r_d\);
- six anisotropic pairs \(D_M/r_d,\ D_H/r_d\).

For an anisotropic pair define the Alcock-Paczynski distance ratio

\[
\boxed{
F_{\rm AP}(z)=\frac{D_M}{D_H}=\frac{D_MH}{c}.
}
\]

Because \(r_d\) cancels,

\[
F_{\rm AP}
=
\frac{D_M/r_d}{D_H/r_d}.
\]

For the isotropic BAO distance,

\[
\boxed{
\frac{D_V}{r_d}
=
\left[
z
\left(\frac{D_H}{r_d}\right)
\left(\frac{D_M}{r_d}\right)^2
\right]^{1/3}.
}
\]

This is directly geometric and dimensionless.

### Current observed DESI pair geometry

Using the committed 13-vector and covariance blocks, the six observed ratios are approximately:

| tracer | z | \(F_{\rm AP}=D_M/D_H\) | propagated \(\sigma\) |
|---|---:|---:|---:|
| LRG1 | 0.510 | 0.6215067 | 0.0170031 |
| LRG2 | 0.706 | 0.8918530 | 0.0205796 |
| LRG3+ELG1 | 0.934 | 1.2230599 | 0.0184948 |
| ELG2 | 1.321 | 1.9470231 | 0.0445767 |
| QSO | 1.484 | 2.3805883 | 0.1354965 |
| Lyα | 2.330 | 4.5166821 | 0.0968626 |

These are observational geometry diagnostics. They are **not** circle/ellipse eccentricities.

## 3. Pantheon+ geometry

Pantheon+ constrains luminosity-distance evolution through supernova magnitudes.

Geometric model quantity:

\[
D_L(z)=(1+z)D_M(z)
\]

under the declared FLRW background.

Distance modulus:

\[
\boxed{
\mu(z)=5\log_{10}\left(\frac{D_L(z)}{\mathrm{Mpc}}\right)+25
}
\]

before the experiment-specific absolute-magnitude/calibration nuisance treatment.

The repository's G4 route uses the official Pantheon+SH0ES catalog, full STAT+SYS covariance when materialized, and a profiled \(M_B\).

The correct comparison is therefore:

\[
\Delta\mu(z)
=
\mu_{\rm RLL}(z)-\mu_{\Lambda{\rm CDM}}(z),
\]

evaluated with the same selection and covariance.

## 4. LCDM vs RLL movement with redshift

The word "movement" is represented here by evolution along \(z\), not literal object motion.

For each model \(M\), define the geometry vector

\[
G_M(z)=
\left(
E_M(z),
\frac{D_H^M(z)}{r_d},
\frac{D_M^M(z)}{r_d},
D_A^M(z),
D_L^M(z),
\mu_M(z)
\right).
\]

Then cross-model residual geometry is

\[
\Delta G(z)=G_{\rm RLL}(z)-G_{\Lambda{\rm CDM}}(z).
\]

The null-limit gate is mandatory:

\[
\boxed{
\Omega_{s0}=0
\Longrightarrow
G_{\rm RLL}(z)=G_{\Lambda{\rm CDM}}(z)
}
\]

for common background parameters in the current RLL implementation.

## 5. Geometry-to-cosmology gate for the 251 expressions

An MF expression may enter the observational test only if it passes:

\[
\text{dimension gate}
\land
\text{domain gate}
\land
\text{operator gate}
\land
\text{falsifier gate}.
\]

Examples:

- ratios \(r/R\), \(s/(2R)\): usable as dimensionless diagnostic templates;
- affine/projective relations: usable as transformation diagnostics;
- textual Matthew numbers: negative-control only;
- base-7 representation identities: no cosmology binding;
- Bohr shell relations: domain-separation control;
- circle→ellipse geometry: diagnostic analogy only unless a physical mapping is derived;
- nested radius/area/volume products: testable as normalized transform families, not as cosmological laws by default.

## 6. Cone/crown extension

The new exact companion is:

\`docs/invariants/circle_triangle_cone_annulus_v1.md\`.

For the equilateral generator:

\[
r_b=\frac a2,\quad
h=\frac{\sqrt3}{2}a,\quad
\ell=a.
\]

Nested circular crowns:

\[
\frac{\Delta A_k}{\pi R_k^2}
=
\sin^2\frac{\pi}{n_k}.
\]

Nested similar-cone volumes:

\[
\frac{V_m}{V_0}
=
\prod_k\cos^3\frac{\pi}{n_k}.
\]

These add a 3D scale channel to the prior 1D-radius and 2D-area channels.

## 7. Required test stack

The full stack is:

\[
\text{251 MF coverage}
\to
\text{exact/structural tests}
\to
\text{geometry diagnostic gate}
\to
\text{DESI BAO geometry}
\to
\text{Pantheon+ distance geometry}
\to
\text{LCDM/RLL model curves}
\to
\text{covariance-aware residuals}
\to
\text{prior-art/physical claim gate}.
\]

No cross-domain item becomes a physical result merely because a geometric residual is small.

## R3

**F_ok:** all 251 expressions are now physically present in RLL and every one has a typed test route; DESI/Pantheon+/LCDM/RLL geometry is explicitly connected through standard cosmological distance observables.

**F_gap:** per-expression execution of all 251 routes is not complete; Pantheon full-covariance availability remains runtime-dependent; prior-art and physical interpretation remain separate.

**F_next:** execute the 144 deterministic formulas and 16 structural assertions first, then run the 130 geometry candidates through DESI/Pantheon+/LCDM/RLL with covariance-aware null/adversarial controls.
