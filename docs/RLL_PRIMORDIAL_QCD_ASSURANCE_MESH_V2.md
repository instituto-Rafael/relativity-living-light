# RLL Primordial / QCD Assurance Mesh V2

**State:** `ASSURANCE_MESH_PARTIAL / claim_allowed=false / publication_effect=NONE`  
**Authority:** `instituto-Rafael/relativity-living-light`, base `rll/lab`  
**Branch:** `work/qcd-primordial-s-sector-20260826`  
**Parent:** `RLL_QCD_S_SECTOR_PRIMORDIAL_BOUND v1`

```text
VISÃO != ARTEFATO != EXECUÇÃO != EVIDÊNCIA != CLAIM
TOKEN_VAZIO != 0
NULL RESULT != MISSING RESULT
ACCESS LIMITED != CENSORSHIP
SUPERSEDED != DELETED
COLLIDER QGP != COSMOLOGICAL RLL LIKELIHOOD
```

## 1. Delta from V1

V1 established only the scoped s-sector result:

```text
DeltaH_s/H < 5.285178186e-11 at 130 MeV
state = PASS_LIMITED_DERIVED_BOUND
```

V2 adds executable QCD thermodynamics, radiation-like B/P compatibility envelopes, machine-readable evidence and attention registries, negative-result preservation, crossover/first-order separation, PMF/plasma/entropy/GW/PBH/axion branches, and explicit promotion gates.

Critical unresolved state remains:

```text
Omega_B0_sign_authority              = TOKEN_VAZIO
Omega_P0_sign_authority              = TOKEN_VAZIO
Omega_B0_P0_perturbation_physics     = TOKEN_VAZIO
full_SM_g_rho_g_s_numeric_ingestion  = TOKEN_VAZIO
post_rng_fix_MCMC_reference_receipt  = TOKEN_VAZIO
direct_RLL_early_universe_likelihood = TOKEN_VAZIO
FULL_RLL_PRIMORDIAL_VERDICT          = TOKEN_VAZIO
claim_allowed                        = false
```

## 2. Canonical RLL background

The canonical registry contains

```text
E2(a) = Omega_r a^-4 + Omega_m a^-3 + Omega_Lambda
      + Omega_s0[f(a)+(1-f(a))a^-3]
      + Omega_B0 a^-4 + Omega_P0 a^-4.
```

The nested null limit is

```text
Omega_s0=Omega_B0=Omega_P0=0 => LCDM background.
```

The validation matrix exposes `RLL_2_transition_plus_radiative_terms` with B/P as free parameters. Algebraic presence, however, does not establish sign, microphysics, perturbations or a posterior. The current structural implementation types `omega_s0` but does not establish an equivalent B/P domain contract, so separate B/P bounds remain blocked if signed cancellation is possible.

## 3. Thermal completion

A constant late-time `Omega_r a^-4` is not a precision time-temperature map across QCD. Thermal cosmology requires

```text
rho_rad(T) = (pi^2/30) g_rho(T) T^4
s(T)       = (2 pi^2/45) g_s(T) T^3
H^2(T)     = (8 pi G/3) rho_total(T)
a T g_s(T)^(1/3) = const   [adiabatic]
```

Therefore `CANONICAL_LOW_Z_BACKGROUND != THERMAL_PRIMORDIAL_COMPLETION`. Full-SM numerical `g_rho/g_s` remains a required ingestion step.

## 4. Executable HotQCD EoS

For `x=T/Tc`, `Tc=154 MeV`, V2 implements the published HotQCD pressure fit

```text
p/T^4 = 1/2[1+tanh(ct(x-t0))]
        (p_id+an/x+bn/x^2+cn/x^3+dn/x^4)
        /(1+ad/x+bd/x^2+cd/x^3+dd/x^4)
```

with `p_id=95*pi^2/180` and coefficients:

```text
ct=3.8706, t0=0.9761,
an=-8.7704, bn=3.9200, cn=0, dn=0.3419,
ad=-1.2600, bd=0.8425, cd=0, dd=-0.0475.
```

Derived identities:

```text
I/T^4       = T d(p/T^4)/dT
epsilon/T^4 = I/T^4 + 3p/T^4
s/T^3       = epsilon/T^4 + p/T^4
g_rho,QCD   = 30(epsilon/T^4)/pi^2
g_s,QCD     = 45(s/T^3)/(2pi^2)
```

Representative fit nodes show the expected soft region: `c_s^2 ~0.145` at 145-150 MeV, rising to about `0.30` at 400 MeV. The machine input stores selected published table values to test the fit against external anchors.

**Scope guard:** HotQCD 2+1-flavor QCD is not total cosmic Standard-Model `g_rho/g_s`; photons/leptons and charm completion are required, especially toward/above roughly 300 MeV.

## 5. Superseded result custody

The HotQCD accepted manuscript documents an incorrect fermion-normalization in preliminary pre-2014 HISQ/tree EoS analyses, which produced too-large trace anomaly below 300 MeV. V2 records those values as:

