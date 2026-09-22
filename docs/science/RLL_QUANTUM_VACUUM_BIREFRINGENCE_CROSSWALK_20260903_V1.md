
# RLL — Quantum Vacuum Birefringence Crosswalk — 2026-09-03

**State:** `DOCUMENTED_PRIMARY_SOURCE_CROSSWALK_TEST_ROUTE_OPEN`
**Policy:** `APPEND_ONLY / CLAIM_ALLOWED=false / PUBLICATION_EFFECT=NONE`
**Canonical machine record:** `data/real_sources/rll_quantum_vacuum_birefringence_crosswalk_20260903.v1.json`

## Source boundary

The discovery article points to Stewart *et al.*'s paper, but it is not the
scientific evidence source used here. The primary source is the Nature version
of record, with the versioned [arXiv v5 preprint](https://arxiv.org/abs/2509.19446)
as a readable provenance anchor. The study reports phase- and energy-resolved
X-ray polarization measurements of magnetar 1E 1547.0-5408 using coordinated
IXPE, NICER and Parkes/Murriyang observations. It concerns QED propagation in
an extreme magnetic-field environment.

The repository does not contain frozen source bytes, supplementary data, event
files, response files, source rights terms, or an independent reproduction.
Those absences are deliberate `TOKEN_VAZIO` records, not negative facts about
the paper.

## Crosswalk

| Layer | Directly supported | Only analogous | Boundary / gap |
|---|---|---|---|
| Strong-field QED | The source reports a polarimetric pattern consistent with vacuum-birefringence-governed propagation under the stated magnetar model. | A multi-observable test can guide how a future RLL claim is falsified. | It does not test RLL, cosmological expansion, dark matter, or dark energy. |
| Canonical-main RLL observer/mirror/photon gate | The canonical `main` artifact explicitly identifies itself as a synthetic proxy; it is absent from the `rll/lab` baseline and is not copied by this crosswalk. | Both use emitted/propagated/observed distinctions. | `TOKEN_VAZIO_NO_EXACT_RLL_QED_FORMULA`; no physical magnetar forward model exists in RLL. |
| DESI DR2 BAO result | The committed 13-point setup labels LCDM preferred over the stored fixed RLL parameterization. | None needed. | This background-distance result is a separate observable, not evidence about magnetar vacuum birefringence. |
| Formula-literature graph | `CLASS_MATCH != SUPPORTS_EXACT` is already an invariant. | The new paper can be a methodology reference after a formula exists. | No formula edge is added until an exact typed RLL prediction, units and falsifier exist. |
| Drive editorial corpus | The operating contract requires source → index → claim → evidence → falsifier separation. | It guides editorial custody. | Private Drive identifiers/content are not copied into the public RLL repository. |

## Testable routes

1. **Reproduce polarimetry:** require rights-cleared IXPE inputs, responses,
   radio ephemeris, hashes, frozen environment and equal-treatment baselines.
2. **Define an RLL QED observable:** require a typed equation, units, nested
   no-extra-term limit, baselines, likelihood and predeclared falsifier.
3. **Assess any cosmology transfer separately:** require a valid derivation,
   distinct cosmological observable, full parity likelihood and independent
   replication. The magnetar result supplies none of these by itself.

## Append-only index and `TOKEN_VAZIO`

Implemented now:

- `data/real_sources/rll_quantum_vacuum_birefringence_crosswalk_20260903.v1.json`
- `workflows/TOKEN_VAZIO_LEDGER_RAFAELIA.md` — four new gaps
- `.github/workflows/rll-quantum-vacuum-birefringence-audit.yml`

Intentionally not changed:

- `data/science/rll_formula_literature_edges.v1.json`: adding an exact edge
  before an exact formula would violate its own contract.
- Canonical `main` at `d500131fff841c6b26c8e3e2f353f23294b12423`:
  `data/evidence/rll_observer_mirror_photon_gate_20260815.json` is historical synthetic evidence; it is absent from the `rll/lab` baseline and must not be copied or rewritten as a measurement.

## Adaptive CI policy

The workflow is deliberately artifact-only (`contents: read`): it never
commits, opens PRs, or ingests remote data. It runs:

- a lightweight integrity/provenance audit hourly at minute 17;
- the deeper test-route audit daily at 04:35 UTC;
- the deeper audit when this crosswalk, its validator, tests, ledger, document
  or workflow changes through a PR or `main` push.

A light-audit failure is fail-closed and produces a receipt; it does not
silently retry, change thresholds, fetch data or promote a claim. Escalation is
visible in the artifact and can be dispatched manually as the deep profile.

## R3

```text
F_ok   = primary sources, repository boundaries and test routes are separated.
F_gap  = source/data receipts, reproduction, an RLL QED model and a cosmology transfer derivation.
F_next = merge only after CI evidence; then use the hourly workflow as a boundary audit, not as scientific proof.
```

