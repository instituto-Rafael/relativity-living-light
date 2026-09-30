# RLL Late-Time Cascade Observable Projection V1

Status: `SHADOW_HYPOTHESIS / EVIDENCE_GATED / claim_allowed=false`

## Purpose

This successor connects the already merged gravitational reverberation + threshold-cascade laboratory to cosmological **observables** without inserting an unearned homogeneous density term into the RLL/ΛCDM background.

The route is intentionally:

```text
local/compact source hypothesis
  -> causal reverberation / threshold network
  -> phenomenological late-time perturbation template
  -> P(k,z), BAO wiggle damping coordinate, peculiar-velocity redshift coordinate
  -> existing DESI/Pantheon/CMB comparison infrastructure
```

and not:

```text
stellar collision -> new Omega term -> H(z) claim
```

## Parent evidence

The parent strong-gravity layer was merged to `rll/lab` by PR #839 after exact-head provider workflows, including Python tests, completed successfully. Its central unresolved bridge remains:

```text
strain-like gravitational response != Joule-valued trigger energy
strain_to_trigger_energy = TOKEN_VAZIO
```

This successor does not close that gap by assumption.

## Observable coordinates

### 1. Dimensionless late-time transfer

For externally supplied baseline power `P_base(k,z)`:

```text
T_c(k,z) = A_c exp[-(k/k_d)^2] [(1+z)/(1+z_ref)]^beta
P_shadow(k,z) = P_base(k,z) [1 + T_c(k,z)]
```

`A_c`, `k_d`, `beta` are phenomenological nuisance/template coordinates. They are not derived source parameters.

The null is exact:

```text
A_c = 0  =>  P_shadow = P_base
```

Therefore ΛCDM/wCDM/CPL/RLL baselines can be compared without changing their background equations.

### 2. BAO existing-wiggle damping coordinate

```text
O_bao,shadow(k) = O_bao,base(k) exp[-(k Sigma_c)^2/2]
```

This can only damp/broaden an already supplied BAO oscillatory component. It **does not generate the primordial BAO standard ruler** and is not evidence that late-time stellar/compact-object cascades caused BAO.

### 3. Peculiar-velocity redshift coordinate

For a bounded non-relativistic line-of-sight peculiar velocity:

```text
z_obs ~= z_cos + (1+z_cos) v_parallel/c
```

V1 stops at the redshift coordinate. A source-specific Pantheon+ magnitude/covariance likelihood remains a separate bridge.

## Why peculiar velocity is the preferred first transverse bridge

Recent observational work gives an immediately falsifiable route: SN Ia magnitudes carry correlations from peculiar velocities sourced by large-scale structure, and those correlations can be combined with CMB information to constrain growth/curvature. This is structurally closer to the proposed late-time cascade question than modifying the homogeneous expansion by declaration.

Reference:
- C. Crisman, M. Quartin, J. Rebouças, *Joint curvature and growth rate measurements with supernova peculiar velocities and the CMB*, Physics of the Dark Universe 53 (2026) 102391, DOI `10.1016/j.dark.2026.102391`.

## Why BAO is a control, not an origin claim

DESI DR2 validation explicitly models nonlinear broadening of the BAO feature using synthetic datasets/mocks. Any RLL cascade-related BAO template must therefore compete with ordinary nonlinear evolution, reconstruction, redshift errors and survey systematics before receiving physical interpretation.

Reference:
- L. Casas et al. (DESI Collaboration), *Validation of the DESI DR2 BAO analysis using synthetic datasets*, Phys. Rev. D 113, 023520 (2026), DOI `10.1103/fvgh-kswf`.

## Strong-gravity reverberation literature boundary

Gravitational memory/ringdown are legitimate strong-field waveform phenomena, but their existence does not supply the missing local trigger-energy bridge for a cosmic cascade.

References:
- *Gravitational memory from hairy binary black hole mergers*, Phys. Rev. D 114, 044094 (2026), DOI `10.1103/6sry-t38l`.
- *Quasinormal mode ringing of binary black hole mergers in scalar-Gauss-Bonnet gravity*, Phys. Rev. D 113, 044041 (2026), DOI `10.1103/dtd2-5vlg`.

## Contemporary comparator boundary

DESI DR2 + Pantheon+ + CMB combinations are actively used to constrain interacting/dynamical dark-sector models. Those publications demonstrate a comparison methodology, not support for the RLL cascade hypothesis.

Reference:
- *The linear and non-linear dark sector interactions: A cosmological study with DESI DR2 BAO*, Journal of High Energy Astrophysics 53 (2026) 100634, DOI `10.1016/j.jheap.2026.100634`.

## Required nulls / adversarial controls

1. `A_c = 0` must recover the exact externally supplied baseline point-by-point.
2. `Sigma_c = 0` must preserve the existing BAO wiggle.
3. Ordinary nonlinear BAO damping must be compared before a cascade interpretation.
4. Standard peculiar-velocity covariance/growth must be compared before a cascade interpretation.
5. ΛCDM, wCDM/CPL and the existing RLL background are controls, not enemies.
6. No extra background energy density may be added unless a covariant/population coarse-graining derivation independently supports it.
7. No stellar-collision rate, compact-object rate or GW strain may be mapped to `A_c` without an explicit source-specific derivation and energy budget.

## TOKEN_VAZIO

```text
strain_to_trigger_energy
stellar_collision_population_to_template_amplitude
compact_object_population_to_template_amplitude
cascade_template_to_pantheon_covariance_likelihood
cascade_template_to_desi_full_likelihood
cascade_template_to_cmb_lensing_isw
independent_observational_replication
```

## Relation to the frontier ladder

This is a successor to the existing strong-gravity/plasma -> cosmology bridge classified in the governed frontier program as a low-maturity bridge candidate. Executability of this shadow adapter raises implementation specificity; it does **not** raise scientific truth or empirical maturity by itself.

## Falsification path

```text
A_c = 0 preferred after complexity penalty
  -> no evidence for this template

A_c != 0 in one dataset but absorbed by standard systematics
  -> no cascade evidence

cross-dataset residual survives standard nonlinear / velocity / lensing controls
  -> source bridge still required

source bridge derived + independent reproduction
  -> only then consider promotion beyond SHADOW_HYPOTHESIS
```

## Invariants

```text
SOURCE != TEMPLATE != OBSERVABLE != LIKELIHOOD != EVIDENCE != CLAIM
BAO_MODULATION != BAO_ORIGIN
PECULIAR_VELOCITY_COORDINATE != PANTHEON_LIKELIHOOD
GW_MEMORY != LOCAL_TRIGGER_ENERGY
EXECUTABLE_SHADOW != PHYSICAL_VALIDATION
TOKEN_VAZIO != 0
claim_allowed=false
```
