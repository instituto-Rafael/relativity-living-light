# Independent literature cross-check and mathematical referee-style note — RLL Ω
**Date:** 2026-11-14 · **Status:** INTERNAL_CRITICAL_REVIEW / NOT_EXTERNAL_PEER_REVIEW · **claim_allowed=false**  
**Parent:** [Critical DESI+Dovekie documentation review](RLL_DESI_DOVEKIE_CRITICAL_REVIEW_20261114.md).  
**Research services actually consulted:** SciSpace search/fetch, alphaXiv PDF page retrieval, GitHub original RLL source. An alphaXiv saved folder is a **bookmark library**, not a submission or endorsement.

## 1. Major scientific finding: calibration and evidence metrics are not interchangeable

[PRIMARY, alphaXiv arXiv:2511.07517, page 1] The DES-Dovekie reanalysis reports \`w0 = -0.803 ± 0.054\`, \`wa = -0.72 ± 0.21\` for its named DES-Dovekie+DESI DR2+CMB combination, a reported frequentist 3.2σ departure from a cosmological constant, and Bayesian odds ~5:1, **weak** in its own interpretation. This is a posterior in flat CPL; it is neither a directly observed \`wa\` nor a tested RLL forecast.

[PRIMARY, arXiv:2503.14738, page 3] DESI DR2 results describe BAO distances and a preference for flat CPL of 3.1σ on DESI DR2+CMB under a stated frequentist comparison, with 2.8–4.2σ across different supernova samples. This cannot be recast as a Bayesian posterior odds without a separate evidence calculation.

[INDEPENDENT METHODS, arXiv:2603.05472v1, pages 1 and 10] A Bayesian nested-sampling reanalysis using PolyChord compares ΛCDM and extensions. For **DESI DR2 + CamSpec (lensing) + DES-Dovekie**, table 3 gives \`ln B(CPL/ΛCDM) = -0.01 ± 0.27\`; for the corresponding **DES-SN5YR older calibration** it gives \`+3.32 ± 0.27\`. For **DESI DR2 + CamSpec (lensing) alone** it gives \`-0.57 ± 0.26\`. These likelihood names must be preserved: other Planck/CMB configurations have different Bayes factors.

**Provider discrepancy:** the SciSpace fetched abstract excerpt for arXiv:2603.05472 quoted \`ln B=-0.30±0.19\` for DES-Dovekie, while the retrieved arXiv v1 abstract and table 3 support \`-0.01±0.27\` for the specific CamSpec(lensing) triple. The primary-source page text takes precedence until version/likelihood equivalence is independently reconciled. Do not silently copy or average those figures.

[INDEPENDENT, peer-reviewed 2026; doi:10.1093/mnras/stag1607] Lozano Torres obtains approximately \`w0=-0.740±0.082,wa=-0.893±0.285\` in a declared joint DESI+DES BAO+SNe+Planck+chronometer analysis, with \`Δχ²≈-12\` but inconclusive \`ln B≈-0.5\` between CPL and ΛCDM. This is not the same likelihood as the DES collaboration combination.

[SECONDARY, arXiv/2026 publication indexed at SciSpace] Kandel et al., doi:10.1140/epjc/s10052-026-16010-6, report weakened dynamical dark-energy support with corrected DES-Dovekie vs DES-SN5YR. The Ekinci 2026 robustness item indexed by SciSpace explicitly describes itself as a *preprint, not peer reviewed*, despite provider metadata describing “Journal Article”; its status must be qualified.

**Conclusion at literature gate:** varying \`w0,wa\` across collaborators and data releases is important; "DES proves RLL" or "RLL's parameters were accurately predicted" is not evidenced. Models must be compared with matched likelihood, covariances, nuisance profiling and priors.

## 2. Mathematical falsification: two possible physical closures must not be conflated

[DOC, source] Canonical RLL:
\[
f(z) = [1+\exp((z-z_t)/w_t)]^{-1},\quad
g(a)=f(a)+(1-f(a))a^{-3},\quad a=(1+z)^{-1}.
\]
The documented additional density is \(\rho_s=\Omega_{s0}\rho_{c0}g\), with originally documented pressure \(p_{s,\mathrm{doc}}=-\Omega_{s0}\rho_{c0}f\).

[DERIVED, conservation test] With \(F=d f /d\ln a=(1+z)f(1-f)/w_t\),
\[
\mathcal C_{\mathrm{doc}}(a)=\frac{1}{\Omega_{s0}\rho_{c0}}
 \left(\frac{d\rho_s}{d\ln a}+3(\rho_s+p_{s,\mathrm{doc}})\right)
=F(1-a^{-3}).
\]
This is nonzero in the nontrivial transition for \(a\neq1\); \`SEPARATELY_CONSERVED_DOCUMENTED_PRESSURE=FAIL\`. It was already recognized in [the existing RLL mathematical audit](../science/RLL_MATH_LITERATURE_COHERENCE_AUDIT_20260808.md). Physical closure via interactions must balance the energy flux elsewhere.

[DERIVED, alternative A — not an implemented replacement] If \(\rho_s(a)\) is kept but is instead assumed **separately conserved**, define
\[
 p_{s,\mathrm{cons}}=-\rho_s-\frac13\frac{d\rho_s}{d\ln a}
 =\Omega_{s0}\rho_{c0}\left[-f+\frac{F}{3}(a^{-3}-1)\right].
\]
With \(\Omega_\Lambda\geq0,\Omega_{s0}\geq0,w_t>0\), \(G=\Omega_\Lambda+\Omega_{s0}>0\), and \(f_0=f(0)\), the local tangent CPL slope of the total conserved dark sector is:
\[
\boxed{
w_{a,\mathrm{cons}}=\frac{\Omega_{s0}(1-f_0)}{G^2}
 \left[\frac{2f_0G}{w_t}+3(\Omega_\Lambda+\Omega_{s0}f_0)\right]\geq0.
}
\]
The corresponding documented-pressure slope from [the RLL sign gate](../../data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json) is
\[
w_{a,\mathrm{doc}}=\frac{\Omega_{s0}(1-f_0)}{G^2}
 \left[\frac{f_0G}{w_t}+3(\Omega_\Lambda+\Omega_{s0}f_0)\right]\geq0.
\]
Thus, **merely replacing the pressure by the separately conserved closure does not reverse the local \(w_a\) sign under these assumptions.** This is a conditional algebraic inference, not a claim about fit preference under a full physical theory.

[LOCAL COMPUTATION, limited reproducibility] With \((\Omega_m,\Omega_{s0},z_t,w_t)=(0.315,0.059,1.164,0.405)\) and \(\Omega_\Lambda=1-\Omega_m-\Omega_{s0}=0.626\), an independent JavaScript arithmetic and central finite-difference check returned:
- \(f_0\simeq0.946549843975\),
- \(w_{0,\mathrm{eff}}\simeq-0.995396263934\),
- \(w_{a,\mathrm{doc}}\simeq+0.024507293327\) (numerical derivative \(+0.024507293356\)),
- \(w_{a,\mathrm{cons}}\simeq+0.035266961611\) (numerical derivative \(+0.035266961651\)),
- \(\mathcal C_{\mathrm{doc}}(z=0.5)\simeq-1.197312537\) and \(\mathcal C_{\mathrm{doc}}(z=1)\simeq-8.297169948\).

These are **model algebra only**, not numerical integration of DESI, Pantheon or DES-Dovekie likelihoods and not validation of the physical sector. No compiled CI was executed for this check.

[OPEN] For alternative B an interaction \(Q_s\) requires a covariant energy transfer with an equal/opposite term in a declared recipient stress-energy tensor and well-defined perturbations. **Neither closure A nor B automatically establishes a consistent Lagrangian or perturbation spectrum**. New dynamics must be versioned and compared to data as a new model rather than treated as a cosmetic documentation fix.

## 3. Technical reviewer checklist and acceptance gates

| Review aspect | State | Minimal falsifier / gate |
| --- | --- | --- |
| RLL original code and equations read | N0, source consulted | Exact function signature and parameter constraints |
| Source-paper calibration/likelihood detail | N0, arXiv PDF pages consulted | Nonmatching paper version or covariance convention |
| \(\mathcal C_{\rm doc}(a)\) | Algebraic derivation and numeric check | Symbolic derivative contradiction |
| \(\mathcal C_{\rm cons}(a)=0\) | By mathematical construction | Separate energy conservation with consistently recomputed pressure |
| Local \(w_{a,\mathrm{cons}}\ge0\) | Conditional derivation | Find counterexample within declared nonnegative domain |
| Model with complete covariant dynamics | N5, NOT_IMPLEMENTED_OR_PROVEN | Derive action, Bianchi/continuity, stable perturbations |
| Matched DESI+CMB+Pantheon/Dovekie \(\ln Z\) | N5, NOT_RUN in this review | Full official covariance/precision, priors, convergence |
| RLL forecast pair \((-0.809,-0.618)\) pre-registered in 2025 | N5, NOT_VERIFIED | Immutable dated equation, parameter values, pre-data freeze |
| External expert referee report | N5, NOT_RECEIVED | Reviewer identity, decision and review receipt |
| Publishability or scientific superiority | NOT_ESTABLISHED | Independent replication, same likelihood, predefined thresholds |

**Minimal next experiment:** preserve RLL original model, create a separately named \`RLL_CONSERVED_A_V1\` *proposal* with its rederived pressure and perturbations, add a symbolic/finite-difference continuity test, then independently fit \(\Lambda\)CDM, CPL, original RLL and closure A to the identical official likelihood using fixed data masks/covariance/priors. Do not merge or promote experimental claims without the existing project gates.

## 4. Exact bibliography / provenance

- DES Collaboration, Popovic et al., *DES-Dovekie reanalysis*, arXiv:2511.07517v3, page 1: https://arxiv.org/abs/2511.07517
- DESI Collaboration, Abdul Karim et al., *DESI DR2 Results II*, arXiv:2503.14738v3, page 3: https://arxiv.org/abs/2503.14738
- Ong, Yallup & Handley, *The Bayesian view of DESI DR2*, arXiv:2603.05472v1, pages 1, 7–10: https://arxiv.org/abs/2603.05472
- Lodha et al., *Extended Dark Energy analysis using DESI DR2 BAO measurements*, arXiv:2503.14743: https://arxiv.org/abs/2503.14743
- Lozano Torres, 2026, MNRAS, doi:10.1093/mnras/stag1607 (SciSpace record): https://scispace.com/papers/dynamical-dark-energy-from-desi-dr2-and-des-year-6-bao-byjmokux9qmp
- Kandel et al., 2026, *Revisiting evidence ... DES-Dovekie*, doi:10.1140/epjc/s10052-026-16010-6: https://scispace.com/papers/revisiting-the-evidence-for-dynamical-dark-energy-from-des-53ojvo428k9r

**Provider notes:** SciSpace returned paper abstracts, metadata and methodological comparisons; alphaXiv returned primary PDF page text. The associated papers were saved to an existing **private** RLL library folder; bibliography is not endorsement or publication.

**R3:** \(F_{\rm ok}\) = source-exact literature cross-check, independent bounded algebra check and both closures distinguished; \(F_{\rm gap}\) = proper covariant theory, observational joint fit, true external referee, claims; \(F_{\rm next}\) = controlled closure A variant and complete reproducible likelihood. \`claim_allowed=false\`.
