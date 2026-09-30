# RLL / DESI DR2 — Interaction, Reconstruction and Degeneracy Review — 2026-08-08

```text
status=LITERATURE_REVIEW_FAIL_CLOSED
claim_allowed=false
scope=DESI_DR2 + PantheonPlus + evolving_DE + interacting_dark_sector + growth
```

## 1. Why this review exists

The RLL continuity audit exposes a real physical bifurcation:

```text
A. preserve rho_s(a) and reconstruct a separately-conserved pressure;
B. preserve the historical p_doc(a) and introduce an interaction Q;
C. keep E2_RLL only as a phenomenological background.
```

Modern DESI DR2 literature contains exactly this methodological problem: distinct microphysical models can reproduce similar or even identical background expansion histories while differing in perturbations and structure growth.

This review asks only what the literature permits us to test. It does not use similarity to promote RLL.

## 2. DESI DR2 key cosmology result

### Reference

DESI Collaboration, **DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations and Cosmological Constraints**, arXiv:2503.14738 (2025).

### Relevant result

The collaboration reports that:

- flat LambdaCDM still describes the BAO data well;
- BAO-preferred parameters show a mild mismatch with CMB constraints;
- allowing CPL-like time evolution improves combined fits;
- the preferred local CPL quadrant is `w0 > -1`, `wa < 0`;
- the preference over LambdaCDM varies materially with the supernova sample included.

### RLL consequence

The RLL logistic-density family with positive transition width has, around `a=1`,

```text
wa_doc  > 0
wa_cons > wa_doc > 0
```

so local sign agreement with the DESI key favored CPL quadrant is absent.

```text
DESI_dynamic_DE_relevance=PASS_CONTEXT
DESI_validates_RLL=BLOCKED_CLAIM
local_CPL_sign_match=FAIL
```

## 3. Extended DESI dark-energy analysis

### Reference

DESI Collaboration / K. Lodha et al., **Extended Dark Energy analysis using DESI DR2 BAO measurements**, arXiv:2503.14743 (2025).

### Relevant result

Using parametric and non-parametric reconstructions, the study reports that a two-parameter evolving equation of state captures the dominant trend in the current combined datasets. It also reports preference for histories containing phantom-divide crossing, while alternatives without crossing are disfavored but not excluded.

### RLL consequence

A single minimally coupled canonical scalar satisfies `w >= -1` and cannot implement a smooth genuine phantom crossing by itself. Therefore the canonical conserved-scalar route is a restrictive falsifiable subclass rather than an automatic realization of the DESI trend.

Possible extensions discussed in the wider literature include interacting sectors, non-minimal coupling, multiple fields, higher derivatives and modified gravity. Each introduces new equations and perturbation obligations.

## 4. Dark degeneracy: same background, different physics

### Reference

V. Petri, V. Marra, R. von Marttens, **Dark Degeneracy in DESI DR2: Interacting or Evolving Dark Energy?**, arXiv:2508.17955 (2025; later Phys. Rev. D).

### Relevant result

The authors construct an interacting dark-sector model that is exactly degenerate at the background level with a CPL evolving-dark-energy model. Despite identical expansion histories, the matter sector evolves differently. Their interaction changes sign at late times and produces a distinct prediction for `f sigma8`.

The growth prediction can then be in tension with structure-formation measurements even though the background fit is good.

### RLL consequence

This is directly relevant to the RLL bifurcation:

```text
same_H(z) != same_stress_energy
same_H(z) != same_Q
same_H(z) != same_delta_m
same_H(z) != same_fsigma8
```

Thus an interacting RLL closure cannot be validated from BAO/SNe distances alone. Its `Q` must be carried into perturbation equations and confronted with growth.

## 5. Interacting dark energy after DESI DR2

### Reference

S. Pan, S. Paul, E. N. Saridakis, W. Yang, **Interacting dark energy after DESI DR2: A challenge for the paradigm?**, Phys. Rev. D 113, 023514 (2026).

### Relevance

