# RLL — Gap Closure + Successor Hypotheses — 2026-08-27

**Target:** `rll/lab`  
**Mode:** append-only / fail-closed  
**claim_allowed:** `false`  
**publication_effect:** `NONE`  

## 0. Contract

This packet does **not** modify the historical DESI 50-hypothesis intake (`H01..H50`).
That intake remains immutable evidence of its original state. New candidates start at
`H51` and live in a successor file.

Invariant:

```text
formula != mechanism != implementation != execution != evidence != claim
CLASS_MATCH != SUPPORTS_EXACT
TOKEN_VAZIO != zero
post-hoc candidate != confirmation
```

Crossed sources:

1. canonical RLL implementation and joint-real artifact;
2. Drive longitudinal Formula ↔ Literature Evidence Graph;
3. project `papers` knowledge packet on cosmology/plasma/photonics;
4. DESI DR2 Results II (`arXiv:2503.14738`);
5. DESI DR2 Results IV Ly-alpha full-shape/AP (`arXiv:2607.27410`);
6. DES Y6 multi-probe cosmology (`arXiv:2601.14559`, `arXiv:2605.27221`);
7. ACT DR6 extended cosmology (`arXiv:2503.14454`);
8. BBN light-element update (`arXiv:2401.15054`);
9. nuisance-only-under-alternative inference: Andrews & Ploberger, Econometrica 62 (1994), DOI `10.2307/2951753`;
10. Bayesian evidence prior-sensitivity methodology (`arXiv:2601.15132`).

No external paper is treated as direct support for an RLL-specific equation unless the
exact equation is evaluated under an equal-treatment likelihood.

---

## 1. Gap closed analytically: H03 has an explicit effective equation of state

Historical H03 is

```math
H^2(z)=H_0^2\left[\Omega_m(1+z)^3+\Omega_\Lambda s^z\right],
\qquad s=\sqrt{3}/2.
```

If the `Omega_Lambda s^z` term is interpreted as a separately conserved effective dark-energy density,

```math
\rho_{DE}(z)/\rho_{DE,0}=s^z.
```

The continuity equation gives

```math
\frac{d\ln\rho}{dz}=\frac{3(1+w)}{1+z},
```

therefore

```math
w_{H03}(z)=-1+\frac{1+z}{3}\ln(s).
```

Since `ln(s)<0`,

```text
for every z >= 0: w_H03(z) < -1
```

and H03 has no finite phantom crossing in the observed `z>=0` domain. At `z=0`,

```text
w_H03(0) ~= -1.04795
```

This **closes the missing physical interpretation**, but not the observational test.
DESI DR2 and DES Y6 currently favor, under the CPL family, a region with `w0>-1` and
`wa<0`; therefore H03 is now a sharper, lower-flexibility adversarial test rather than an
unspecified dynamical-DE candidate.

Additional boundary: H03 as historically written omits the radiation term, so a CMB-era
use must either add the standard radiation contribution explicitly or scope the equation
to late-time background data. No silent extrapolation is allowed.

**Remaining state:** `TOKEN_VAZIO_EXACT_LIKELIHOOD`.

---

## 2. Gap closed structurally: the RLL null is non-regular

Canonical RLL uses

```math
E^2(z)=E^2_{background}(z)+\Omega_{s0}
\left[f(z;z_t,w_t)+(1-f(z;z_t,w_t))(1+z)^3\right].
```

At

```math
\Omega_{s0}=0,
```

both `z_t` and `w_t` disappear exactly from the prediction. They are therefore not
identifiable under the LambdaCDM null.

This is a nuisance-parameter-only-under-the-alternative problem. Classical regular
likelihood-ratio intuition is not automatically valid, and MCMC mixing in the shape
coordinates can become poor as the amplitude approaches zero. The G6 receipt already
showed the relevant symptom: RLL `Rhat(Omega_s0)` and `Rhat(z_t)` were elevated while
the nested evidence was prior-sensitive. A separate RNG defect in `emcee` was later
identified and fixed; the old receipt remains historical.

**Gap reclassified:**

```text
old: implement/run MCMC
new: rerun deterministic sampler + test null non-identifiability + prior sensitivity
```

This motivates `H52` below.

---

## 3. New external-data gap: DESI Ly-alpha full-shape/AP is absent from the July joint-real artifact

DESI DR2 Results IV (2026) reports a full-shape Alcock-Paczynski measurement at
`z_eff=2.33`, including the joint AP+BAO constraints

```text
DH/rd = 8.600 +/- 0.066
DM/rd = 39.32 +/- 0.33
```

