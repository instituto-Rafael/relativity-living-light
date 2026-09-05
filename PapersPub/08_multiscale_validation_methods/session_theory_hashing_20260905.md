# Session Theory Hashing — Scale-Preserving Geometry, Modular Dynamics and Global Closure

**Date:** 2026-09-05  
**Canonical context:** *From the Observed Void to Recurrence*  
**State:** `RESEARCH / APPEND_ONLY / THEORY_HASHING / claim_allowed=false`  
**Leaf schema:** `raf.theory.leaf.v1`  
**Leaf count:** 46  
**Session Merkle root:** `2cb1b26f4f7abea31d7a6e959783cb623e11440f879965c412f89a59803ae143`

## 1. Purpose and epistemic boundary

This appendix imports the exact mathematical and computational results of the 2026-09-05 session into the RLL evidence framework. It does not treat a hash as proof, a repeated integer as semantic identity, or a geometric construction as a physical law.

Theory Hashing is defined only as a tamper-evident identity/provenance layer:

```text
leaf = SHA256(NFC(UTF-8(canonical sorted-key compact JSON)))
parent = SHA256(left_leaf_bytes || right_leaf_bytes)
odd terminal leaf is duplicated
```

The resulting ordered-session root is:

`2cb1b26f4f7abea31d7a6e959783cb623e11440f879965c412f89a59803ae143`

Hash equality means payload identity under this canonicalization. It does not establish theorem truth, causal mechanism, empirical validation or cryptographic signature.

## 2. Non-reduction theorem for scale-bearing geometry

The rational equality

\[
\frac{77}{33}=\frac73
\]

preserves slope but does not identify the corresponding scale-bearing vectors:

\[
(77,33)=11(7,3).
\]

Hence geometric measures transform as

\[
L\mapsto 11L,\qquad A\mapsto 11^2A,\qquad V\mapsto 11^3V.
\]

A geometry-preserving rational object therefore stores

```text
ratio
unreduced vector (p,q)
gcd scale
Euclidean norm
direction angle
dimension/measure context
```

and treats the reduced rational as a derived coordinate, not as a replacement for the original geometric state.

## 3. Side-14 equilateral, medial inversion and square bridge

For equilateral side `a=14`:

\[
h=7\sqrt3,
\quad
A_\triangle=49\sqrt3,
\quad
R=\frac{14}{\sqrt3},
\quad
r=\frac7{\sqrt3}.
\]

The medial inverted equilateral has side 7 and planar area ratio

\[
\frac{A_{\rm inner}}{A_{\rm outer}}=\frac14.
\]

Its circumradius equals the outer triangle's inradius:

\[
R_{\rm inner}=r_{\rm outer}=\frac7{\sqrt3}.
\]

The 30°/45° bridge is exact:

\[
14\sin\frac\pi6=7,
\]

\[
7\sqrt2=s_\square,
\]

\[
s_\square\sqrt2=14.
\]

Thus

```text
14 -> 7 -> 7sqrt(2) -> 14
```

closes through the equilateral midpoint operation and the diagonal of the derived square.

The square area is 98. For the outer circumcircle,

\[
A_C=\frac{196\pi}{3},
\]

so

\[
\frac{A_\square}{A_\triangle}=\frac2{\sqrt3},
\qquad
\frac{A_\square}{A_C}=\frac3{2\pi}.
\]

## 4. Planar versus spherical medial inversion

In the Euclidean plane, the medial central triangle has area fraction `1/4`.

For the normalized midpoint construction on a regular icosahedral spherical face:

\[
m_{uv}\cdot m_{uw}=\frac\phi2,
\]

\[
\beta=\frac\pi5,
\qquad
s_c=\frac R\phi,
\qquad
s_g=\frac{\pi R}{5},
\]

and therefore

\[
\frac{s_g}{s_c}=\frac{\pi\phi}{5}.
\]

The central spherical child has area fraction

\[
\eta=
\frac5\pi\left(3\arccos\frac1{\sqrt5}-\pi\right)
\approx0.2862457352435007,
\]

rather than `1/4`. The difference is a finite-curvature effect of the declared spherical construction, not a universal physical constant.

## 5. Frequency-2 icosphere closure

The radial-projected `f=2` icosphere has

```text
V=42
E=120
F=80
Euler=2
```

and exactly two spherical face classes:

```text
20 central inverted spherical-equilateral
60 corner spherical-isosceles
```

The graph incidence is

```text
12 original vertices of degree 5
30 normalized midpoint vertices of degree 6
60 original-midpoint edges
60 midpoint-midpoint edges
```

