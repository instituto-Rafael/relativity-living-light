# Receipt — MF160 formal execution + MF130 cosmology geometry gate V1

**Date:** 2026-09-21  
**Author:** RAFAEL MELO REIS  
**State:** \`EXECUTION_PARTIAL_STRONG / NEGATIVE_RESULT_PRESERVED / CLAIM_BLOCKED\`

## 1. MF160 formal execution

Verifier:
\`tools/verify_mf160_formal_expressions.py\`

Test:
\`tests/test_mf160_formal_expressions.py\`

Result:
\`results/MF160_FORMAL_EXECUTION_V1.json\`

Observed isolated execution:

\`\`\`text
target=160
executed=160
PASS=155
PASS_CONDITIONAL=2
TOKEN_VAZIO_SEMANTICS=2
FAIL=1
\`\`\`

### Contradiction preserved

\`MF-0219\`

Written:

\[
\text{núcleo}\subset\text{coroa}\subset\text{envoltória circular}.
\]

Under the standard annulus/crown definition, the inner core is **not** a subset of the crown.

State:

\`FAIL\`.

Safe repair candidate:

\[
\text{núcleo}\subset\text{envoltória},
\qquad
\text{coroa}\subset\text{envoltória},
\]

with the exact core/crown intersection depending on whether the inner boundary is open or closed.

The original MF record remains append-only.

### TOKEN_VAZIO preserved

- \`MF-0130\`: \`m=R\` — symbol \`m\` undefined.
- \`MF-0191\`: right-hand von Neumann nesting is formal, but the leading \`indeterminado→\` map is undefined.

### Conditional passes

- \`MF-0129\`: \`c=2R\` only for the diameter chord, \(\theta=\pi\).
- \`MF-0221\`: \(R_1<R_2<\cdots\) under the outward \(\sec(\pi/n)\) route with \(n>2\).

## 2. Polygon-limit closure

\`MF-0089\` and \`MF-0209\` were separately tested under the declared regular-inscribed-polygon route:

\[
n_k=4\cdot2^k,
\]

\[
R\left[1-\cos\left(\frac{\pi}{n_k}\right)\right]\to0,
\]

\[
2n_kR\sin\left(\frac{\pi}{n_k}\right)\to2\pi R.
\]

Both are now:

\`PASS_CONDITIONAL\`.

Result:
\`results/MF0089_MF0209_POLYGON_LIMIT_V1.json\`.

## 3. MF130 cosmology domain gate

All 130 previously selected geometry candidates now have a domain-gate state:

\`\`\`text
PASS_DOMAIN_GATE=125
PASS_DOMAIN_GATE_CONDITIONAL=3
TOKEN_VAZIO_SEMANTICS=1
BLOCKED_UPSTREAM_FAIL=1
total=130
\`\`\`

Artifact:

\`results/RLL_MF130_COSMO_GEOMETRY_DOMAIN_GATE_V2.json\`

No MF-specific empirical mapping is allowed to be chosen after seeing residuals.

## 4. DESI DR2 geometry execution

Committed DESI DR2 geometry was materialized through:

\[
F_{\rm AP}
=
\frac{D_M}{D_H}
=
\frac{D_M/r_d}{D_H/r_d}.
\]

The six observed anisotropic pairs were converted into dimensionless geometry.

A second artifact independently recomputed the G4 DESI predictions at the recorded best fits:

\`results/RLL_G4_DESI_GEOMETRY_LCDM_RLL_REPRODUCTION_V1.json\`.

Recomputed DESI chi-square:

\`\`\`text
LCDM = 11.770259180500712
RLL  = 11.77025905554635
\`\`\`

Recorded G4 values:

\`\`\`text
LCDM = 11.770254061852592
RLL  = 11.770253936897157
\`\`\`

The small reproduction difference is attributable to the independent Simpson integration versus the G4 integration-grid/interpolation implementation.

Maximum RLL↔LCDM BAO-prediction difference in the reproduction:

\[
6.54\times10^{-9}
\]

in the dimensionless BAO observable vector.

## 5. LCDM ↔ RLL distance geometry

Using the recorded joint G4 best-fit parameters, the following were recomputed over the selected redshift grid:

\[
E,\ H,\ D_H,\ D_M,\ D_A,\ D_L,\ \mu,\ F_{\rm AP}.
\]

Artifact:

\`results/RLL_G4_DISTANCE_GEOMETRY_LCDM_RLL_V1.json\`.

Maximum relative differences:

\`\`\`text
E      3.50e-10
H      6.66e-10
DH     6.66e-10
DM     5.25e-10
DA     5.25e-10
DL     5.25e-10
F_AP   1.41e-10
max |Δmu| = 1.14e-9 mag
\`\`\`

This is expected because the recorded G4 RLL optimum has

\[
\boxed{\Omega_{s0}=0},
\]

placing the fitted RLL background on its \(\Lambda\)CDM null submanifold.

This is **unfavorable evidence for a distinct RLL background effect in this G4 scope**, not a universal falsification.

## 6. Pantheon+ full-covariance binding

Existing repository evidence:

\`artifacts/science/RLL_G4_PANTHEON_FAIRNESS_RECEIPT_20260819_RUN32286390824.json\`

records:

\`\`\`text
N=1657
full STAT+SYS covariance
RLL Omega_s0=0
Δchi2(RLL-LCDM)=2.27e-13
ΔBIC(RLL-LCDM)=+22.2383
\`\`\`

Thus the Pantheon-only G4 subgate also places RLL on its LCDM null boundary.

## 7. Circle / ellipse / triangle diagnostic embedding of DESI

Artifact:

\`results/RLL_DESI_SYNTHETIC_GEOMETRY_EMBEDDING_V1.json\`

Synthetic dimensionless coordinates:

\[
x=\frac{D_M}{r_d},
\qquad
y=\frac{D_H}{r_d},
\]

\[
\rho=\sqrt{x^2+y^2},
\qquad
\phi=\operatorname{atan2}(x,y),
\]

\[
q=\frac{\min(x,y)}{\max(x,y)},
\qquad
e_{\rm proxy}=\sqrt{1-q^2}.
\]

These provide circle/right-triangle/ellipse coordinates for testing the geometric corpus.

Hard boundary:

\[
\text{synthetic geometric embedding}
\neq
\text{physical Euclidean ellipse/cone in spacetime}.
\]

## 8. CI

Recent formula/index workflows succeeded, while the full Python-test run for the latest commit was cancelled by workflow scheduling/concurrency before execution. Therefore:

\`LOCAL_ISOLATED_EXECUTION != GITHUB_CI_PASS\`.

## μWRITE

\`\`\`text
μID=RLL-MF160-MF130-GEOMETRY-EXEC-20260921-V1
source/ref=MF-0001..MF-0251 + DESI DR2 + Pantheon+ G4 + LCDM/RLL G4
parent=RLL-MF251-COSMO-GEOMETRY-20260921-V1
kind=formal-expression-execution-and-cosmology-geometry-gate
Δsummary=160 individual formal outcomes; one contradiction preserved; two semantic gaps; three conditional geometry items; 130 candidate domain gates; DESI/Pantheon/LCDM/RLL distance-geometry baselines; synthetic DESI geometric embedding
evidence=LOCAL_ISOLATED_EXECUTION + REPO_G4_EVIDENCE + DESI_RECOMPUTATION
gap=GitHub Python CI rerun + per-MF empirical mappings + multiple-testing correction + prior-art + independent replication + physical derivation
next=freeze non-adaptive MF-family mappings, then score only predeclared mappings against covariance-aware DESI/Pantheon geometry
rollback=revert this delta commits/results only; preserve failed/token-vazio history
\`\`\`

## R3

**F_ok:** 160/160 formal-route items now have individual outcomes; 130/130 geometry candidates have domain-gate states; DESI, Pantheon+, LCDM and RLL are bound to explicit distance-geometry evidence.

**F_gap:** formula-specific empirical mappings are not yet frozen; one MF is false under standard semantics and one geometry candidate remains TOKEN_VAZIO; latest full Python CI did not execute to completion.

**F_next:** define the non-adaptive mapping families before looking for matches, apply covariance-aware scoring with multiplicity controls, and preserve the current G4 negative/null-boundary evidence.