and an approximately 1% AP constraint. The same publication notes that the high-redshift
Ly-alpha full-shape point is close to Planck LambdaCDM and reduces the DESI/CMB discrepancy,
while the evolving-DE preference remains in combined lower-redshift datasets.

The canonical `joint_real_likelihood.v2` predates this result and uses the earlier DESI DR2
BAO block. Therefore the full-shape/AP information is a real post-artifact evidence gap.

**Critical anti-double-counting rule:** AP/full-shape and BAO use overlapping Ly-alpha
spectra. The new distances must not simply be appended as independent points. The next
likelihood must ingest the published joint covariance/likelihood or replace the overlapping
Ly-alpha block.

This motivates `H54`.

---

## 4. New candidate H51 — fixed-crossing one-parameter dark energy

This is a **post-hoc discovery hypothesis**, generated after observing the DESI/DES Y6
preference region. It is not confirmatory evidence.

Use the structural constant only as a measurable anchor:

```math
s=\sqrt{3}/2,
\qquad s^2=3/4.
```

Define

```math
w_{51}(a)=-1+A\left(a-\frac{3}{4}\right).
```

Properties:

```text
A=0                 -> LambdaCDM
crossing             -> a=3/4, z=1/3
A>0                  -> w0>-1 and wa<0
one extra parameter  -> lower complexity than free CPL
```

It is exactly equivalent to the CPL constraint

```math
w_0=-1+\frac{A}{4},
\qquad w_a=-A,
```

hence

```math
w_a=-4(w_0+1).
```

The current DESI/DES Y6 preferred regions lie qualitatively in the same quadrant, and
published DES Y6 central values are near this line at the level of a marginal sanity check.
Because `w0` and `wa` are strongly correlated, **marginal error bars cannot establish
agreement**. The cheap first test is a projection of official chains onto this one-dimensional
constraint using the original covariance/posterior samples.

Confirmation must use held-out or future data because H51 was generated after inspection
of existing results. Suitable confirmation routes include future DESI galaxy/quasar
full-shape or DR3 products.

**State:** `TOKEN_VAZIO_EXACT_TEST`.

---

## 5. H52 — null non-identifiability as the dominant G6 inference pathology

Hypothesis:

```text
The remaining G6 convergence/prior-volume sensitivity is primarily structural because
zt and wt are undefined at Os0=0, not merely a sampler implementation defect.
```

Falsifiable protocol:

1. rerun G6 with the repaired explicit `emcee` proposal RNG;
2. preserve the exact likelihood, thresholds and data;
3. compare free `(Os0,zt,wt)` against a preregistered fixed-shape alternative and/or a
   conditional amplitude region used only as a diagnostic;
4. compare Rhat, ESS, posterior geometry and `ln Z` prior sensitivity;
5. do not convert a diagnostic model into a physical claim.

Falsifier: if convergence/evidence stability does not improve when the non-identified
shape freedom is controlled, H52 is rejected or downgraded.

---

## 6. H53 — background-to-growth consistency

The July joint-real code predicts `f*sigma8` with a fixed growth-index approximation
approximately proportional to

```math
\sigma_8\,\Omega_m(z)^{0.55}.
```

The artifact itself records that CLASS/CAMB was unavailable. This is now a priority gap
because DES Y6 3x2pt and ACT DR6 supply independent structure-growth information.

Hypothesis:

```text
If RLL modifies only the homogeneous background while gravity remains GR and the new
sector is smooth on linear scales, the exact linear-growth solution derived from H(a)
must agree with a Boltzmann/GR growth calculation within a preregistered tolerance.
```

Falsifier: exact growth disagrees materially with the current approximation or with
independent growth data under equal treatment.

No perturbation-sector freedom may be introduced after seeing the residuals without a new
hypothesis ID and complexity penalty.

---

## 7. H54 — Ly-alpha AP/full-shape anchor

Hypothesis:

```text
RLL and successor background models must reproduce the new z=2.33 AP geometry without
sacrificing lower-z fit or relying on double-counted BAO information.
```

Required evidence before execution:

- published joint AP+BAO covariance/likelihood or equivalent official chain;
- source hash and version;
- explicit overlap map against the existing DESI BAO rows;
- replacement/joint-model policy;
- identical baselines and nuisance treatment.

Until those are materialized: `TOKEN_VAZIO_JOINT_COVARIANCE`.

---

## 8. H55 — QCD-to-BBN persistence bridge

The QCD gate should not be assigned an invented universal `max_abs_delta_h`.
Split the physics into two branches.

### H55-PERSISTENT

