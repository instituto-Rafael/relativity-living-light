# RLL Ω — Evidence DAG and Polymorphic Hypothesis Composition V1

**Authority:** `instituto-Rafael/relativity-living-light`. **State:** `STRUCTURAL_SHADOW_NO_NETWORK`.
**No new workflow count**: attach one offline gate to existing `.github/workflows/rll-calibration-orchestrator.yml`.
`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`; `claim_allowed=false`.

## 1. Existing routes, no parallel engines

- Research composition: `data/contracts/frontier_research_composition.v1.yml` and existing `frontier-research-composition.yml`.
- Observational G4/G5: `tools/run_g4_background_tournament.py` and `tools/build_g5_canonical_background_manifest.py`.
- Existing Nature/Zenodo metadata intake: `.github/workflows/rll-nature-zenodo-intake.yml`.
- Hypothesis instability: `.github/workflows/hypothesis-instability-orchestrator.yml`.
- NOAA source governance: `data/climate/rll_climate_source_registry.v1.json`.
- Cross-domain relation precedent: `data/governance/RLL_CROSS_SCALE_EVIDENCE_GRAPH_20261028.json`.
- Cellular boundary: `data/science/rll_cellular_metabolic_manifold_claims_v1.json`.
- Supabase: private `raf_private` graph/registry tables have RLS observed; no Edge Function observed. **Private index only, not provider of physical truth**. The CI does not connect to Supabase.

## 2. Evidence classes are not reputation scores

| Route | Current role | Promotion rule |
|---|---|---|
| DESI DR2 BAO / Pantheon+ | Instrument/collaboration observations | version, covariance, sample overlap, likelihood & independent reproducibility |
| NOAA NCEI | Climate/environmental observations | dataset release, station metadata, calibration, local applicability |
| Nature / SciELO | Scholarly articles & datasets linked by DOI | publication is evidence-of-publication, **not proof of results** |
| Zenodo | Archive, DOI versioning | content identity + version-specific DOI + independent validation |
| Crossref | DOI resolver/metadata | metadata only; citation count is not a prior |
| NIST | Established reference/constants | scope, edition, units and uncertainty must be frozen |
| Science X / Phys.org | News discovery | find primary paper; never raw-likelihood or measured data by itself |
| GitHub | Software custody | CI green does not mean experimental result |
| Supabase | Private index/relations/receipts | RLS and append-only metadata, no autonomous publication/compute |

Source official references: https://data.desi.lbl.gov/doc/papers/dr2/ ; https://www.ncei.noaa.gov/cdo-web/webservices ; https://zenodo.org/help/versioning ; https://www.scielo.org/pt-br/sobre-o-scielo/programa-scielo-modelo-scielo-de-publicacao-e-rede-scielo/ ; https://sciencex.com/help/journalism/ ; https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards .

## 3. Deductive / empirical / exploratory

- **Pétreo formal:** square diagonal = `side*sqrt(2)` under Euclidean/Pythagorean axioms. Deductive proof is not a posterior probability.
- **Biology:** ATP synthesis by bioenergetics is a physically measured mechanism, but RLL local validation is still NOT_RUN. A particular numerical claim requires primary biochemistry sources.
- **Exploratory:** a hypothetical biological tribo-X-ray energy pathway is `TOKEN_VAZIO_PHYSICAL_MECHANISM`. The analogy with mitochondrial bioenergetics may generate questions, not established causality or numeric evidence.
- **Cosmology:** compare ΛCDM/wCDM/CPL/GEDE/IDE/RLL under G4 frozen observations; G5 locks covariance/selection/nuisance and hashes; G6 posterior remains separate.

## 4. DAG

```text
S0 Source registry / rights
   -> S1 version, DOI, raw release and observational independence group
   -> S2 mathematical formal vs empirical vs exploratory classification
   -> S3 typed relations, scope and falsifier
   -> S4 Bayes readiness: registered prior, likelihood, full covariance, k/nuisance
   -> S5 [MANUAL] existing G4 six-model background tournament
   -> S6 existing G5 frozen-likelihood manifest
   -> S7 [SEPARATE] G6, growth/CMB and external replication
```

No numeric posterior is produced by this gate. No score based on prestige of journals.
Correlated DESI observations cannot be multiplied as independent evidence.
The conditional independence model must be documented; reject post-hoc priors, synthetic observations, diagonal covariance substitutions.

## 5. Security / rollback

`pull_request`: read-only checkout, no secrets, no network, no model fits, no supabase writes.
`workflow_dispatch=run_g4_g5` remains explicit and separately gated by pinned covariance and model scripts.
No new secrets, no `secrets: inherit`, no `pull_request_target`, no exposure of tokens. Existing GitHub secret **names/permissions not verified**.
Supabase future adapter would be manual, narrow scoped, RLS-preserving, append-only metadata after active authority checked. No live database writes in this wave.

Test locally: `python tools/ci/rll_polymorphic_evidence_gate_v1.py --require-pass`, then
`python -m unittest discover -s tests -p test_rll_polymorphic_evidence_gate_v1.py -v`.
Only CI execution on the exact branch head makes a `PASS_SCOPED` structural receipt.
Rollback: revert this additive commit or close the PR; legacy workflows and scientific code untouched.
