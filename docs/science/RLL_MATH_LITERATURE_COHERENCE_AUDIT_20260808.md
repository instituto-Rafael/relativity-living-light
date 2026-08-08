# RLL Math + Literature Coherence Audit — 2026-08-08

```text
status=REVIEWED_FAIL_CLOSED
claim_allowed=false
scope=background + EFT + growth + DESI/Pantheon literature + BITRAF cross-math guardrail
```

## 1. Purpose

This audit separates four layers that must not be collapsed into one claim:

1. exact mathematical identities;
2. equations actually implemented in RLL;
3. physical closure required by GR/EFT/continuity;
4. observational support from current cosmology literature.

The goal is not to promote RLL from resemblance. The goal is to determine which equations close, which fail, which remain phenomenological, and which experiments can falsify the remaining model.

## 2. Repository sources inspected

Canonical files read from `main` at base commit `72dec9cb499a4f6e28a994b3f3943cad90a2ca27`:

- `docs/RLL_FORM_GAP_MAP.md` — blob `b917cc04b977bde7d206b34c9aa5902d5469d3f4`;
- `docs/LAGRANGIANO_EFT.md` — blob `c675b20ca5fa65ee5feb1dfc74e9916507e2168e`;
- `docs/ESTABILIDADE_GHOST_CHECK.md` — blob `e5f1f94b26615e24da5fd5ca808c1b4fc9001895`;
- `src/rll/class_rll_background.c` — blob `39fbfe9a7ba299d49bdbfda20865d08685c8b17a`;
- `scripts/check_rll_background.py` — blob `e6c8279a4b1bb33518819593e67184ec70f33e11`;
- `docs/RLL_GROWTH_FSIGMA8.md` — blob `635abbef0e9eac6fe7012577c931772ff80d9483`;
- `src/rll/rll_perturbation_kernel.py` — blob `c146f981df8b5c23d0dd3dbb62192aa125af31f3`;
- `docs/RLL_W0WA_IMPLEMENTATION_LEDGER.md` — blob `6489161c59a91c1e9c8fc4d154de26f10a83268c`;
- `docs/science/RLL_COSMOLOGY_GAP_AUDIT_20260717.md` — blob `48f0d5d00b93247a16bc79d71ba0f4aa2d037bee`.

## 3. What RLL currently implements

The logistic transition is

\[
f(z)=\frac{1}{1+\exp[(z-z_t)/w_t]},\qquad w_t>0.
\]

With `a=(1+z)^-1`, define

\[
R(a)=f(a)+[1-f(a)]a^{-3}.
\]

The background implementation uses

\[
E^2(a)=\Omega_m a^{-3}+\Omega_\Lambda+\Omega_{s0}R(a),
\qquad
\Omega_\Lambda=1-\Omega_m-\Omega_{s0}.
\]

The EFT and stability documents additionally assign

\[
\rho_s=\Omega_{s0}\rho_{c0}R(a),
\qquad
p_s=-\Omega_{s0}\rho_{c0}f(a),
\]

and therefore

\[
w_{\rm doc}=\frac{p_s}{\rho_s}=-\frac{f}{R}.
\]

These expressions are implemented consistently with each other at the algebraic level. The physical conservation test below is a separate requirement.

## 4. P0 mathematical finding — continuity does not close with the documented pressure

For a separately conserved FLRW component,

\[
\frac{d\rho_s}{d\ln a}+3(\rho_s+p_s)=0.
\]

The RLL transition satisfies

\[
f'\equiv\frac{df}{d\ln a}
=\frac{1+z}{w_t}f(1-f).
\]

Differentiating `R(a)` gives

\[
R'=f'(1-a^{-3})-3(1-f)a^{-3}.
\]

Using the currently documented pressure `p_s/(Omega_s0 rho_c0)=-f`, the exact continuity residual is

