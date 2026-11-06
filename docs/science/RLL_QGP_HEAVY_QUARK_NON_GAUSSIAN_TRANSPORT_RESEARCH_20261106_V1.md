# Heavy-quark non-Gaussian transport — scoped QGP research bridge (2026-11-06)

Status: **REFERENCE_ONLY / READY_TO_TEST**. Scientific promotion: **HOLD**. `claim_allowed=false`.

## External source and provenance

Jean F. Du Plessis and Bruno Scheihing-Hitschfeld, *Heavy Quark Transport Is Non-Gaussian beyond Leading Logarithm*, Physical Review Letters **137**, 192302 (5 November 2026), DOI: https://doi.org/10.1103/7fd5-1kq5 . MIT News (5 November 2026): https://news.mit.edu/2026/pinning-down-quark-gluon-plasma-structure-1105 .

The authors derive a **leading-order momentum-transfer kernel** for relativistic heavy quarks in a **weakly coupled non-Abelian plasma**, with asymmetric exponential tails in the longitudinal momentum-transfer distribution; they identify related structure in a strong-coupling holographic calculation. This is a theoretical calculation, **not a new experimental confirmation**.

## Existing RLL contract and boundary

- Producer and prior gate: [RLL_QCD_PRIMORDIAL_GATE.md](RLL_QCD_PRIMORDIAL_GATE.md), whose inputs concern QCD equation of state, primordial expansion and an explicitly separated RLL sector.
- Heavy-quark momentum-transfer distributions are **not** identical to the equilibrium equation of state, cosmological H(T), primordial curvature non-Gaussianity or ALICE/CMS flow observables.
- Do **not** inject a collider kernel into `epsilon_background_GeV_fm3`, double-count QCD radiation, or promote RLL versus LambdaCDM/CPL from this paper.
- The paper reports *exponential*, not inherently Lévy/Pareto power-law, tails. The RAFAELIA rare-event metaphor must not prescribe a physical distribution.

## Additive, reversible verification proposal

1. Pin the version-of-record DOI and available manuscript/supplement source; retain license and source checksum when bytes are retrieved. `source_pdf_sha256=TOKEN_VAZIO` until byte-level readback.
2. Reproduce a longitudinal transfer-kernel distribution in the authors' stated validity regime, with documented units, coupling, quark mass, temperature and numerical discretization. `authors_kernel_numeric_reproduced=TOKEN_VAZIO`.
3. Include a Gaussian matched-moment baseline plus a phenomenological asymmetric exponential reference. **Neither synthetic proxy is claimed to be the published kernel.**
4. Pre-register normalization, positivity, equilibrium/detailed-balance checks **when applicable to the derived kernel**, positive/negative log-tail slopes, skew, numerical convergence and independent held-out comparison. Preserve raw transfer increments before any IIR/T7/Q16 smoothing; characterize fixed-point quantization error separately.
5. Implement a freestanding test target only in an isolated subsequent code change; run same-target golden and adversarial fixtures. No changes to the existing QCD primordial gate in this proposal.
6. Permit a cosmological descendant only after an explicitly derived mapping from a justified microscopic transport input to a non-overlapping thermodynamic or cosmological observable, with comparison baseline and external uncertainty.

## Falsification / gates

- `H0`: Gaussian approximation adequately describes specified tails and equilibration over the pre-registered domain.
- `H1`: a reproduced non-Gaussian kernel provides demonstrable improvement there.
- Falsifiers: normalization failure; an invalid weak-coupling applicability claim; spurious Pareto tail attribution; equal-parameter Gaussian baseline mismatch; failure to reproduce cited primary-source figures; a cosmological impact asserted without a justified mapping.
- `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`; `IMPLEMENTED_UNTESTED != PASS`.
- Initial disposition: `REFERENCE_ONLY`, `PHYSICAL_EXECUTION=NOT_RUN`, `RLL_COSMOLOGICAL_IMPACT=TOKEN_VAZIO`, `claim_allowed=false`, `merge_allowed=false`.

## Federation pointers

Dispatcher: [START HERE Ω V2.2](https://docs.google.com/document/d/1T4OIN2RC1I-KFsdaQTCqieeZUGYBXissWrdrZMG0DN8/edit). Hot state: [CURRENT_STATE](https://docs.google.com/document/d/1d0J5SkF2S2emBq6jLuTkhYVaSOQiWazJWyRCTMJ-iRI/edit). Leader is a documented coordination role, implementation owner unresolved; operational SHARD002 is distinct from Google Drive `NOVOexport/` corpus shards. Append-only private evidence should be cataloged in `raf_private.omega_continuity_events_v1` with exact receipt readback; never place private conversation content, raw Drive IDs or credentials in this public file.

Rollback: close or abandon this draft branch without modifying `main`; preserve historical references and record a superseding correction instead of deletion.