```text
SUPERSEDED_RESULT
active_numeric_use=false
```

not deletion and not censorship.

## 6. QCD transition contract

Physical-mass standard cosmic QCD at small chemical potential is routed as:

```text
STANDARD_COSMIC_QCD = CROSSOVER
```

Thus latent heat, bubble nucleation `beta/H`, wall speed and first-order bubble/sound-shell GW templates are not default Standard-Model QCD inputs. They remain `BSM_OR_NONSTANDARD_CONDITIONAL` unless an explicit RLL mechanism changes the transition order.

V2 also separates `GW_SOURCE_FIRST_ORDER` from `GW_TRANSFER_THROUGH_QCD_EOS`: a crossover can modify transfer of a pre-existing stochastic background through changing `g_*` without generating bubble GWs.

## 7. Radiation-like B/P mapping

Define

```text
Omega_X = Omega_B0 + Omega_P0
omega_X = Omega_X h^2.
```

For a positive homogeneous decoupled component with exact `a^-4` background scaling:

```text
rho_extra/rho_gamma = (7/8)(4/11)^(4/3) DeltaN_eff
alpha_Neff = 0.227107317660239
omega_X = alpha_Neff * DeltaN_eff * omega_gamma
omega_gamma = Omega_gamma h^2 ~= 2.4728e-5.
```

This is a **background-equivalence mapping**, not a direct RLL likelihood. `omega=Omega h^2` is kept primary to avoid injecting H0 degeneracy.

## 8. Observational compatibility envelopes

These use `mean+1.96 sigma` as reproducible Gaussian envelopes, not official positive-component one-sided re-fits.

```text
PDG BBN 2024:
Nnu=2.898+/-0.141
DeltaN_hi=0.13036
omega_X <~ 7.3209e-7
role=BACKGROUND_EXPANSION_PROXY

Planck+BAO 2018:
N_eff=2.99+/-0.17
omega_X <~ 1.5680e-6
role=FREE_STREAMING_RADIATION_PROXY

ACT DR6:
N_eff=2.86+/-0.13
omega_X <~ 3.9761e-7
role=FREE_STREAMING_RADIATION_PROXY

ACT DR6 + external BBN:
N_eff=2.89+/-0.11
omega_X <~ 3.4594e-7
role=HYBRID_COMPATIBILITY_PROXY
```

The ACT+BBN number is the tightest stored reference envelope but cannot become a direct B/P posterior until sign, perturbation and interaction physics are specified and fitted.

## 9. Historical RMR blueprint diagnostic

RMR blueprint metadata lists `Omega_B0,Omega_P0 in [1e-6,1e-5]`. At the simultaneous illustrative minimum:

```text
Omega_BP,min=2e-6
omega_BP,min=2e-6 h^2.
```

Against the ACT+BBN reference envelope:

```text
H0=50 -> 5.00e-7 -> 1.45 x envelope
H0=70 -> 9.80e-7 -> 2.83 x envelope
H0=90 -> 1.62e-6 -> 4.68 x envelope
threshold equality H0 ~= 41.59 km/s/Mpc.
```

Hence the illustrative simultaneous minimum lies above that proxy throughout the reference H0=50-90 interval. Correct status:

```text
BLUEPRINT_RANGE_DIAGNOSTIC = TENSION_UNDER_PROXY_MAPPING
RLL_FALSIFIED              = NO
```

because blueprint ranges are not authoritative fitted priors and the proxy is not a dedicated RLL likelihood.

## 10. BBN, collider QGP and claim separation

BBN probes radiation-era expansion around `T~1 MeV`, with `H ~ sqrt(g_* G_N)T^2`, through light-element abundances. Collider QGP probes microscopic strongly interacting matter:

```text
nuclear geometry -> eccentricity -> QGP response -> v2/v3.
```

Therefore:

```text
LHC_QGP != BBN != direct RLL evidence.
```

The “mini Big Bang” phrase remains metaphorical.

## 11. Magnetic-field completion

If `Omega_B0` is a physical primordial magnetic field, V2 requires at least:

```text
B_lambda, n_B, coherence scale, helicity, generation epoch,
damping history, rho_B convention, anisotropic stress,
scalar/vector/tensor perturbations, Faraday rotation,
ionization/heating effects.
```

A homogeneous scalar density alone cannot be mapped directly to PMF nG limits.

## 12. Plasma completion

If `Omega_P0` is actual plasma energy, define:

```text
species, masses, charges, temperature ratio, chemical potentials,
charge neutrality, EoS, opacity/coupling, photon/baryon/neutrino
interactions, entropy exchange, source/decay terms, sound speed/viscosity.
```

Otherwise it should be explicitly treated as a phenomenological radiation-like term rather than implied microphysics.

## 13. Entropy / decay branch

For production/decay/thermalization:

```text
dot(rho_i)+3H(rho_i+p_i)=Q_i
sum_i Q_i=0.
```