The flat chordal realization concentrates curvature as angular defects whose sum is `4*pi`. All `C(42,2)=861` unordered vertex pairs collapse into 14 dot-product/angular classes, including 21 antipodal and 180 orthogonal pairs.

## 6. Distinct 42 and 420 namespaces

The following cardinalities are explicitly separate:

```text
42_icosphere_vertices
42_paper_hyperforms = 7 coordinates x 6 operators
42_Z6xZ7_nodes
42_OmegaCube_attractors = 6 tetrahedral edges x 7 phases
42_runtime_slots
FIB_DEPTH_42
```

The frequency-2 icosphere graph is not isomorphic to the circulant `C42(±6,±7)` because

```text
icosphere: E=120, degrees 5/6
circulant: E=84, degree 4
```

although both have diameter 6.

Likewise, three separate 420 constructions are maintained:

```text
lcm(7,10,12,20)=420
7!/(3!*2!)=420 permutations of 0001123
420 authorial/index target
```

Equal integer value does not transfer semantics.

## 7. Modular folds, period 70 and period 420

For

\[
d_m(a,b)=\min(r,m-r),\quad r=(a-b)\bmod m,
\]

the mod-7 fold is

```text
[0,1,2,3,3,2,1]
```

and its cyclic second difference is

```text
[2,0,0,-1,-1,0,0].
```

This localizes the discrete curvature at the fold singularities.

The tuple `(n mod7,n mod14,n mod10)` has joint period 70, while `(n mod7,n mod10,n mod12,n mod20)` has period 420.

At `n=14000`:

```text
14000 = 200*70 -> (0,0,0)
14000 = 33*420+140 -> r420=140 and tuple (0,0,8,0)
```

Thus period-70 closes while period-420 does not. Numeric zero is never `TOKEN_VAZIO`.

For `999`:

```text
999 mod70 = 19
proposed theta_999 = 19*pi/35
999 mod420 = 159
```

These are modular encodings only. A physical 999-Hz interpretation requires a time/unit/calibration contract.

## 8. Fibonacci and Rafaeliana calculus

Canonical Fibonacci modulo 7 has Pisano period 16.

For the integer Rafaeliana,

\[
R_n=F_{n+3}-1
=\sum_{k=0}^{n+1}F_k,
\]

hence

\[
\Delta R_n=F_{n+1}.
\]

Integer Rafaeliana, Fibonacci-perturbed, affine-forced and symbolic real Fibonacci-Rafael families are versioned separately. Cross-family theorem transfer is blocked without an explicit map.

## 9. Seven-component and symbol namespaces

The following are distinct:

```text
RUNTIME_T7=(u,v,psi,chi,rho,delta,sigma)
PAPER_X7=(psi,chi,rho,Delta,Sigma,Omega,Phi_ethica)
FIBONACCI_MOD_T7
D7=(+X,-X,+Y,-Y,+Z,-Z,Omega_context)
```

D7 is an operational inspection coordinate system, not seven physical spatial dimensions.

Overloaded symbols require namespaces:

```text
phi = golden ratio / runtime phi_gate / Phi_ethica
psi = runtime coordinate / paper coordinate / wavefunction-style notation
Delta = paper coordinate / discriminant / runtime delta / modular difference
Sigma = paper coordinate / runtime sigma / Omega-cube sigma bit-field
R = radius / Rafaeliana state / alignment score / Merkle-root label
```

## 10. Dynamics and relation calculus

For `alpha=1/4`, the affine filter

\[
x_{t+1}=\frac34x_t+\frac14u_t
\]

has memory factor `3/4`, explicit inverse for `u_t`, and constant-input error half-life

\[
\frac{\ln(1/2)}{\ln(3/4)}.
\]

Normalized spherical midpoint refinement induces the Möbius map

\[
T(c)=\frac{1+3c}{2(1+c)}.
\]

With

\[
z(c)=\frac{c-1}{c+1/2},
\]

one obtains the exact projective contraction

\[
z(T(c))=\frac14z(c).
\]

Thus repeated midpoint refinement contracts this coordinate by `4^{-n}`; the small angular scale asymptotically halves and the leading arc/chord excess asymptotically quarters.

## 11. Sphere, torus, Bhaskara and focus boundaries

The equilateral-to-concentric-sphere map preserves explicit scale. A line-sphere intersection is the quadratic

\[
At^2+Bt+C_0=0,
\]

whose discriminant classifies intersection multiplicity.

For a torus cross-section radius `r`:

\[
w(\alpha)=2r\sin\alpha,
\]