Current interacting-dark-energy analyses are actively testing whether energy exchange in the dark sector can account for part of the DESI-era dynamical-dark-energy phenomenology. The reported evidence is model- and dataset-dependent rather than a generic confirmation of interaction.

RLL therefore has a legitimate hypothesis class to compare against, but no license to identify its required continuity source term with a physical dark-sector coupling before the recipient sector, covariant transfer vector and perturbations are specified.

```text
RLL_Q_formal_residual=DERIVED
RLL_Q_physical_interaction=TOKEN_VAZIO
```

## 6. Non-minimally coupled quintessence with sign-switching interaction

### Reference

J.-Q. Wang, R.-G. Cai, Z.-K. Guo, Y.-H. Li, S.-J. Wang, X. Zhang, **Nonminimally coupled quintessence with sign-switching interaction**, accepted Phys. Rev. D, 9 July 2026, DOI: 10.1103/4sl7-m1qc.

### Relevance

This recent model illustrates a physically important distinction: the scalar field may remain canonical and never cross the phantom divide while the coupled matter/dark-energy evolution produces an effective observational crossing. The mechanism relies on an explicit coupling and modified matter evolution.

For RLL this reinforces a strict gate:

```text
apparent_effective_crossing_without_Q_equations = NOT_A_MODEL
```

If RLL chooses an interacting closure, the background matter term can no longer silently remain the standard uncoupled `a^-3` law unless the interaction is assigned elsewhere consistently.

## 7. Model-independent quintessence reconstruction

### Reference

S. Wang, T.-N. Li, T. Liu, G.-H. Du, **Model-Independent Reconstruction of Quintessence Potential and Kinetic Energy from DESI DR2 and Pantheon+ Supernovae**, arXiv:2603.21125 (2026).

### Relevant result

The work reconstructs potential and kinetic terms non-parametrically from current BAO and SNe information and explicitly notes that derivative reconstruction amplifies uncertainty. Apparent negative kinetic energy at intermediate redshift can arise as a statistical artifact within propagated uncertainty.

### RLL consequence

RLL currently has analytic derivatives, which is an advantage for numerical stability, but a central-parameter positivity gate is not enough. The uncertainty of fitted parameters must propagate through:

```text
f -> f' -> rho -> p -> w -> K -> V -> phi
```

before a canonical-scalar viability statement is allowed.

## 8. 2026 review: current observational status remains dataset-dependent

### Reference

S. G. Turyshev, **Dark energy after DESI DR2: Observational status, reconstructions, and physical models**, Phys. Rev. D 113, 103540 (26 May 2026), DOI: 10.1103/dqxw-yp1j.

### Relevant result

The review emphasizes that the preference for evolving dark energy depends on data combinations and is particularly sensitive to supernova calibration/selection residuals. It also stresses perturbation-sensitive probes such as redshift-space distortions and weak lensing when mapping background reconstructions to physical models.

### RLL consequence

The repository's existing fail-closed distinction between diagonal Pantheon diagnostics and full covariance is correct and should be retained. Model preference must be recomputed under common covariance, priors and likelihood definitions.

## 9. Counterevidence / consistency challenge

### Reference

**Hint toward an inconsistency between BAO and supernovae datasets: The evidence of redshift evolving dark energy from DESI DR2 is absent**, Phys. Rev. D 113, 083514 (9 April 2026), DOI: 10.1103/k59d-l795.

### Relevant result

This work argues that an inconsistency between BAO and supernova distance information can mimic redshift-evolving dark energy and reports that the dynamical-DE preference weakens when the proposed inconsistency is modeled.

This is important because the DESI-era interpretation is scientifically contested. It would be incorrect to use the DESI key result as an invariant fact that dark energy evolves.

RLL gate:

```text
DESI_DR2_DDE_interpretation=ACTIVE_CONTESTED_RESEARCH
```

The model must therefore survive both the pro-evolution and systematics/consistency interpretations.

## 10. Pantheon+ likelihood boundary inside this repository

The repository already distinguishes:

```text
catalog + diagonal errors -> diagnostic only
catalog + verified STAT+SYS covariance -> canonical full likelihood
```

