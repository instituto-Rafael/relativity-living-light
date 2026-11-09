# RLL Ω — Obvious / Neglected from atoms to cosmos (2026-11-08)

**Status:** additive research atlas, `CATALOG_ONLY_UNTESTED_RLL`, `claim_allowed=false`. This is a literature-to-falsifier map, not a cosmological or stellar fit. SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.

## Intent / parent

Parent authority (do not replace): `data/governance/RLL_CROSS_SCALE_EVIDENCE_GRAPH_20261028.json` with 8 existing nodes and 11 typed edges, including atom-to-spectral forest/recombination-to-BAO physics, and explicit analogy-only connections for Rydberg effects. Also preserve `data/science/perturbations/RLL_PERTURBATION_CLOSURE_CONTRACT_20260808_V1.json`, the nine slots C01-C09, and `docs/research/RLL_COSMOLOGY_MODEL_COMPARATOR_AUDIT_20261108.md`. This addendum contains **13 new typed records, 13 links to the parent nodes and 13 modern sources**. All physical bridges from nuclear stars or biology into the RLL cosmological sector remain unproven.

## Findings — what may be obvious, neglected or improperly conflated

| ID | Priority | What could be missed | Specific falsifier / boundary |
|---|---|---|---|
| NG01 | P0 | DESI Ly-alpha full-shape AP at z=2.33 overlaps BAO data | Never add new AP points as independent BAO without full joint covariance and released-product binding |
| NG02 | P0 | The dark-energy fit may be driven by a small subset of correlated BAO LRG tracers | Conditional, covariance-preserving tracer and redshift-block holdouts |
| NG03 | P0 | Calibration, host-galaxy systematics and z cuts in supernova compilation can mimic changes in evolving energy | Refit under separate Pantheon+, DES-SN5YR, Dovekie calibrations with identical nuisance handling |
| NG04 | P1 | Cosmic transparency assumption and distance duality D_L=(1+z)^2 D_A | Opacity and selection ablation under correct observational likelihood |
| NG05 | P0 | Non-cold dark matter pressure might be misattributed to evolving DE | Matched wDM vs CPL/RLL fit with physical DM perturbation closure |
| NG06 | P1 | An *apparent* phantom crossing may reflect interacting dark-sector model, not fundamental phantom field | Q_mu and conservation/perturbation closure before inferring crossing physics |
| NG07 | P0 | High-density nuclear P(epsilon) for TOV star is **not** cosmic P_DE or RLL Omega_s0 | Missing dimensioned covariance/stress-energy map; cannot inject NS EOS parameter into RLL without mechanism |
| NG08 | P1 | Dark cores inside neutron stars are hypothetical and may be degenerate with baryonic EOS | Mass-radius alone cannot identify dark sector without independent probes |
| NG09 | P0 | Giant star radius does not imply black-hole compactness | Use C=GM/(Rc²), cgs/SI unit correctness and GR assumptions |
| NG10 | P0 | Proton local QCD stress is not stellar isotropic bulk pressure | Thermodynamic/statistical EOS needed; same word *pressure* != same observable |
| NG11 | P0 | At Omega_s0=0, transition z_t and width w_t can become unidentifiable | Prior-sensitivity, zero-limit and G6 H52 nested stability diagnostics |
| NG12 | P2 | Biochemical electron/proton gradient is valid physiology, not cosmic gravity | Keep semantic analogy not causal physics |
| NG13 | P1 | 50,000 IU is not an SI amount of mass | IU conversion is substance-specific; no IU-to-kg universal map |

## Concrete equations / dimensional tests

- Compactness: `C = G M / (R c^2)`, dimensionless. For illustrative mass 1.4 solar masses and radius 12 km, `C ≈ 0.172278`. Black-hole horizon formula `R_s=2GM/c²` applies to the Schwarzschild exterior and is **not a full theorem about spinning-star collapse or any star based solely on size**.
- EoS: `P[Pa] = P(epsilon[J/m³])`. Define `c_s²/c² = dP/d epsilon` for barotropic local EOS, subject to domain and assumptions. A microscopic QCD stress distribution is not a measured nuclear-bulk EOS without statistical/thermodynamic derivation.
- Luminosity/diameter distances under cosmic transparency and photon number conservation: `eta(z) = D_L / ((1+z)^2 D_A) = 1`. A deviation in a model may reflect calibration/selection as well as opacity. Not a detection.
- Distances: `D_H = c/H(z)`, `D_M` and `r_d` use Mpc; do not multiply new AP full-shape data and original BAO data as statistically independent.
- Identifiability: `Omega_s0=0` is a measured-fit boundary state; `z_t` and `w_t` may be unidentifiable, but `TOKEN_VAZIO` of their posterior is not numerical zero.

## New source provenance (selection)

1. DESI Collaboration 2026 Ly-alpha AP official: https://arxiv.org/abs/2607.27410 and official 2026 release (13 sources with exact IDs in contract).
2. DES-Dovekie 2026 peer reviewed: https://doi.org/10.1093/mnras/stag632 ; independent 2026 SN truncation https://doi.org/10.1093/mnras/stag1868.
3. Distance duality/opacity 2026 peer reviewed: https://doi.org/10.1093/mnras/stag1380.
4. Non-cold dark matter interpretation 2026: https://doi.org/10.1016/j.physletb.2026.140858 ; coupled quintessence preprint https://arxiv.org/abs/2610.23497.
5. NICER 2026 peer-reviewed review https://doi.org/10.1146/annurev-nucl-100824-043815; sound-speed scaling preprint https://arxiv.org/abs/2610.21806; hybrid quark-core preprint https://arxiv.org/abs/2610.28408; hypothetical dark core https://arxiv.org/abs/2609.14494.
6. Bayesian prior/DEI caution https://arxiv.org/abs/2603.05472.

## Route and evidence

- Machine-readable: `data/governance/RLL_NEGLECTED_CROSS_SCALE_FALSIFIERS_20261108_V1.json`.
- Validator: `tools/ci/rll_neglected_cross_scale_gate_v1.py`.
- Adversarial tests: `tests/test_rll_neglected_cross_scale_gate_v1.py`.
- Parent cross-scale graph unchanged; CI appends one scoped test step; no gates removed and no datasets/models/likelihoods changed.
- **A source paper ≠ implemented RLL equation ≠ observed RLL agreement**. Every P0 experiment must have explicit source snapshots, model priors, covariance, identified target and negative null tests, followed by an independent replication to promote.

## Falsifiers / rollback

```
python -m unittest discover -s tests -p test_rll_neglected_cross_scale_gate_v1.py -v
python tools/ci/rll_neglected_cross_scale_gate_v1.py --root . --output artifacts/python-tests/rll_neglected_cross_scale_receipt.json
```

This yields **PASS_SCOPED_STRUCTURE_ONLY** if and only if references, typed edges and claim barriers are intact, never physical validation. Keep all prior CI failures. Closing DRAFT PR or reverting additive files/CI insertion is a reversible rollback.
