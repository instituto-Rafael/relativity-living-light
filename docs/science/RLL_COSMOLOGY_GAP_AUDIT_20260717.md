# RLL Cosmology Gap Audit — 2026-07-17

**Question:** Is the proposed list of missing cosmology layers worth preserving?  
**Verdict:** **yes, after correction**. It is valuable as a physical-completion backlog, but inaccurate as a current-state report because several statistical gaps were already closed or partially closed.

## 1. Evidence hierarchy

Statuses used here:

- `CLOSED` — executable path and result artifact exist;
- `PARTIAL` — an implementation exists but lacks complete covariance, convergence, backend parity, or physical closure;
- `MISSING` — no executable scientific implementation was located;
- `REFERENCE_ONLY` — present in text but not as a reproducible calculation;
- `TOKEN_VAZIO` — required evidence has not been demonstrated.

## 2. Statistical validation — corrected

| Proposed statement | Current verdict | Repository evidence | Remaining work |
|---|---|---|---|
| “No joint H(z)+BAO+fσ8+CMB analysis” | **OUTDATED** | `data/pipelines/structure_d/joint_real_likelihood.py` fits a joint vector; `scripts/rll_fase20_mcmc_bayes.py` performs a five-dataset MCMC/nested run including SNe | consolidate a single canonical route and prevent divergent dataset definitions |
| “Only diagonal BAO covariance” | **OUTDATED/PARTIAL** | `data/real/desi_dr2_bao_covariance.csv` is consumed as official full covariance in the joint optimizer; FASE 20 separately uses per-tracer 2×2 correlations | make the full covariance route the one used by the canonical MCMC/nested sampler |
| “No MCMC chain” | **OUTDATED** | FASE 20 runs `emcee` 32×1500 and `dynesty` with `nlive=150` | chain length is below the preferred autocorrelation criterion; rerun with convergence target and prior-sensitivity study |
| “χ²/AIC only” | **OUTDATED** | AIC/AICc/BIC plus a formal Bayes factor are present | regenerate all reports from one canonical likelihood and verify independent reproduction |
| “Complete publication-grade statistics” | **NOT YET** | current artifacts themselves preserve `claim_allowed=false` and convergence/prior limitations | full Pantheon+ covariance in the same sampler, robust convergence, prior robustness, systematic variants and external replication |

### Important route mismatch

The repository currently contains at least two scientifically relevant routes:

1. `joint_real_likelihood.py`: full DESI matrix, H(z), fσ8 proxy and compressed CMB; no Pantheon+ in that result.
2. `rll_fase20_mcmc_bayes.py`: MCMC/nested over H(z), historical BAO, DESI, Pantheon+ and compressed CMB, but Pantheon+ uses diagonal errors and DESI uses tracer-block correlations rather than the committed full 13×13 matrix.

Therefore the remaining P0 is not “invent a joint analysis”; it is **unify the strongest components into one canonical posterior pipeline**.

## 3. Physical mechanisms

| Proposed gap | Verdict | Precise correction |
|---|---|---|
| inflation / primordial perturbations | **MISSING executable mechanism** | no generated primordial spectrum or inflationary dynamics were located; this blocks full early-Universe claims, not late-time phenomenological testing by itself |
| particle nature of dark matter | **MISSING microphysical closure** | RLL fits a matter sector and `Omega_s0`; it does not identify `Omega_s0` as CDM nor provide a particle model |
| origin of dark energy | **MISSING fundamental derivation** | a phenomenological background term may still be tested, but cannot be advertised as deriving vacuum energy or a field theory |
| stress-energy tensor/effective fluid | **PARTIAL/MISSING closure** | the model needs density, pressure, continuity, sound speed, anisotropic stress and stability conditions for its added sector |

## 4. Geometry and relativity

The statement “RLL does not use FLRW” is too strong.

The repository implements Friedmann-background relations, FLRW distance measures and curvature-aware `D_M` utilities. What remains missing is the stronger object:

\[
S[g,\phi,\ldots]\rightarrow G_{\mu\nu}=8\pi G\,T_{\mu\nu}^{\mathrm{total}}
\rightarrow \text{background}+\text{perturbations}.
\]

Correct status:

- FLRW operational background: `PARTIAL/IMPLEMENTED`;
- explicit cosmological-principle assumption: should become a formal contract;
- covariant derivation from GR, modified gravity or EFT: `MISSING`;
- proof of conservation and stability: `MISSING`.

## 5. High-precision cosmology