so `w(30°)=r`; tangent slope magnitude is `1/sqrt(3)` and the local osculating focus is `r/2`.

Embedded `T2` geometry and normalized `T7` state space remain distinct. No physical bridge is inferred.

## 12. Logarithmic scale preservation

For a D-dimensional geometric measure under scale factor `s`:

\[
M_D' = s^D M_D,
\]

therefore

\[
\ln(M_D'/M_D)=D\ln s.
\]

For `(77,33)=11(7,3)`:

```text
Delta ln length = ln 11
Delta ln area   = 2 ln 11
Delta ln volume = 3 ln 11
```

For dimensionless `L/L0>1`:

\[
\ln\ln\frac{sL}{L_0}-\ln\ln\frac{L}{L_0}
=
\ln\left(1+\frac{\ln s}{\ln(L/L_0)}\right).
\]

Thus neither log nor log-log justifies removing geometric scale.

## 13. Theory-hash leaf registry

| ID | Theory | SHA-256 |
|---|---|---|
| TH-001 | Scale-preserving rational geometry | `5c19407255a0992a34c14adf62ead0755cd25e525cf60bf5514086032db737d6` |
| TH-002 | 77/33 versus 7/3 | `2ac63ac129978990513160641fcc360728a55290c553823543904a74325660d3` |
| TH-003 | Geometry object contract | `6acd29338419c77ea2e57e0502dd95a5eb36c01246d31ba79b9f7e689bc3ba6a` |
| TH-004 | External equilateral side 14 | `1dce1617e0ae1fbc4f42aaa45e9c31aa85964ac419419a53a28d0f5cc3f3d418` |
| TH-005 | Medial inversion 14 to 7 | `00541be0ea2dde837414e5764f991d5ec444f6a04fb0aa5269acc45255c1346b` |
| TH-006 | Incircle-circumcircle equality | `1961c9b3b2c0b0a218c597d4a923f45383149818254880a795134bbed3639920` |
| TH-007 | Triangle-square sqrt2 closure | `481851562f603620a4c91b983ad35259bda9224137e5366729f987885e336789` |
| TH-008 | Area square-triangle-circle ratios | `e092ab43275bc54e1e60ebda69b29b6ef8c83233c2f22bac087a45e86d942fa4` |
| TH-009 | Planar versus spherical medial area | `950a4784f79700294a2094975a8e064b87f8ec832294fdd06b139519e32b2f64` |
| TH-010 | Icosphere pi-phi midpoint identity | `7699824898041381e817422893f16048950ab86877276654d097570d7be75ff7` |
| TH-011 | Arc-chord pi-phi ratio | `ee269fc75171f4a72632be95e8266ca6a4ca3544cb5a273017721a817b549b88` |
| TH-012 | Frequency-2 icosphere combinatorics | `1c58d629ce81c8a3a6ff01e1662949324fc6c60d75e8db0c0dd4eadf6a8171f0` |
| TH-013 | Two face classes at f=2 | `6d77017f53ce750307066009a8be1d6924550a61349c347eb8e8569468b970c2` |
| TH-014 | Icosphere incidence classes | `360d88e66f58ccf8dd91c87d22a71f94fd3894cbb3de72378c9ce1d06a47f580` |
| TH-015 | Discrete Gauss-Bonnet chordal closure | `68a0539d0bbea6a33967421c462b5527ab16c246a24aedf04647b97a84356454` |
| TH-016 | Full 42-vertex pair spectrum | `3e232960862023b99395b31d6b5b54ef635d78a03d0e7118603f11b4d6f2f8c1` |
| TH-017 | C42 circulant non-isomorphism | `b201729f13f80d0791ddb14262913cf528bad7e087d8768a89ab94f85ae0ed94` |
| TH-018 | CRT 6x7 representation | `e3a9c36f2fb6e807344c7bd645f4c0c7118a19803281256a6730bc39210a39b3` |
| TH-019 | Multiple 42 namespaces | `e52903722f4d600a0fba8d868c5b97a1d9c269dd4811a1f38d0fcb332a04a54e` |
| TH-020 | Multiple 420 namespaces | `46ac6a2ad3d13d42322aed6b5521c5b2a610dfb2b8db13057350e05180180cd7` |
| TH-021 | Modular folded distance | `0e6f9aac4dff7f1e3bc5504657586e8dfbb50d875824dd9907bcc2d54e0bef03` |
| TH-022 | Fold curvature | `170902577a5bcf63dacd6b775561531e73bcd8d6f36214f4858f15d62f36dc9b` |
| TH-023 | No equilateral triple in C7 | `6453580d5055c27d01e7d6dc8bea9877dc2b0f491da6704b948180558b2f000d` |
| TH-024 | Primes mod7 finite atlas | `6f6b8affc741b24ae11ce09c38e1384c89cd50ec147f13f7c36d90baf2dc8358` |
| TH-025 | Fibonacci mod7 | `06368c212f418a6c4071cb434434233609376157b4c0f392bc79360585df9e1a` |
| TH-026 | Integer Rafaeliana | `c50e0dc108426a80a501114538b61604c5898d1116e732d57c4e3f155887f154` |
| TH-027 | Rafaeliana family separation | `be2f802990412394d6918215f6f1fa84c71a6064da28c352321c7cdbcd69d06d` |
| TH-028 | 420 modular embedding | `27200510a9527089139c6da8157f6266d2013e4a0179499324877436d9412353` |
| TH-029 | 14000 dual closure | `412700786e16fae4c08a4dbe0310efb50d435a3742b43459da8b6a3b9b09ca29` |
| TH-030 | theta999 modular encoding | `17cc01a9b4f77946337f4c0fe4fb3bc182bd9045523bea9d9df7b1970c26c703` |
| TH-031 | Seven-component namespace separation | `b4d9668283226b538ab2062fdc07e09e8e5902782bb775d8010fdc4e51f75683` |
| TH-032 | Symbol collision registry | `25cba69b4baa6b247921ed4bfcb16efc666b21aa34ab7e3cad6290e321b52815` |
| TH-033 | Contraction versus expansion | `735f8d92fc481f39b46513fac7aa7aaf6d7a943fe5c05d499d09562221d73c8e` |
| TH-034 | EMA quarter dynamics | `c8e8fd0252b24ddeabcb5ab0acf9e5829f5c94cc420db5caa9fe83aaa080c9d4` |
| TH-035 | Sphere and torus boundary | `9d27d7fa273f572028519634b102990179401706af538d8831d353ca3e2f8243` |
| TH-036 | Equilateral-to-sphere projection | `2304ad3526282041e17f4a0b5b8d46aba45001245a69b519518d3e5b94ccb3c5` |
| TH-037 | Line-sphere Bhaskara | `7c38bb5cc3bb4dcd383261c8a134a65525bafc0f78169992a51e24722f657927` |
| TH-038 | Torus width and local focus | `c00a20eb7dca9921f515684d9d385bd3b5c1e45954cf7aad981862c78e8e773b` |
| TH-039 | Möbius midpoint operator | `3622339defe1e4bd8e12f99285302f21f10fd2e2315584a01d0fc1cd0431821b` |
| TH-040 | Projective quarter contraction | `d444db540268628332350bf7939c42e6c7d66b5075d3727f3665610394957128` |
| TH-041 | Angular and arc-chord asymptotics | `a2a105ecac85af73561c01b5e30f57057e405765386dcc8441307085561de5ba` |
| TH-042 | Operational recurrence versus memory | `bc69112801d7d44b2b8336988832866374dab4f1d2df66d1f09e44b75e139843` |
| TH-043 | Theory hashing principle | `3bd5fb847489fdd8104b3003398a91e61ba82e0c1506d7db90fe7611739e0b39` |
| TH-044 | Theory Merkle aggregation | `b31e8de607608856538af8511767c64290ef0bf618120b26983e69a0b0bf83ae` |
| TH-045 | Log-scale geometry preservation | `5250c9b723ea96bf1402ff72929f24c44d061e94a9deee58d9bcc73b984597ad` |
| TH-046 | Log-log scale transform | `b108278cd729404291956822820419d3cdb9bf22d17c1f8f284e7d3137b54db4` |

## 14. Remaining gates

```text
canonical cross-42 maps = TOKEN_VAZIO
paper hyperform -> runtime stage map = TOKEN_VAZIO
physical T2 <-> T7 bridge = TOKEN_VAZIO
physical meaning of pi*phi/5 = TOKEN_VAZIO
real/symbolic Fibonacci-Rafael integer discretization = TOKEN_VAZIO
physical theta999 time/unit contract = TOKEN_VAZIO
rho_log domain/base = TOKEN_VAZIO
sigma_mod weights/modulus = TOKEN_VAZIO
physical D7 interpretation = BLOCKED
```

## 15. R3

```text
F_ok   = 46 hashed theory leaves + scale-preserving 77/33 and side-14 geometry + modular/topological/dynamical closure
F_gap  = only maps, empirical contracts and physical evidence not derivable from current definitions
F_next = bind each future cross-domain relation explicitly and hash the successor claim/evidence packet append-only
```
