# RLL — 76-Operator Falsification Mesh from Three ChatGPT Interactions

**State:** `PROPOSED_NOT_EXECUTED / claim_allowed=false / publication_ready=false`

## Why this exists

The three preceding ChatGPT interactions are consumed as one **operational-evidence bundle**, not as training data. Interactions I1 and I2 contributed 76 adversarial operators; I3 contributed the custody/correction boundary.

The mesh does **not** claim that any operator result has passed. Its job is to prevent missing or attractive heuristics from silently becoming physical evidence.

## Gate order

1. address/covariance integrity;
2. out-of-sample prediction;
3. null simulations + multiple-testing control;
4. prior/posterior robustness;
5. inverse-response and identifiability;
6. orthogonal physics gates (growth, CMB/lensing, BBN/PMF);
7. independent reproduction.

## P0 subset

- `OP01` — Conditional residual / Schur complement
- `OP04` — LRG2 z=0.706 ablation
- `OP05` — LyA z=2.33 holdout
- `OP06` — Posterior PSIS-LOO/ELPD
- `OP09` — Injection/recovery
- `OP10` — Covariance-respecting null mocks
- `OP11` — Look-elsewhere accounting
- `OP12` — Multiple-testing/FDR
- `OP28` — Physical sign restriction
- `OP31` — Physical growth/fσ8
- `OP34` — B/P perturbation completion
- `OP37` — Blind analysis/preregistration
- `OP38` — Independent implementation/executor reproduction
- `OP42` — Frequentist coverage
- `OP46` — Posterior conditioned by block
- `OP50` — Savage-Dickey nested test
- `OP53` — Influence derivative
- `OP54` — Systematics Jacobian
- `OP59` — Inverse reconstruction of minimal δH(z)
- `OP60` — Functional derivative δχ²/δlnH(z)
- `OP61` — Observable response kernel
- `OP62` — Regularized inverse kernel
- `OP63` — dDM/dz=DH consistency
- `OP65` — Cumulative χ² vs z
- `OP70` — Address integrity vector↔covariance
- `OP73` — Contradiction tensor
- `OP76` — Prequential sequential model competition

## All 76 operators

