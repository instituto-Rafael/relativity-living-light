# SGPT M87* Fire Test V1

> **Canonical navigation:** start at `docs/strong_gravity/START_HERE_SGPT_M87.md`. It routes humans and AI agents through preregistration -> regime admissibility -> timescales -> data custody -> statistics -> reproducibility -> claim ladder -> execution/receipts. Do not bypass unresolved locks.

**Status:** `PREREGISTERED_UNEXECUTED`  
**Parent:** `B08_SGPT_V1` on `rll/lab@e287ef13be4d5e6d366f29e234c8a5d113d21729`  
**Claim:** `claim_allowed=false`

## Objective

Turn the SGPT discussion into one source-specific, falsifiable external-data test without relabelling already-public EHT results as a prospective discovery.

The target is **M87*** because the EHT has public calibrated 2017 M87 data, public polarimetric products, a contemporaneous multi-wavelength product, a public imaging-pipeline repository, and a later calibrated 2018 M87 release that can be frozen as a repository-local retrospective holdout.

This protocol does **not** assert that those products are sufficient to validate SGPT. It freezes what must be known before any result-producing fit.

## Canonical contract

`data/contracts/sgpt_m87_firetest.v1.json`

The contract pins:

- RLL SGPT parent commit;
- M87* as the object;
- official EHT product identifiers/DOIs;
- the public EHT imaging-pipeline commit;
- three SGPT hypotheses;
- five mandatory physical baselines;
- seven negative controls;
- the retrospective development/holdout split;
- the claim and rights boundaries.

## Data roles

- `EHT_2017_L1` — raw/calibration custody reference only until exact bytes are acquired and hashed.
- `EHT_2019_D01_01` — primary calibrated 2017 M87 product.
- `EHT_2019_D01_02` — public imaging-pipeline reference, pinned by commit.
- `EHT_2021_D02_01` — contemporaneous 2017 multi-wavelength context.
- `EHT_2023_D01_01` — calibrated 2017 polarimetric product.
- `EHT_2024_D01_01` — calibrated 2018 M87 product reserved here as a **retrospective analysis holdout**, not a prospective blind prediction.

Public accessibility or a DOI does not prove redistribution or ML-training rights. Exact terms and file-level SHA-256 values remain `TOKEN_VAZIO` until acquired and verified.

## Hypotheses under fire

### H_down

```text
H_down = max(0,-Theta) * tau_flow * M_f
         * p_ram/(p_th + p_B + p_rad)
```

It survives only if it adds robust out-of-sample predictive information beyond standard GRMHD/GRRT predictors and the same gain is not reproduced by drop-term, sign-flip or shuffled controls.

### H_logistic_photonic

```text
f_gamma(chi) = 1/(1 + exp((chi-chi_t)/w_chi))
```

It survives only if the frozen logistic transition outperforms or adds justified predictive value beyond physically motivated transition models after uncertainty and complexity penalties.

### H_temporal_ordering

```text
compression -> hardening -> polarization change -> flare/outflow
```

This remains `TOKEN_VAZIO_NOT_RUN`. No lag analysis is allowed until an adequate time-resolved data product, cadence, primary variables and uncertainty model are frozen.

## Mandatory baselines

1. ideal GRMHD;
2. resistive GRMHD;
3. two-temperature GRRMHD;
4. GRPIC;
5. general-relativistic radiative transfer.

A baseline may not be silently omitted because it performs better. If a baseline is physically inapplicable, the justification must be recorded before the corresponding result is inspected.

## Predeclared negative controls

1. drop `Theta`;
2. drop `M_f`;
3. drop `R_ram`;
4. flip the sign of `Theta`;
5. shuffle predictor variables;
6. permute temporal targets;
7. baseline only.

A test suite that cannot reject deliberately wrong variants is not a strong falsifier.

## What remains deliberately unknown

```text
M, a_star, dot_M, B, rho, T_e = TOKEN_VAZIO
file SHA-256                    = TOKEN_VAZIO
exact primary observable vector = TOKEN_VAZIO
covariance model                = TOKEN_VAZIO
likelihood                      = TOKEN_VAZIO
primary model-comparison metric = TOKEN_VAZIO
complexity penalty              = TOKEN_VAZIO
G0..G7                          = TOKEN_VAZIO
scientific validation           = TOKEN_VAZIO
```

These are not missing documentation to be filled from memory. They are gates whose values require specific source/evidence bindings.

## Gate ladder

```text
G0 identity
 -> G1 mathematics
 -> G2 determinism
 -> G3 adversarial controls
 -> G4 mandatory physical baselines
 -> G5 independent reproduction
 -> G6 held-out prediction
 -> G7 explicit human-authorized claim promotion
```

Passing the preregistration workflow means only that this design remains internally fail-closed. It is not G4, G5, G6 or G7.

## Validator

```bash
python3 tools/validate_sgpt_m87_firetest.py --selftest
python3 tools/validate_sgpt_m87_execution_locks.py --selftest
python3 -m unittest -v tests.strong_gravity.test_sgpt_m87_firetest
```

The preregistration selftest rejects attempts to invent source mass, file hashes, remove GRPIC, remove a negative control, pre-run the temporal hypothesis, invent covariance, preselect a model metric, mark G4 PASS, promote a claim, or pretend the holdout was executed.

The execution-lock selftest rejects attempts to invent source-regime applicability, process rates, custody hashes/rights, statistical choices, independent reproduction or a direct jump from software success to a new-physics claim.

## Next admissible mutation

The next scientific delta is **data custody**, not hypothesis promotion:

```text
official bytes
 -> exact source locator/version
 -> SHA-256
 -> rights/terms record
 -> immutable local manifest
 -> only then freeze primary observable/covariance/likelihood
```

Before any dense/nuclear/spin-QED process is enabled, `source_regime_admissibility.v1.json` must establish source-domain applicability. Before any process is timed, `process_timescale_registry.v1.json` must bind a physical rate model, units, source and domain.

After the first result-producing execution, this V1 protocol must not be rewritten to fit the result. Corrections require a successor protocol preserving this lock.

R3 = <F_ok: source, baselines, negative controls, six pre-execution locks and non-promotion rules frozen; F_gap: bytes, hashes, rights, source-regime evidence, process rates, priors, covariance, likelihood and G0-G7 scientific evidence are absent; F_next: validate locks, acquire official M87 products with custody hashes and terms, then freeze the exact primary likelihood before fitting.>
