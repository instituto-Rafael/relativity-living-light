# RLL — Invariantes do Tear Geométrico — V1

**Date:** 2026-09-21  
**Author:** RAFAEL MELO REIS  
**State:** \`FORMALIZED / INVARIANT_CANDIDATES_TYPED / PHYSICAL_CLAIM_BLOCKED\`  
**Source corpus:** \`MF-0001..MF-0251\` from \`rafaelmeloreisnovo/Matem-tica-\`  
**Rule:** \`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM\`

## 0. R3 source

\[
\langle
F_{ok}:\ \text{estrutura, relações, transformações, 251 expressões e proveniência};
\quad
F_{gap}:\ \text{determinar quais composições sobrevivem à literatura e aos testes};
\quad
F_{next}:\ \text{procurar os invariantes do tear}
\rangle
\]

RLL consumes this as a **typed invariant-search program**, not as proof of new physics.

## 1. Tear state

Use the geometric state

\[
X=(R,\theta,n,i,\mathcal{I},\mathcal{P})
\]

where:

- \(R\): scale/radius;
- \(\theta\): angular state;
- \(n\): polygon order/discretization;
- \(i\): projection inclination;
- \(\mathcal{I}\): incidence/adjacency structure;
- \(\mathcal{P}\): parallel-direction structure.

Primary operators:

\[
\operatorname{Rot}_\phi,
\qquad
\operatorname{Scale}_\lambda,
\qquad
\operatorname{Proj}_i,
\qquad
\operatorname{HalfStep}_n.
\]

The search target is not “what remains numerically identical under every operator”, because different operators preserve different structures. The correct object is a **typed invariant family**.

## 2. Exact invariants under rotation

For a planar rotation matrix

\[
R_\phi=
\begin{bmatrix}
\cos\phi&-\sin\phi\\
\sin\phi&\cos\phi
\end{bmatrix},
\qquad
R_\phi^TR_\phi=I,
\]

the following are exact:

\[
\|R_\phi x\|=\|x\|,
\]

\[
\|R_\phi x-R_\phi y\|=\|x-y\|,
\]

\[
(R_\phi u)\cdot(R_\phi v)=u\cdot v,
\]

therefore rotation preserves:

- Euclidean distances;
- angles;
- area magnitude;
- collinearity;
- parallelism;
- polygon side equality;
- circumradius/inradius;
- dimensionless ratios formed from lengths.

**State:** \`EXACT_CLASSICAL_INVARIANT\`.

## 3. Exact invariants under uniform scale

For

\[
x\mapsto \lambda x,\qquad \lambda>0,
\]

absolute lengths are not invariant, but normalized ratios are:

\[
\frac{\lambda a}{\lambda b}=\frac ab.
\]

Angles are unchanged. Hence the following survive uniform scale:

\[
\frac{r_n}{R}=\cos\frac{\pi}{n},
\]

\[
\frac{s_n}{2R}=\sin\frac{\pi}{n},
\]

\[
\frac{s_8}{2r_8}=\tan\frac{\pi}{8}=\sqrt2-1,
\]

\[
\frac{h}{a}=\frac{\sqrt3}{2},
\qquad
\frac{h}{R}=\frac32,
\qquad
r:R:h=1:2:3.
\]

Areas transform as \(A\mapsto\lambda^2A\), so area ratios remain invariant.

**State:** \`EXACT_SIMILARITY_INVARIANT\`.

## 4. Half-step combinatorial invariant

For a regular \(n\)-gon with distinct vertex directions,

\[
V(P_n)\cup V(\operatorname{Rot}_{\pi/n}P_n)=V(P_{2n}).
\]

The exact preserved object is not the original polygon but the **interleaving rule**:

\[
\boxed{n\xrightarrow{\pi/n}2n}.
\]

Examples:

\[
3\to6,\qquad4\to8,\qquad5\to10,\qquad7\to14.
\]

Under any centered uniform rescaling, the angular/interleaving structure is unchanged.

**State:** \`EXACT_CONDITIONAL_COMBINATORIAL_INVARIANT\`.

## 5. Nested radial invariant

For the chosen polygon sequence \(\{n_k\}\),

\[
R_{k+1}=R_k\cos\frac{\pi}{n_k},
\]

so

\[
\boxed{
\frac{R_m}{R_0}
=
\prod_{k=0}^{m-1}
\cos\frac{\pi}{n_k}
}.
\]

The absolute radius changes with \(R_0\), but the normalized layer ratio is invariant under global uniform scale.

Area-normalized form:

\[
\boxed{
\frac{A_m}{A_0}
=
\prod_{k=0}^{m-1}
\cos^2\frac{\pi}{n_k}
}.
\]

**State:** \`EXACT_DERIVED_SCALE_INVARIANT\`.

## 6. Projection invariants and non-invariants

Under orthographic projection of an inclined circle,

\[
(x,y)\mapsto(x,\cos i\,y),
\]

a circle of radius \(R\) becomes an ellipse:

\[
a=R,\qquad b=R|\cos i|.
\]

Exact projection relations:

\[
\boxed{\frac ba=|\cos i|},
\]

\[
\boxed{e=|\sin i|},
\]

\[
\boxed{e^2+\left(\frac ba\right)^2=1}.
\]

Under the same non-degenerate affine/orthographic projection:

- collinearity is preserved;
- parallelism is preserved;
- incidence is preserved;
- affine combinations are preserved.

In general, the following are **not** preserved by anisotropic projection:

- Euclidean length;
- Euclidean angle;
- circle shape;
- arbitrary length ratios in different directions.

Therefore projection must not be mixed with similarity invariants.

**State:** \`EXACT_AFFINE_INVARIANT_BOUNDARY\`.

## 7. Concentric-family projection invariant

If several circles share the same center and undergo the same centered linear projection, they become ellipses sharing the projected center.

For radii \(R_j\),

\[
\frac{b_j}{a_j}=|\cos i|
\]

is common to every layer.

Thus the layer family preserves a shared projection anisotropy:

\[
\boxed{
\forall j:\ \frac{b_j}{a_j}=|\cos i|
}.
\]

**State:** \`EXACT_CONDITIONAL_FAMILY_INVARIANT\`.

## 8. Square → two octagons

For two congruent concentric squares of side \(L\) separated by \(\pi/4\):

### intersection octagon

\[
s_{\cap}=L(\sqrt2-1),
\]

\[
r_{\cap}=L/2,
\]

\[
R_{\cap}=\frac{L}{\sqrt{2+\sqrt2}}.
\]

### outer vertex-hull octagon

\[
R_{\mathrm{hull}}=\frac{L}{\sqrt2},
\]

\[
s_{\mathrm{hull}}
=
L\sqrt{\frac{2-\sqrt2}{2}}.
\]

Cross-relation:

\[
\boxed{R_{\cap}=s_{\mathrm{hull}}}.
\]

This equality survives:

- rotations;
- translations;
- uniform positive scale.

It is **not guaranteed** under arbitrary anisotropic projection because the two compared lengths may occupy different directions.

**State:** \`EXACT_MODEL_INVARIANT_UNDER_SIMILARITIES\`.

## 9. Direction-class invariant

The ideal square + \(45^\circ\) square construction has line-direction classes modulo \(180^\circ\):

\[
\boxed{\{0^\circ,45^\circ,90^\circ,135^\circ\}}.
\]

A global rotation adds the same \(\phi\) to all classes, so relative angular differences remain

\[
45^\circ,\ 90^\circ,\ 135^\circ.
\]

Thus the absolute compass orientation is not invariant, but the cyclic difference structure is.

**State:** \`EXACT_RELATIVE_ANGLE_INVARIANT\`.

## 10. Invariant matrix

| Object | Rotation | Uniform scale | Orthographic/affine projection |
|---|---|---|---|
| incidence | PASS | PASS | PASS |
| collinearity | PASS | PASS | PASS |
| parallelism | PASS | PASS | PASS |
| Euclidean angle | PASS | PASS | FAIL generally |
| absolute length | PASS | FAIL | FAIL generally |
| length ratio | PASS | PASS | FAIL generally |
| area magnitude | PASS | FAIL | FAIL generally |
| area ratio under one global scale | PASS | PASS | not general |
| vertex adjacency/order | PASS | PASS | PASS if nondegenerate |
| \(n\to2n\) half-step rule | PASS | PASS | combinatorial PASS if vertices remain distinct |
| \(R_m/R_0\) layer ratio | PASS | PASS | not general as Euclidean radii |
| \(b/a=|\cos i|\) | N/A | PASS | PASS for declared circle-projection model |
| \(R_{\cap}=s_{\mathrm{hull}}\) | PASS | PASS | FAIL/not guaranteed |

## 11. What counts as a stronger project invariant

A candidate becomes stronger only if it satisfies all relevant gates:

1. **definition gate** — exact variables/operator/domain;
2. **algebra gate** — derivation or executable proof;
3. **transformation gate** — explicit class of transformations under which it survives;
4. **counterexample gate** — declared transformations under which it fails;
5. **prior-art gate** — known/equivalent/unlocated status;
6. **reproduction gate** — independent rerun or symbolic/numeric verifier;
7. **claim gate** — no jump from geometry to physical mechanism.

## 12. RLL physical boundary

These geometric invariants do not establish an RLL cosmological mechanism.

Allowed:

\[
\text{geometry invariant}
\to
\text{diagnostic/operator/test feature}.
\]

Blocked without independent evidence:

\[
\text{geometry invariant}
\not\Rightarrow
\text{new physical law}.
\]

Electronic-shell, cosmological, biological, historical and biblical bindings remain separate hypotheses unless independently derived and tested.

## 13. Cross-repository provenance

Upstream mathematical census:

- \`rafaelmeloreisnovo/Matem-tica-\`
- current range: \`MF-0001..MF-0251\`
- master index commit: \`cebd462154e0de5551b2e0c8de6ff3c6f906940d\`
- academic-recognition index commit: \`71d07ba9bbe0f84cc0f0a01d604cf029852b3825\`
- current octagon formalization commit: \`abf9a390792e8b5b81a832c659e00f84722b69b5\`

Research projection:

- \`rafaelmeloreisnovo/papers\`
- academic-recognition pointer commit: \`3d2a82061a9edc2ce5d946ec7682112ed75c1a31\`
- octagon research note commit: \`b44a7df86753b06fd2c8e797ee57a30ea75e0063\`

## 14. R3

**F_ok:** the “invariants of the weave” are now typed by transformation class instead of being treated as one vague universal invariant.

**F_gap:** no global prior-art closure; no image calibration; no independent verifier for this RLL intake; no physical binding.

**F_next:** implement an executable invariant test matrix over rotation, scale, affine projection and counterexamples, then issue PASS/FAIL receipts per invariant family.