- **OP01 [P0]** Conditional residual / Schur complement — state=`PROPOSED_NOT_EXECUTED`; falsifier: Conditional standardized residual remains anomalous after covariance conditioning.
- **OP02 [P1]** Block influence and leverage — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Block influence and leverage disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP03 [P2]** DM vs DH separation — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from DM vs DH separation disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP04 [P0]** LRG2 z=0.706 ablation — state=`PROPOSED_NOT_EXECUTED`; falsifier: Model preference disappears or reverses when LRG2 is withheld.
- **OP05 [P0]** LyA z=2.33 holdout — state=`PROPOSED_NOT_EXECUTED`; falsifier: RLL trained without LyA fails to predict the LyA block within predeclared predictive tolerance.
- **OP06 [P0]** Posterior PSIS-LOO/ELPD — state=`PROPOSED_NOT_EXECUTED`; falsifier: Out-of-sample ΔELPD does not favor the extension or is dominated by one block.
- **OP07 [P1]** Contiguous redshift K-fold — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Contiguous redshift K-fold disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP08 [P1]** Low-z↔high-z reversal — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Low-z↔high-z reversal disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP09 [P0]** Injection/recovery — state=`PROPOSED_NOT_EXECUTED`; falsifier: Null injections recover a false nonzero extension at unacceptable frequency.
- **OP10 [P0]** Covariance-respecting null mocks — state=`PROPOSED_NOT_EXECUTED`; falsifier: Observed Δχ² improvement is common under ΛCDM covariance mocks.
- **OP11 [P0]** Look-elsewhere accounting — state=`PROPOSED_NOT_EXECUTED`; falsifier: Global significance collapses after trial-factor accounting.
- **OP12 [P0]** Multiple-testing/FDR — state=`PROPOSED_NOT_EXECUTED`; falsifier: Discovery set does not survive declared multiplicity control.
- **OP13 [P1]** Posterior predictive checks — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Posterior predictive checks disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP14 [P1]** LOO-PIT calibration — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from LOO-PIT calibration disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP15 [P2]** Prior predictive checks — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Prior predictive checks disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP16 [P1]** Prior-width sensitivity — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Prior-width sensitivity disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP17 [P1]** Physics-derived priors — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Physics-derived priors disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP18 [P2]** Minimum description length — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Minimum description length disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP19 [P1]** Covariance whitening/Pythagorean residual geometry — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Covariance whitening/Pythagorean residual geometry disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP20 [P1]** Residual SVD — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Residual SVD disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP21 [P2]** Effective model rank — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Effective model rank disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP22 [P1]** Information geometry — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Information geometry disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP23 [P1]** Posterior manifold curvature/sloppiness — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Posterior manifold curvature/sloppiness disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP24 [P2]** Coordinate-transform invariance — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Coordinate-transform invariance disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP25 [P1]** Redshift wavelet localization — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Redshift wavelet localization disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP26 [P1]** Equal-complexity kernel swap — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Equal-complexity kernel swap disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP27 [P2]** Reparameterization invariance — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Reparameterization invariance disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP28 [P0]** Physical sign restriction — state=`PROPOSED_NOT_EXECUTED`; falsifier: Best fit requires parameter sign forbidden by the physical interpretation.
- **OP29 [P1]** Controlled sound-horizon r_d release — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Controlled sound-horizon r_d release disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP30 [P2]** Compressed vs full CMB likelihood — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Compressed vs full CMB likelihood disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP31 [P0]** Physical growth/fσ8 — state=`PROPOSED_NOT_EXECUTED`; falsifier: Background fit cannot reproduce growth with derived perturbation equations.
- **OP32 [P1]** Lensing/S8 cross-check — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Lensing/S8 cross-check disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP33 [P2]** SN compilation cross-check — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from SN compilation cross-check disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP34 [P0]** B/P perturbation completion — state=`PROPOSED_NOT_EXECUTED`; falsifier: Background-equivalent B/P term fails CMB/PMF/plasma perturbative observables.
- **OP35 [P1]** PMF parity + Faraday observables — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from PMF parity + Faraday observables disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP36 [P2]** BBN+CMB+spectral-distortion phase test — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from BBN+CMB+spectral-distortion phase test disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP37 [P0]** Blind analysis/preregistration — state=`PROPOSED_NOT_EXECUTED`; falsifier: Result changes materially when holdout/gates are frozen before analysis.
- **OP38 [P0]** Independent implementation/executor reproduction — state=`PROPOSED_NOT_EXECUTED`; falsifier: Independent implementation/executor cannot reproduce result within tolerance.
- **OP39 [P2]** Posterior topology — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Posterior topology disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP40 [P1]** HPD vs equal-tail intervals — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from HPD vs equal-tail intervals disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP41 [P1]** Profile vs marginal comparison — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Profile vs marginal comparison disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP42 [P0]** Frequentist coverage — state=`PROPOSED_NOT_EXECUTED`; falsifier: Nominal intervals fail empirical coverage under simulations.
- **OP43 [P1]** Posterior contraction — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Posterior contraction disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP44 [P1]** KL information gain — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from KL information gain disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP45 [P2]** Correlation-sign reversal — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Correlation-sign reversal disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP46 [P0]** Posterior conditioned by block — state=`PROPOSED_NOT_EXECUTED`; falsifier: Posterior feature disappears when one data block is removed.
- **OP47 [P1]** Predictive width vs redshift — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Predictive width vs redshift disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP48 [P2]** Prior-width scan — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Prior-width scan disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP49 [P1]** Prior-center scan — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Prior-center scan disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP50 [P0]** Savage-Dickey nested test — state=`PROPOSED_NOT_EXECUTED`; falsifier: Nested-model density ratio supports null once prior/posterior density is evaluated consistently.
- **OP51 [P2]** Evidence by two algorithms — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Evidence by two algorithms disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP52 [P1]** Reverse Bayes prior requirement — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Reverse Bayes prior requirement disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP53 [P0]** Influence derivative — state=`PROPOSED_NOT_EXECUTED`; falsifier: A single datum has disproportionate derivative influence on fitted parameters.
- **OP54 [P0]** Systematics Jacobian — state=`PROPOSED_NOT_EXECUTED`; falsifier: Small plausible systematic shifts move conclusions more than declared uncertainty.
- **OP55 [P1]** Posterior Hessian — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Posterior Hessian disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP56 [P1]** Stiff vs sloppy eigendirections — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Stiff vs sloppy eigendirections disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP57 [P2]** LCDM→RLL homotopy — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from LCDM→RLL homotopy disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP58 [P1]** Redshift-cut bifurcation — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Redshift-cut bifurcation disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP59 [P0]** Inverse reconstruction of minimal δH(z) — state=`PROPOSED_NOT_EXECUTED`; falsifier: Minimal reconstructed δH(z) is inconsistent with the assumed RLL functional form.
- **OP60 [P0]** Functional derivative δχ²/δlnH(z) — state=`PROPOSED_NOT_EXECUTED`; falsifier: Functional sensitivity localizes support outside the proposed transition region.
- **OP61 [P0]** Observable response kernel — state=`PROPOSED_NOT_EXECUTED`; falsifier: Response kernels show claimed datasets do not constrain the proposed region independently.
- **OP62 [P0]** Regularized inverse kernel — state=`PROPOSED_NOT_EXECUTED`; falsifier: Regularized inversion cannot recover a stable deformation across regularization choices.
- **OP63 [P0]** dDM/dz=DH consistency — state=`PROPOSED_NOT_EXECUTED`; falsifier: Reconstructed distances violate dDM/dz=DH consistency beyond propagated uncertainty.
- **OP64 [P1]** Antiderivative cumulative sensitivity — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Antiderivative cumulative sensitivity disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP65 [P0]** Cumulative χ² vs z — state=`PROPOSED_NOT_EXECUTED`; falsifier: Cumulative χ² preference appears only after one narrow redshift block.
- **OP66 [P2]** Cancellation index — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Cancellation index disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP67 [P1]** Physical inequalities/stability — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Physical inequalities/stability disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP68 [P1]** Change-point inference — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Change-point inference disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP69 [P2]** Rebinning invariance — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Rebinning invariance disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP70 [P0]** Address integrity vector↔covariance — state=`PROPOSED_NOT_EXECUTED`; falsifier: Any row/column/tracer address mismatch invalidates the likelihood result.
- **OP71 [P1]** Covariance-preserving permutation — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Covariance-preserving permutation disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP72 [P2]** Observable dependency graph — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Observable dependency graph disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP73 [P0]** Contradiction tensor — state=`PROPOSED_NOT_EXECUTED`; falsifier: Contradiction localizes to method/source axis rather than physical-model axis.
- **OP74 [P1]** Four-state evidence logic — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Four-state evidence logic disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP75 [P2]** Causal clustering of failures — state=`PROPOSED_NOT_EXECUTED`; falsifier: The claimed advantage from Causal clustering of failures disappears, reverses, or becomes statistically/physically non-identifiable under the declared control.
- **OP76 [P0]** Prequential sequential model competition — state=`PROPOSED_NOT_EXECUTED`; falsifier: Sequential predictive score does not improve when new blocks arrive.