If the RLL primordial component persists as radiation-like energy from the QCD epoch to BBN,
then

```math
H/H_{SM}=\sqrt{1+\rho_{RLL}/\rho_{SM}}
```

can be mapped to a BBN `Delta N_eff` constraint after specifying the relativistic degrees of
freedom, temperature evolution and convention.

### H55-TRANSIENT

If the component is transient around the QCD epoch and decays/disappears before BBN, BBN
does not directly bound its peak amplitude. That branch remains `TOKEN_VAZIO` until a
QCD-era-specific observable/constraint is materialized.

This split fills a semantic gap while preserving the numerical bound as unknown.

---

## 9. H56 — H0 lower-bound audit

The July joint-real result places the LCDM and RLL optimum near the configured lower bound
`H0=60 km/s/Mpc`, while CPL is slightly interior. A fit pinned to a hard boundary can distort
optimization diagnostics and information-criterion interpretation.

The newer DESI Ly-alpha full-shape paper reports, under LambdaCDM with a BBN prior,

```text
H0 = 66.5 +/- 1.3 km/s/Mpc.
```

This does not directly refit RLL, but it makes the boundary contact operationally urgent.

Hypothesis:

```text
The H0~60 optimum is partly a parameter-bound / compressed-rd/CMB approximation artifact.
```

Falsifier: widen the H0 range with every other data/model choice frozen; if the optimum
remains interior and stable with no boundary pile-up, the boundary-artifact hypothesis is
rejected.

Run this audit **before** interpreting small differences in AIC/BIC as robust.

---

## 10. H57 — magnetic/plasma latent from project papers, reformulated fail-closed

The project knowledge packet contains the candidate extension

```math
\Omega_{s0}\rightarrow\Omega_{s0}
\left[1+\alpha_B(\Omega_{B0}a^{-4})^\beta\right].
```

The same packet correctly states that local MHD/plasma mechanisms do not establish a
cosmological dark-sector coupling. Therefore H57 is not activated as a fit parameter yet.

Promotion requirements:

1. define a covariant cosmological stress-energy contribution;
2. close units and no-double-counting against standard radiation/EM sectors;
3. define a cosmological magnetic observable;
4. specify the `alpha_B=0` nested limit;
5. compare against standard primordial-magnetic-field baselines;
6. only then open an equal-treatment likelihood.

**State:** `TOKEN_VAZIO_OBSERVABLE / REFORMULATE_FIRST`.

---

## 11. Priority order

```text
P0  H56  H0 boundary audit                         cheap; may change interpretation
P0  H52  deterministic G6 rerun + nonidentifiability diagnostic
P1  H03  exact equal-treatment likelihood         model already fully defined now
P1  H51  official-chain line projection           cheap, one-dimensional, post-hoc
P1  H54  DESI Ly-alpha AP/full-shape upgrade      requires joint covariance/likelihood
P2  H53  exact growth / CLASS-CAMB benchmark       closes an explicit artifact gap
P2  H55  QCD persistent-vs-transient mapping       do not invent a universal bound
P3  H57  magnetic/plasma cosmology reformulation   observable first, fit later
```

## 12. What is genuinely closed in this packet

```text
CLOSED_ANALYTIC:
- H03 -> explicit w_eff(z)
- H03 -> no phantom crossing for z>=0
- H51 -> exact CPL constraint wa=-4(w0+1)
- H51 -> exact crossing z=1/3
- RLL Os0=0 -> zt/wt non-identifiable

RECLASSIFIED:
- G6 gap -> deterministic rerun + nonregular inference, not missing MCMC implementation
- QCD gap -> persistent branch vs transient branch

OPEN/TOKEN_VAZIO:
- H03 exact likelihood
- H51 chain projection and held-out confirmation
- post-RNG G6 scientific convergence
- latest Ly-alpha joint covariance/likelihood ingestion
- exact RLL growth
- QCD numeric max_abs_delta_h
- magnetic/plasma cosmological observable
```

## 13. Anti-regression

- H01..H50 remain untouched.
- Contradicted H15/H21/H25 remain contradicted under their recorded interpretations.
- H35 remains malformed as a real auto-power spectrum unless retyped under a new ID.
- Negative Bayes factors and failed convergence receipts remain immutable evidence.
- No new candidate is allowed to inherit support from a paper that tests only its model class.

---

**R3:** `F_ok = analytic gaps closed + current publications routed + successor hypotheses falsifiable`; `F_gap = exact likelihoods/covariances/reruns remain evidence-gated`; `F_next = execute P0 in order, emit immutable receipts, then promote only survivors within rll/lab.`