Possible consequences include `g_s(T)`, `T_nu/T_gamma`, baryon-to-photon ratio, BBN/CMB `N_eff`, sound/damping horizons, abundances and CMB spectral distortions. V2 therefore does not collapse all early-universe effects into one DeltaN_eff number.

## 14. PBH, GW and axion branches

QCD softening can alter PBH collapse thresholds for a supplied primordial spectrum, but PBH claims require `P_zeta(k)`, non-Gaussianity, collapse prescription, critical scaling, population evolution and selection likelihood. Current 2026 BSM-QCD PBH work is indexed as hypothesis evolution, not observation.

QCD topological susceptibility is retained as an orthogonal axion-cosmology branch. It does not become RLL evidence without an explicit RLL coupling/falsifier.

## 15. Negative/null results

Negative evidence is retained. ACT DR6 reports no significant preference in its tested models for extra free-streaming light species, self-interacting dark radiation, primordial magnetic fields, early dark energy or modified recombination, and no statistically significant departure from baseline LCDM.

```text
NEGATIVE_RESULT != ZERO_INFORMATION
NULL_RESULT     != TOKEN_VAZIO
```

## 16. Attention-state semantics

The machine ledger includes 26 states/items spanning:

```text
OBVIOUS_UNMATERIALIZED
OBVIOUS_BUT_EASY_TO_FORGET
FORGOTTEN_DEPENDENCY
IGNORED_BY_BACKGROUND_ONLY_MODEL
IGNORED_INFERENCE_RISK
DEVIATED_FROM_PHYSICAL_SPECIFICATION
SCOPE_GUARD
NEW_NUMERIC_INPUT
NEW_BRANCH
NEW_DERIVED_CONSEQUENCE
SUPERSEDED_RESULT
ABORTED_OR_INCOMPLETE_PIPELINE
NEGATIVE_RESULTS_MUST_BE_PRESERVED
ACCESS_LIMITED_NOT_CENSORSHIP
CLAIMED_CENSORSHIP_UNVERIFIED
OBVIOUS_BUT_CRITICAL
```

No current surveyed item is promoted to documented censorship. Promotion requires actor, specific suppression action, date, affected artifact, before/after evidence, provenance/hash and independent corroboration where feasible. Search failure, rejection, correction, supersession, paywall or omission do not satisfy that gate.

## 17. Assurance layers

```text
P0 MODEL AUTHORITY
P1 SOURCE CUSTODY
P2 THERMAL MICROPHYSICS
P3 BACKGROUND COSMOLOGY
P4 PERTURBATIONS
P5 OBSERVATIONAL LIKELIHOODS
P6 STATISTICS / CONVERGENCE
P7 CLAIM GATE / RECEIPT
```

No upper layer may manufacture a missing lower layer.

## 18. V2 artifacts

```text
data/inputs/qcd_primordial/hotqcd_2014_eos_fit.v1.json
data/inputs/qcd_primordial/rll_primordial_evidence_registry.v2.json
data/inputs/qcd_primordial/rll_primordial_attention_ledger.v1.json
data/results/rll_primordial_assurance_v2.receipt.json
tools/rll_primordial_assurance_v2.py
tests/test_rll_primordial_assurance_v2.py
docs/RLL_PRIMORDIAL_QCD_ASSURANCE_MESH_V2.md
```

## 19. Promotion gates

`G0` source integrity; `G1` full-SM thermal completion; `G2` B/P sign/microphysics; `G3` direct BBN/CMB RLL likelihood; `G4` post-RNG MCMC convergence with Rhat/tau/ESS/seed/data hashes; `G5` fair nested LCDM/comparator evaluation; `G6` claim promotion.

Until G0-G5 close:

```text
claim_allowed=false
```

## 20. Highest-value next path

```text
1. ingest Borsanyi full-SM g_rho/g_s supplementary data;
2. hash and thermodynamically validate it;
3. resolve authoritative B/P signs and physical semantics;
4. keep primary constraints in omega h^2;
5. implement PMF or plasma perturbations according to actual identity;
6. run direct BBN sensitivity;
7. add Boltzmann-compatible CMB perturbations;
8. recover/rerun post-RNG MCMC with convergence gates;
9. compare RLL_1, RLL_2 and LCDM under identical likelihoods;
10. only then issue a new model-selection receipt.
```

### R3

```text
F_ok  = V1 preserved + executable QCD EoS + observational proxy mesh
        + attention/supersession/censorship taxonomy + blueprint diagnostic
        + negative/null evidence preservation.
F_gap = full-SM g_rho/g_s + B/P sign/microphysics/perturbations
        + direct BBN/CMB RLL likelihood + post-RNG converged MCMC receipt.
F_next = full-SM thermal ingestion -> B/P semantic closure
         -> direct early-Universe likelihood -> converged model comparison.
```

**Full verdict:** `TOKEN_VAZIO`  
**Claim state:** `claim_allowed=false`
