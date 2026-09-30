# RLL — Causal Scenario Ensemble / Body Y / Cascade V1

**Date:** 2026-09-15  
**Parent:** \`docs/canonicos/34_RMRCTI_OMEGA_WORLDLINE_CASCADE_ROUTER.md\`  
**Sibling:** \`docs/science/OBSERVABILITY_WINDOW_I3ATLAS_HALLEY_V1.md\`  
**State:** \`MODEL_CONTRACT / DATA_TOKEN_VAZIO / claim_allowed=false\`

## 0. Purpose

Extend the existing RMRCTI worldline/cascade router with a bounded counterfactual scenario ensemble.

"Multiversal", "metaversal" and "parallel realities" are normalized here as:

\[
\boxed{
\text{counterfactual scenario ensemble}
}
\]

unless independent physical evidence for a literal multiverse is supplied.

The generic body is \(Y\); its identity is \`TOKEN_VAZIO\`.

## 1. State

\[
X_Y=
\{
x^\mu,u^\mu,p^\mu,m,R,\omega,
composition,\rho,T,
provenance,\Sigma_X
\}.
\]

Between discrete events:

\[
X_{k+1}^{-}=\Phi_k(X_k^-,\mathcal F,\partial\Omega)
\]

and event update:

\[
X_{k+1}^{+}
=
\mathcal E_{k+1}(X_{k+1}^{-};\eta_{k+1}).
\]

This reuses the existing canonical worldline router rather than creating an incompatible dynamics layer.

## 2. Scenario set

\[
\mathcal S_Y=
\{
s_{\rm flyby},
s_{\rm deflect},
s_{\rm capture},
s_{\rm eject},
s_{\rm collide},
s_{\rm fragment},
s_{\rm tidal},
s_{\rm accrete},
s_{\rm strong-field}
\}.
\]

Each state has:

\[
s_j=
(
preconditions,
dynamics,
conservation,
observables,
uncertainty,
falsifier
).
\]

No branch gets nonzero scientific weight merely because it is linguistically imaginable.

## 3. N-body perturbation gate

Weak-field baseline:

\[
\dot{\mathbf r}=\mathbf v,
\]

\[
\dot{\mathbf v}
=
-\sum_i GM_i
\frac{\mathbf r-\mathbf r_i}
{|\mathbf r-\mathbf r_i|^3}
+
\mathbf a_{NG}.
\]

Close planetary or stellar passages may alter the body's heliocentric/galactocentric energy and angular momentum.

The RLL must preserve frame dependence:

\[
\Delta E_{\rm heliocentric}
\neq
\Delta E_{\rm planetocentric}.
\]

## 4. Bound/unbound transition

\[
\epsilon=
\frac{v^2}{2}-\frac{\mu}{r}.
\]

\[
\epsilon<0\Rightarrow bound,\qquad
\epsilon>0\Rightarrow unbound.
\]

A branch-changing event must demonstrate a physical \(\Delta\epsilon\) sufficient to cross zero with covariance propagated.

## 5. Collision operator

\[
X^{+}
=
\mathcal E_{\rm collision}
(X_1^{-},X_2^{-};
v_{\rm rel},
b,
strength,
porosity,
spin,
composition).
\]

Conservation gate:

\[
\sum p^\mu_{\rm before}
=
\sum p^\mu_{\rm after}.
\]

At nonrelativistic scale this reduces to momentum conservation plus an explicit energy budget.

Possible results:

\[
\{\text{crater},\text{deflection},\text{merge},\text{fragmentation},\text{catastrophic disruption}\}.
\]

## 6. Ejecta geometry

A planar "360 degree" statement is mapped to a 3D angular density:

\[
f(\theta,\phi),\qquad
\int_{4\pi}f\,d\Omega=1.
\]

Uniformity is not assumed.

DART/Dimorphos provides an observed control that ejecta recoil can materially enhance momentum transfer.

## 7. Strong-gravity / black-hole gate

Use:

\[
R_s=\frac{2GM}{c^2}.
\]

The strong-field branch is enabled only if:

\[
R_{\rm eff}\le R_s
\]

under a physically specified mass-energy and collapse/compression model.

For ordinary asteroid/comet collision scenarios:

\[
\boxed{
BLACK\_HOLE\_FORMATION=BLOCKED\_BY\_ENERGY\_DENSITY
}
\]

unless the gate is explicitly closed by a valid model.

This aligns with \`FALSIFIABILITY_PROTOCOL.md\`: Schwarzschild identities cannot be relabelled as astrophysical evidence.

## 8. Cascade graph

\[
G_C=(V_C,E_C,W_C)
\]

with nodes as physical events and weighted edges as conditional transitions.

A bounded event-chain example:

\[
E_0:\text{collision}
\rightarrow
E_1:\text{fragmentation}
\rightarrow
E_2:\text{secondary encounters}
\rightarrow
E_3:\text{additional collisions/ejections}.
\]

Define branch factor:

\[
B_k=
\sum_j
P(E_{k+1}^{(j)}\mid E_k,D,M).
\]

This is an operational branching score, not a conserved physical quantity.

Energy control:

\[
E_{\rm out}
\le
E_{\rm in}
+
E_{\rm released,stored}
\]

for the declared boundary.

"Cascade" must therefore not be used to imply energy creation.

## 9. Domino / avalanche regimes

Three distinct meanings are separated:

1. **causal chain:** one event changes conditions for another;
2. **collisional cascade:** fragments increase future collision opportunities in a dense population;
3. **dynamical cascade:** perturbations propagate through coupled orbital/resonant degrees of freedom.

NASA's Kessler-syndrome description is an existence proof of regime-specific collisional cascading. It is not a universal astrophysical cascade law.

## 10. Scenario posterior

\[
P(s_j\mid D,M)
=
\frac{P(D\mid s_j,M)P(s_j\mid M)}
{\sum_kP(D\mid s_k,M)P(s_k\mid M)}.
\]

The model keeps all admitted branches addressable while allowing evidence to make some branches negligible.

Thus:

\[
\text{logical possibility}
\neq
\text{physical plausibility}
\neq
\text{posterior support}.
\]

## 11. Coupling to observability window

For window \(W\):

\[
D_W=M_W X+\epsilon.
\]

Scenario uncertainty:

\[
H_S(W)
=
-\sum_jP(s_j\mid D_W)\log_2P(s_j\mid D_W).
\]

A wider or multi-vantage window should reduce \(H_S\) only if it adds independent discriminating information.

This gives a direct bridge to \(\Sigma_W^*\) without identifying Shannon entropy with thermodynamic entropy.

## 12. Required simulation

Minimum finite experiment:

- body Y synthetic state;
- Sun + selectable planetary perturbers;
- bound and unbound initial conditions;
- close-flyby operator;
- collision operator;
- anisotropic ejecta distribution;
- conservation checks;
- branch posterior;
- window masking;
- strong-gravity gate hard-disabled by default;
- deterministic seed + receipt.

## 13. Hard boundaries

\[
SCENARIO\_ENSEMBLE\neq PHYSICAL\_MULTIVERSE\_EVIDENCE
\]

\[
COLLISION\neq BLACK\_HOLE
\]

\[
EJECTA\neq UNIFORM\_4PI
\]

\[
CASCADE\neq FREE\_ENERGY
\]

\[
POSSIBLE\neq PREDICTED
\]

\`claim_allowed=false\`.