| Layer | Current status | Correction |
|---|---|---|
| BBN | `PARTIAL` | FASE 20 uses a Gaussian `Omega_b h²` prior; it does not calculate H/He/Li abundances or alter a BBN network |
| CMB | `PARTIAL` | compressed distance priors and covariance exist; no `C_ell^{TT}`, `TE`, `EE`, lensing spectrum or recombination/Boltzmann evolution |
| linear growth | `PARTIAL` | `D+(z)`, `S8` and `fσ8` helpers/proxies exist; canonical joint route still lacks CLASS/CAMB benchmark parity |
| nonlinear structure | `MISSING` | no validated nonlinear power spectrum, halo model or N-body implementation for the RLL sector |
| Pantheon+ | `PARTIAL` | loader and FASE 20 data path exist; canonical full STAT+SYS covariance is not unified with the MCMC/nested route |

CAMB/CLASS-level integration matters because these solvers evolve perturbations into CMB and matter power spectra; a new physical sector must specify how it enters background and perturbation equations before backend parity is meaningful.

## 6. Observational tensions

| Tension | Status | Safe language |
|---|---|---|
| H0 | `PARTIAL` | RLL has fitted H0 values and comparison text, but no canonical SH0ES likelihood and no demonstrated alleviation mechanism |
| S8/sigma8 | `PARTIAL` | S8 and growth proxies exist, but no versioned weak-lensing likelihood measuring the tension in sigma |

A fitted H0 near one measurement is not a mechanism. A tension claim requires the same model, likelihoods, nuisance treatment and covariance on both local and early-Universe data.

## 7. Roadmap domains

The proposed domains are real and worth preserving because they already exist in `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`:

- `C01`: `f(z) ↔ w(z)` with DESI DR2 + Pantheon+ + Planck;
- `C03`: core→cusp / halo structure;
- `C05`: H0 tension;
- `C07`: alternative gravity;
- `C09`: photon/plasma dispersion with CHIME/FRB.

They must not share one claim gate. Each domain needs its own:

```text
claim → equation → dataset → covariance → baseline → falsifier → result → allowed language
```

## 8. Priority surgery

### P0 — statistical integrity

1. create one canonical joint posterior route;
2. use full DESI covariance and full Pantheon+ STAT+SYS covariance in that same route;
3. require `N/tau >= 50` or an explicitly justified convergence rule;
4. rerun prior sensitivity for `Omega_s0`, `z_t` and `w_t`;
5. derive interpretation labels from metrics, never hard-code them;
6. version command, environment, seeds, hashes and outputs.

### P1 — physical closure

1. define whether the RLL sector is an effective fluid, field, modified gravity term or propagation effect;
2. derive `rho_s(a)`, `p_s(a)`, `w_s(a)` and the continuity equation;
3. specify sound speed, perturbations, anisotropic stress and stability;
4. state the cosmological principle and FLRW assumptions explicitly;
5. prove the standard-model limit when `Omega_s0 → 0`.

### P2 — precision backends

1. implement/patch CLASS or CAMB only after the perturbation equations are closed;
2. generate CMB and matter power spectra;
3. benchmark ΛCDM recovery before enabling RLL;
4. add lensing/RSD likelihoods and nonlinear-systematics gates.

### P3 — extended research

- inflationary completion;
- BBN abundance calculation;
- nonlinear/N-body halo tests;
- H0 and S8 tension likelihoods;
- CHIME/FRB plasma propagation;
- Euclid/Rubin adapters when public products and covariance are appropriate.

## 9. Final assessment

The submitted text is worth keeping as a **corrected roadmap**, not as a statement that the repository lacks every listed capability.

Canonical summary:

\[
\mathrm{RLL}_{2026-07-17}=
\mathrm{background\ phenomenology}_{\checkmark}
\oplus
\mathrm{joint\ Bayesian\ testing}_{\mathrm{partial}}
\oplus
\mathrm{covariant\ microphysics}_{\varnothing}
\oplus
\mathrm{Boltzmann/Nbody\ parity}_{\varnothing}.
\]

- `F_ok`: the project already crossed the threshold from simple χ² smoke testing to real Bayesian confrontation.
- `F_gap`: its strongest statistical pieces are split across routes, while physical closure remains incomplete.
- `F_next`: unify the posterior pipeline first; then derive the effective physical sector before attempting CMB/N-body expansion.

`claim_allowed=false` remains the correct state for claims of new cosmological physics.
