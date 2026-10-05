# RLL Median Multicarrier Theorem Candidates V1

Status: research lab, append-only successor to PR #1061.

Boundary:

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
APPROXIMATION != IDENTITY
DRAWING_TOPOLOGY != CALIBRATED_METRIC
FORMAL_COHERENCE != PHYSICAL_BINDING
claim_allowed=false
```

## 1. Session-as-one-object

This document treats the whole bounded session as one evolving object rather than independent prompts. The carriers that appeared are kept typed and coexisting:

- geometric: triangles, medians, medial triangles, polygons, stars, circles, arcs, annuli, rotated squares;
- numeric: bases, residues, primes, repunits/repdigits, exact radicals and ratios;
- graph: incidence, functional residue graphs, factor bipartite graphs, Cayley-type graphs;
- set: nested regions, residue classes, typed void states, products/intersections;
- statistical/physical boundary: residual regressions, covariance, formal fluid equations, no physical promotion without binding evidence.

The current RLL base for this successor is `rll/lab@d7bcf03632f2a44235d2e429b53726e07d9c75f3`.

## 2. Median of median of median: classical closed form

Let a triangle have vertices `A_0,B_0,C_0` and centroid

\[
G=\frac{A_0+B_0+C_0}{3}.
\]

Define the labelled medial transform by

\[
A_{k+1}=\frac{B_k+C_k}{2},\quad
B_{k+1}=\frac{C_k+A_k}{2},\quad
C_{k+1}=\frac{A_k+B_k}{2}.
\]

Then exactly

\[
\boxed{V_k-G=\left(-\frac12\right)^k(V_0-G)}
\]

for each labelled vertex `V=A,B,C`.

Consequences:

\[
\boxed{\ell_k=2^{-k}\ell_0},\qquad
\boxed{\Delta_k=4^{-k}\Delta_0}.
\]

The centroid is invariant. The sign alternates because the labelled medial triangle is the image of the original under a homothety centered at `G` with factor `-1/2`.

This core result is **classical**, not a novelty claim.

## 3. A useful set-theoretic corollary

For the nested closed medial triangles `T_k`,

\[
T_{k+1}\subset T_k,\qquad \operatorname{diam}(T_k)\to0,
\]

so

\[
\boxed{\bigcap_{k\ge0}T_k=\{G\}}.
\]

At the same time,

\[
\operatorname{area}(T_k)\to0.
\]

Thus zero limiting area does **not** imply an empty limiting set:

\[
\boxed{\text{MEASURE ZERO}\neq\varnothing}.
\]

Within the session ontology this is a rigorous example supporting the separation of `NUMERIC_ZERO`, `EMPTY_SET`, and `TOKEN_VAZIO`. It is a derived classical corollary, not a new theorem claim.

## 4. General cyclic side-division map

For `t in [0,1]`, define

\[
A'=(1-t)B+tC,\quad
B'=(1-t)C+tA,\quad
C'=(1-t)A+tB.
\]

The centroid remains fixed and the exact area factor is

\[
\boxed{q(t)=1-3t+3t^2}.
\]

Therefore one identical iteration gives

\[
\Delta'=q(t)\Delta,
\]

and repeated identical iterations give

\[
\boxed{\Delta_k=q(t)^k\Delta_0}.
\]

At `t=1/2`, `q=1/4`, recovering the medial case. This belongs to established affine/cevian geometry territory and is classified `DERIVED_KNOWN_FAMILY` pending exact source matching.

## 5. Candidate composition: stroboscopic median-residue relation

Let the numerical carrier be a finite tuple of moduli

\[
M=(m_1,\ldots,m_s),
\]

with residue signature

\[
\mathcal R(k)=(k\bmod m_1,\ldots,k\bmod m_s)
\]

and joint period

\[
L=\operatorname{lcm}(m_1,\ldots,m_s).
\]

Then the numerical state recurs:

\[
\boxed{\mathcal R(k+L)=\mathcal R(k)}.
\]

If the geometry evolves by the medial transform, at that same stroboscopic return:

\[
\boxed{V_{k+L}-G=\left(-\frac12\right)^L(V_k-G)},
\]

\[
\boxed{\Delta_{k+L}=4^{-L}\Delta_k}.
\]

If `L` is even, the labelled geometric orientation parity agrees; if `L` is odd, the signed centered vertex factor is negative.

For the already canonical session carrier

\[
M=\{3,7,14,10,30,5,50,70\},
\]

\[
L=1050.
\]

Hence the discrete residue signature repeats every 1050 iterations while the medial geometry has contracted by

\[
2^{-1050}
\]

in length and

\[
4^{-1050}
\]

in area. `1050` is an arithmetic carrier period, not a cosmological period.

This exact combined statement is registered as `CANDIDATE_NEW_COMPOSITION`, **not** as an established authorial theorem. Its ingredients are classical; novelty of the composition requires broader prior-art search and independent proof review.

## 6. Product carrier for multidimensional coexistence

Define the typed state

\[
\Omega_k=(G_k,N_k,\Gamma_k,S_k),
\]

where:

- `G_k` is geometric state (triangle/medial/cyclic/polygon/star/circle/square-rotation);
- `N_k` is numerical state (base representation, residues, factors, repunits);
- `Gamma_k` is graph state (incidence, functional, factor, Cayley template);
- `S_k` is set state (nested hull, intersections, residue classes, void types).

For independent transformations,

\[
F=F_G\times F_N\times F_\Gamma\times F_S.
\]

Changing the display order of these axes is a permutation of representation, not automatically a change in mathematical meaning. Cross-domain couplings must be declared explicitly and tested; they are not assumed commutative.

This is standard product-dynamics mathematics used here as an engineering framework, not a novelty claim by itself.

## 7. Latest freehand image: pixel-ruler receipt

Latest image SHA-256:

`3785622ae7603e66c9e53439f6ef03d77aacc334a631b31c488a0a50e01d775a`

Raster size: `1024 x 1365` pixels.

A bounded Hough/edge analysis over the dominant colored strokes found three strong orientation families near the triangular basis:

- horizontal: weighted estimate about `-0.53 deg`, RMS about `1.08 deg`;
- first diagonal: about `57.76 deg`, RMS about `2.39 deg`;
- second diagonal: about `122.19 deg`, RMS about `3.00 deg`.

This supports using `0/60/120 deg` as a **pixel-level candidate basis** for measurements on this raster. It does not prove the hand-drawn segments are exact medians, an exact equilateral triangle, or any physical geometry. The image therefore stays `IMAGE_PIXEL_EVIDENCE_ONLY`.

## 8. Prior-art gate

Initial academic discovery finds established literature on:

- cevian geometry and cevian simplexes;
- fixed points of affine maps in triangle geometry;
- generalized cevian constructions;
- medial/median triangle families.

Examples retrieved in the first prior-art pass include work by Igor Minevich and Patrick Morton on fixed points of affine maps and synthetic foundations of cevian geometry, and older work on cevian simplexes. This is already enough to forbid relabeling the medial/affine core as authorial.

The only item presently allowed to retain a novelty-candidate label is the **typed cross-carrier composition** in section 5, and even that remains `prior_art_status=INCOMPLETE` and `claim_allowed=false`.

## 9. Falsifiers

The candidate composition fails or must be downgraded if any of these occur:

1. the modular signature does not return at the declared LCM;
2. medial coordinates disagree with the exact `(-1/2)^k` closed form;
3. area does not scale by `4^-k`;
4. base representation changes are mistaken for value changes;
5. graph isomorphism is confused with geometric equality;
6. an image-derived angle is promoted to exact geometry without calibration;
7. prior art contains the same combined theorem in equivalent form;
8. a formal relation is promoted to RLL physics without an observational binding gate.

## 10. R3

`F_ok`: exact medial closed form, centroid invariant, area contraction, general cyclic area factor, modular LCM recurrence, typed product carrier and pixel-bounded image orientation measurement are now executable/testable.

`F_gap`: complete novelty search, independent proof review, calibrated image geometry, physical/cosmological binding.

`F_next`: run repository CI on this successor; if green, retain T4 only as a preregistered theorem candidate and expand prior-art search before any authorship/novelty claim.