## Typed gaps

- `TOKEN_VAZIO_OP_EXECUTION_RECEIPTS` = `NOT_EXECUTED`; close when: Run operators and bind exact-head receipts.
- `TOKEN_VAZIO_PSI_ELPD_RLL` = `NOT_EXECUTED`; close when: Run posterior leave-redshift-block-out/PSIS-LOO or equivalent ELPD.
- `TOKEN_VAZIO_DESI_LYA_FULL_SHAPE` = `NOT_EXECUTED`; close when: Bind non-overlapping DESI Lyα full-shape/AP likelihood.
- `TOKEN_VAZIO_RLL_GROWTH_PERTURBATIONS` = `MISSING_MODEL`; close when: Derive perturbation/growth model before fσ8.
- `TOKEN_VAZIO_RLL_BAYES_EVIDENCE` = `NOT_EXECUTED`; close when: Define physical priors and compute lnZ with algorithm cross-check.
- `TOKEN_VAZIO_PMF_PERTURBATIVE_LIKELIHOOD` = `MISSING_LIKELIHOOD`; close when: Bind PMF amplitude/spectrum/helicity/Faraday/CMB perturbation likelihood.
- `TOKEN_VAZIO_INDEPENDENT_REPRODUCTION_76_MESH` = `MISSING_REPRODUCTION`; close when: Independent implementation executes the promoted P0 subset.

## Non-compensation rule

```text
P1/P2 PASS != closure of P0
PROPOSED_NOT_EXECUTED != PASS
TOKEN_VAZIO != 0
BETTER_CHI2 != BETTER_MODEL
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
```

## R3

**F_ok:** 76 operators are now uniquely addressed, prioritized, provenance-bound and falsifier-bound.

**F_gap:** execution receipts, Lyα full-shape, physical growth, Bayesian evidence, PMF perturbative likelihood and independent reproduction remain typed.

**F_next:** execute the smallest P0 sequence that maximizes uncertainty reduction: OP70 → OP01/OP04/OP05 → OP06 → OP09/OP10/OP11/OP12 → OP59/OP60/OP61/OP62/OP63 → OP31/OP34 → OP38/OP76.