Current project state still marks full Pantheon+ covariance as `TOKEN_VAZIO` in the readiness document. Therefore the old diagonal RLL-vs-Pantheon route cannot carry publication-grade evidence into either the canonical density family or the logistic-EoS family.

## 11. Two RLL mathematical families must remain separate

### Family D — prescribed density

```text
rho_s(a) proportional to f+(1-f)a^-3
```

Pressure must be reconstructed from continuity or paired with an interaction.

### Family W — prescribed equation of state

The Pantheon diagnostic code uses

```text
w(z)=w0+wa g(z)
```

and integrates continuity to obtain `rho_de(z)`.

These are different constructions. The second automatically builds density from its chosen EoS; the first prescribes density directly.

Evidence transfer is blocked until an explicit equivalence test establishes that the two produce the same observable predictions over the relevant parameter domain.

## 12. Minimum physical implementation if the interaction route is chosen

A publishable interacting closure needs at least:

```text
1. background continuity:
   rho_c' + 3 rho_c = -Q/H
   rho_s' + 3(1+w_s)rho_s = +Q/H

2. covariant definition:
   nabla_mu T_c^{mu nu} = -Q^nu
   nabla_mu T_s^{mu nu} = +Q^nu

3. momentum-transfer prescription / rest-frame choice;
4. perturbation equations for delta_c, theta_c and dark-sector variables;
5. initial conditions;
6. stability checks;
7. LambdaCDM null-limit recovery;
8. CLASS/CAMB parity or an independently validated perturbation backend;
9. fsigma8 / lensing confrontation;
10. common BAO+CMB+SNe likelihood with provenance receipts.
```

The scalar background residual alone supplies item 1's required source function only after a recipient sector and sign convention are fixed. It supplies none of items 2-10 by itself.

## 13. Falsification tree

```text
TEST A — conserved fluid
rho fixed -> p_cons -> w_cons -> K/V -> posterior propagation
    if K<0 robustly in supported posterior -> canonical route fails

TEST B — interacting sector
p_doc fixed -> Q residual -> recipient sector -> perturbations
    if growth/lensing inconsistent -> interacting closure fails

TEST C — phenomenological background
E2 only -> BAO/SNe/CMB distances
    if no model-selection gain under common likelihood -> extra sector unsupported

TEST D — family equivalence
RLL_density vs RLL_EoS on identical parameters/observables
    if H(z), dL(z), growth differ -> evidence must remain family-specific
```

## 14. Current claim ledger

| Claim | Status |
|---|---|
| DESI DR2 motivates evolving-DE tests | `PASS_CONTEXT` |
| DESI DR2 proves evolving dark energy | `BLOCKED_CLAIM` |
| RLL density family locally matches DESI favored `wa` sign | `FAIL` |
| conserved RLL repair reverses `wa` sign | `FAIL` |
| exact background-degeneracy can hide different physics | `SUPPORTED_BY_LITERATURE` |
| RLL has a derived formal continuity source term | `MATH_PASS` |
| that source is a validated dark-sector interaction | `TOKEN_VAZIO` |
| current RLL growth solver validates an interacting model | `FAIL_SCOPE` |
| full Pantheon+ likelihood ready | `TOKEN_VAZIO` |
| logistic-density and logistic-EoS RLL families equivalent | `TOKEN_VAZIO` |

## 15. Closure

```text
F_ok:
- dynamic-DE and interacting-DE are legitimate modern comparison classes;
- background degeneracy vs perturbation discrimination is established methodology;
- RLL now has an exact continuity residual and a concrete Q candidate at background level;
- local CPL sign is analytically computable.

F_gap:
- recipient sector for Q;
- covariant Q^mu;
- perturbations/stability;
- full Pantheon covariance route;
- common joint posterior;
- equivalence map between the two RLL formula families.

F_next:
choose physical semantics -> implement same-background adversarial pair ->
compute growth/f_sigma8 -> unify covariances/likelihood -> compare evidence -> preserve claim_allowed=false until replicated.
```