\[
\boxed{
\mathcal C(a)
\equiv
\frac{1}{\Omega_{s0}\rho_{c0}}
\left[
\frac{d\rho_s}{d\ln a}+3(\rho_s+p_s)
\right]
=f'(1-a^{-3})
}
\]

Therefore

```text
C(a)=0 only if f'=0 or a=1.
```

For a genuine transition, `f' != 0` over a finite redshift interval. Consequently:

```text
rho_s + documented p_s + separate conservation = FAIL
```

This is not a numerical issue. It is an exact symbolic mismatch.

### 4.1 Closure A — conserved effective fluid

If `rho_s(a)` is preserved and the sector is required to conserve separately, pressure is not free. It must be

\[
p_{\rm cons}=-\rho_s-\frac{1}{3}\frac{d\rho_s}{d\ln a}.
\]

In units of `Omega_s0 rho_c0`,

\[
\boxed{
\frac{p_{\rm cons}}{\Omega_{s0}\rho_{c0}}
=-f+\frac{f'}{3}(a^{-3}-1)
}
\]

and

\[
\boxed{
w_{\rm cons}(a)=
\frac{-f+\frac{f'}{3}(a^{-3}-1)}
{f+(1-f)a^{-3}}
}.
\]

This `w_cons` is the equation of state implied by the implemented density if the RLL sector is a separately conserved effective fluid.

### 4.2 Closure B — interacting sector

If the project intentionally keeps `p_s=-Omega_s0 rho_c0 f`, then the sector must be interacting. With convention

\[
\frac{d\rho_s}{d\ln a}+3(\rho_s+p_s)=\frac{Q_s}{H},
\]

RLL requires

\[
\boxed{
\frac{Q_s}{H}=\Omega_{s0}\rho_{c0} f'(1-a^{-3})
}.
\]

An equal-and-opposite exchange must then be specified in another sector so that total stress-energy conservation is preserved. The present background leaves matter scaling as `a^-3` and Lambda constant, so that compensating exchange is not yet represented.

Status:

```text
interaction_closure=TOKEN_VAZIO
```

## 5. Consequence for the current canonical scalar reconstruction

The repository uses the standard canonical relations

\[
K=\frac{1+w}{2}\rho,
\qquad
V=\frac{1-w}{2}\rho,
\]

and

\[
\frac{d\phi}{d\ln a}
=M_{\rm Pl}\sqrt{3\Omega_s(1+w)}.
\]

These relations are appropriate for a minimally coupled canonical scalar after its stress-energy evolution has been closed consistently.

Because the documented `(rho_s,p_s)` pair has a non-zero continuity residual during the transition, the present `K(a)`/`V(a)` reconstruction is not yet a demonstrated covariant completion of the implemented background.

Required decision:

```text
A. conserved effective fluid -> use p_cons and w_cons;
B. interacting fluid/field -> specify Q and the receiving sector;
C. pure phenomenological H(z) -> stop calling the current map a closed EFT.
```

Until one route is selected and tested:

```text
canonical_EFT_closure=BLOCKED
```

## 6. Sound speed and perturbations

The EFT note correctly states that a canonical scalar has rest-frame sound speed

\[
c_s^2=1.
\]

The executable background gate also defines

\[
c_{s,\rm proxy}^2=f(z).
\]

Bounding a proxy in `[0,1]` is mathematically harmless, but it is not a derivation of perturbative sound speed. The two objects must remain explicitly separated.

The current linear growth kernel solves

\[
D_{xx}+
\left(2+\frac{d\ln H}{d\ln a}\right)D_x
-\frac{3}{2}\Omega_m(a)D=0,
\qquad x=\ln a.
\]

This is a useful GR smooth-dark-energy/background-response equation. It does not evolve perturbations of the RLL sector itself, an interaction `Q`, entropy perturbations, anisotropic stress, or a Boltzmann hierarchy.

Therefore the current growth result should be classified as

```text
linear_growth_background_response=OBSERVED_LIMITED
exact_RLL_perturbation_theory=TOKEN_VAZIO
```

There is also a metadata inconsistency: `scripts/check_rll_background.py` still emits `growth_solver=TOKEN_VAZIO`, while a separate executable perturbation/growth kernel now exists. This is a stale status field, not evidence that the solver is absent.

## 7. Comparison with current literature

### 7.1 DESI DR2 key cosmology result

Reference: DESI Collaboration, **DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations and Cosmological Constraints**, arXiv:2503.14738 (2025).

Relevant result for RLL review:

- the BAO+CMB combination prefers a time-varying `w0-wa` solution over LambdaCDM;
- adding supernova samples changes the significance but maintains the dynamical-dark-energy tension;
- the favored region has `w0 > -1` and `wa < 0`.

This makes RLL's explicit `w(z)` mapping scientifically relevant, but it does not validate the logistic form.

### 7.2 DESI extended dark-energy analysis

Reference: DESI Collaboration / Lodha et al., **Extended Dark Energy analysis using DESI DR2 BAO measurements**, arXiv:2503.14743 (2025).

The paper compares parametric and non-parametric reconstructions and reports that a two-parameter `w(z)` captures the current trend well. It also reports preference for histories featuring phantom-divide crossing, while quintessence-only alternatives remain disfavored but not ruled out.

A single minimally coupled canonical scalar satisfies `w >= -1` and cannot realize genuine phantom crossing. Thus a canonical RLL closure is a restrictive, falsifiable subclass — not a mechanism that automatically explains the DESI preference.

### 7.3 Model-independent quintessence reconstruction with DESI DR2 + Pantheon+

Reference: Wang, Li, Liu, Du, **Model-Independent Reconstruction of Quintessence Potential and Kinetic Energy from DESI DR2 and Pantheon+ Supernovae**, arXiv:2603.21125 (2026).

This work reconstructs potential and kinetic terms directly from current data and emphasizes that derivative reconstruction can amplify uncertainties; apparent negative kinetic energy around intermediate redshift can arise statistically.

Operational consequence for RLL:

```text
kinetic_gate_without_uncertainty_propagation != observational proof of canonical viability
```

RLL should propagate posterior/data uncertainty through `f`, `f'`, `rho`, `w`, `K`, and `V` rather than test only one central parameter point.

### 7.4 Pantheon+

Reference: Brout et al., **The Pantheon+ Analysis: Cosmological Constraints**, arXiv:2202.04077.

Pantheon+ uses 1701 light curves from 1550 distinct SNe Ia and a systematic covariance treatment. This reinforces the repository's existing P0 requirement that full STAT+SYS covariance be used inside the same canonical posterior route before publication-grade SNe claims.

### 7.5 EFT/quintessence reconstruction precedent

Reference: Park, Raveri, Jain, **Reconstructing Quintessence**, arXiv:2101.04666.

This EFT-based reconstruction combines CMB, supernova, clustering and lensing information. The relevant lesson for RLL is methodological: a scalar-field reconstruction is judged jointly by background evolution, perturbations, stability and multiple likelihoods, not by an `H(z)` fit alone.

## 8. BITRAF64 cross-mathematics — exact identity, no cosmological bridge yet

The BITRAF64 material contains the factor

\[
q=\frac{\sqrt3}{2}.
\]

Its classical geometric identities are exact:

\[
\frac{\sqrt3}{2}=\cos30^\circ=\sin60^\circ
\]

and, for an equilateral triangle of side `a`,

\[
h=\frac{\sqrt3}{2}a.
\]

Therefore

\[
q^{n+2}=\frac{3}{4}q^n.
\]

Likewise Fibonacci asymptotics follow from the characteristic quadratic

\[
r^2-r-1=0,
\]

whose roots are

\[
\phi=\frac{1+\sqrt5}{2},
\qquad
\psi=\frac{1-\sqrt5}{2}.
\]

These identities are legitimate mathematics. They do **not** currently derive `Omega_s0`, `z_t`, `w_t`, `H(z)`, the stress-energy tensor, or a cosmological observable in RLL.

Guardrail:

```text
BITRAF_classical_identity=MATH_PASS
BITRAF_to_RLL_physical_operator=TOKEN_VAZIO
```

A cross-project connection becomes physics only after it supplies units, an operator, a dynamical equation, and an observable that survives comparison with data.

## 9. Immediate falsifiable work

### P0 — continuity and EFT

1. Add a symbolic/numeric continuity residual gate for the currently documented `(rho_s,p_s)` pair.
2. Choose conserved-fluid, interacting-sector, or phenomenological-background semantics.
3. Recompute `w`, `K`, `V` from the selected closure.
4. If interacting, define `Q` and modify the receiving sector consistently.
5. Propagate posterior uncertainty through `f'`, `w`, `K`, and `V`.

### P0 — status coherence

6. Replace the stale `growth_solver=TOKEN_VAZIO` field with an explicit distinction between `linear_background_response_available` and `exact_RLL_perturbations=TOKEN_VAZIO`.

### P1 — observational comparison

7. Map RLL's effective `w(a)` into the same observable space used by DESI DR2 `w0-wa` analyses.
8. Use the canonical full DESI covariance and full Pantheon+ STAT+SYS covariance in the same posterior route.
9. Preserve LambdaCDM and `w0-wa` as adversarial baselines.
10. Report posterior predictive residuals, prior sensitivity and evidence with method/version receipts.

### P2 — perturbations/backend

11. Only after continuity is closed, derive dark-sector perturbation equations.
12. Then implement CLASS/CAMB parity and validate LambdaCDM recovery before RLL activation.

## 10. Claim ledger

| Claim | Status | Reason |
|---|---|---|
| Logistic `f(z)` implementation | `PASS` | formula and code agree |
| `E2_RLL` background implementation | `PASS` | executable and internally consistent as a phenomenological background |
| documented `rho_s,p_s` separately conserved | `FAIL` | exact residual `f'(1-a^-3)` |
| canonical scalar EFT reconstruction | `BLOCKED` | depends on unresolved conservation/interaction semantics |
| `cs2_proxy=f` as physical sound speed | `NOT_DEMONSTRATED` | proxy is not a perturbative derivation |
| linear `f sigma8` background-response solver | `OBSERVED_LIMITED` | executable, dark-sector perturbations absent |
| exact RLL perturbation/Boltzmann model | `TOKEN_VAZIO` | not closed |
| DESI DR2 relevance of dynamic `w(z)` | `PASS_CONTEXT` | modern data motivate testing dynamic-DE forms |
| DESI DR2 validates RLL logistic form | `BLOCKED_CLAIM` | no such inference follows |
| `sqrt(3)/2` and golden-ratio identities | `MATH_PASS` | classical identities |
| BITRAF identities imply RLL cosmology | `TOKEN_VAZIO` | no physical derivation/operator yet |

## 11. Closure

```text
F_ok:
- RLL has a real executable logistic background.
- RLL has a real linear growth/background-response solver.
- The project already identifies covariance, CMB/Boltzmann and microphysics as open layers.
- Modern DESI DR2 makes dynamic dark energy a scientifically relevant comparison target.
- BITRAF sqrt(3)/2 and Fibonacci/golden-ratio relations contain exact classical mathematics.

F_gap:
- the documented logistic rho/p pair fails separate continuity during the transition;
- the current canonical EFT reconstruction therefore lacks physical closure;
- exact RLL perturbations remain open;
- full covariance/posterior unification remains necessary;
- BITRAF-to-RLL physical coupling remains TOKEN_VAZIO.

F_next:
continuity gate -> choose physical semantics -> reconstruct EFT consistently ->
propagate uncertainties -> unify DESI/Pantheon posterior -> derive perturbations -> backend parity.
```

The strongest next move is not to add more symbolic constants. It is to make the already implemented density obey an explicit conservation law or to declare and implement the interaction that replaces separate conservation.
