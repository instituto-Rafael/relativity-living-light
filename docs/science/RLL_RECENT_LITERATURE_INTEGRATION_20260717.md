# RLL Recent Literature Integration Ledger — 2025–2026

**Verified:** 2026-07-17  
**Registry:** `data/registries/rll_recent_primary_sources_2026.json`  
**Rule:** a neighboring paper supplies a comparator or mechanism family; it does
not retroactively validate RLL.

## 1. Corrections to earlier narrow interpretations

### 1.1 Transitional dark energy is an active family

Generalized Emergent Dark Energy analyses using DESI DR2, CMB distance priors and
multiple supernova samples show that rapid late-time emergence is an active and
testable family. The exact RLL logistic density is not GEDE, but it belongs in the
same adversarial comparison space.

**RLL consequence:** compare shape, transition redshift, width, priors and
Bayesian evidence rather than claiming conceptual isolation.

### 1.2 Dissipation has a physical comparator

Recent DESI DR2 work models dark energy with bulk viscosity and interacting
dissipative sectors.

**Safe translation:**

\[
p_{\rm eff}=p-3H\xi
\]

**Unsafe translation:** calling an unspecified RLL coherence effect “photonic
viscosity” without a microscopic stress tensor, transport coefficient or
frequency-dependent prediction.

### 1.3 The transition may encode interaction

Interacting dark-sector analyses now include both background and perturbation
effects. A matter-like to dark-energy-like migration can be tested as a
\(Q\)-coupled system instead of being interpreted only as an effective equation
of state.

### 1.4 Density-dependent unified fluids are strong comparators

The Anton–Schmidt model tested with DESI DR2, Planck PR4 and multiple supernova
catalogues provides a current density-dependent/logarithmic competitor.

**RLL consequence:** the baseline tournament must extend beyond LambdaCDM and
CPL.

### 1.5 Photon–field–magnetic coupling is not unique as a concept

Cosmic birefringence and axion-photon conversion already provide physical
examples of photon coupling to fields in magnetic/polarization environments.

**Potentially original RLL content** must therefore be the exact coupling,
symmetry, scale dependence or observable—not the generic existence of a
photon-field relation.

### 1.6 FRB/plasma is an active observational route

FRB dispersion measures are increasingly used as probes of baryons, expansion,
\(H_0\), dark energy and the galaxy/plasma distribution.

**RLL gate:** a result must survive standard \(\nu^{-2}\) dispersion, Galactic,
host, halo and IGM models and produce a preregistered residual.

## 2. Dataset compatibility is now a first-class gate

Recent distance-crosscheck studies show that conclusions depend on:

- the supernova catalogue;
- calibration;
- reconstruction method;
- redshift bin;
- nuisance treatment;
- frequentist versus Bayesian reconstruction.

This does not prove that BAO and SNe are incompatible. It proves that joint
likelihoods must include a compatibility audit rather than silently multiplying
blocks.

Required diagnostics:

\[
\eta(z)=D_L/[(1+z)^2D_A]
\]

\[
F_{\rm AP}(z)=D_M/D_H
\]

The output must record:

```text
compatible
method_sensitive
calibration_sensitive
inconclusive
blocked
```

## 3. Updated adversarial model set

\[
\mathcal A_{\rm RLL}=
\{
\Lambda{\rm CDM},
w_0w_a,
{\rm GEDE},
{\rm Anton\! -\! Schmidt},
{\rm viscous},
{\rm interacting},
{\rm EFT/MG},
{\rm standard\ plasma},
{\rm axion/photon}
\}
\]

Not every model belongs in one likelihood. The set is partitioned:

- background expansion;
- perturbations/growth;
- propagation;
- polarization;
- structure formation.

## 4. Updated interpretation of current RLL constraints

The existing internal limit on \(\Omega_{s0}\) and the Bayes factor remain results
of their exact data, covariance, priors, code and likelihood.

Canonical notation:

\[
P(\Omega_{s0}\mid D,C,\Pi,M,L)
\]

where:

- \(D\): data selection;
- \(C\): covariance/systematics;
- \(\Pi\): priors;
- \(M\): physical implementation;
- \(L\): likelihood/reconstruction method.

Therefore:

```text
current implementation disfavored in current route
```

is allowed, while:

```text
all RLL mechanisms are physically excluded
```

is blocked.

## 5. Integration targets

| Target | Immediate action | Promotion gate |
|---|---|---|
| logistic background | canonical full-covariance posterior | convergence + prior robustness |
| distance compatibility | implement eta and F_AP reports | mock/null validation |
| interaction | define Q and perturbations | stability + baseline recovery |
| viscosity | define xi and units | thermodynamics + perturbations |
| EFT/MG | map background functions | covariant degrees of freedom |
| FRB | standard plasma residual pipeline | localized catalogue + null tests |
| magneto-optical | Faraday/instrument baseline | frequency and scale dependence |

## 6. Source boundary

The machine-readable registry records only safe uses. Abstract-level verification
is not a substitute for reproducing every numerical table. Before a numerical
value enters a fit, the repository must attach:

```text
primary source
table/equation identifier
version
download date
license/access
checksum
loader
validation test
```
