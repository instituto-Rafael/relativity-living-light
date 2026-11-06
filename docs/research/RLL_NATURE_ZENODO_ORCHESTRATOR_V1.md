# RLL scientific-source orcha V1 — Nature × Zenodo

**Producer:** `instituto-Rafael/relativity-living-light`; bounded new adapter `scripts/rll_source_orchestrator.py`.
**Authority:** existing ORCID/Crossref/DataCite/OpenAlex routes remain in `src/rll/orcid_vector.py`, and the existing Giza academic intake remains in its own workflow. This orchestrator aggregates *public scholarly metadata* only; it does not supersede any research, reproduce peer review, or import licensed content.

## Inputs and routes

1. Nature journals by official ISSN, queried via public Crossref journal works API: Nature `0028-0836`; Nature Communications `2041-1723`; Nature Astronomy `2397-3366`.
2. Zenodo published public records via `https://zenodo.org/api/records/?q=...&size=...`.
3. Bounded normalized title, DOI, author names, publication date, license reference, exact provider record ID, and per-provider canonical SHA-256 fingerprint. No abstract, article text, PDFs, datasets, provider tokens, credentials or user-specific content.
4. Deterministic DOI lowercasing and same-DOI dedup; absent DOI uses `provider:id`, never fuzzy-title identity. Preserve distinct observations and metadata disagreements rather than falsely equating hypotheses with publications.
5. Claim is permanently `false`. Network failures are `TOKEN_VAZIO` with explicit provider result and nonzero live status; successful retrieval is not scientific validation.

## Run

```sh
python3 -m unittest discover -s tests -p test_rll_source_orchestrator.py -v
python3 scripts/rll_source_orchestrator.py --mode offline --query cosmology --journal nature
# Only when authorized to query public networks:
python3 scripts/rll_source_orchestrator.py --mode live --query cosmology --journal nature-communications --limit 5
```

`workflow_dispatch` in `.github/workflows/rll-nature-zenodo-intake.yml` allows deliberate **live** or **offline** mode; `pull_request` runs offline tests only. No schedule, auto-commit, automatic upload to Zenodo, auto-publication, webhook from Supabase or cross-repo secret broker. Artifacts have run ID, sha, 30-day retention; journal and provider URL remain in the catalog. Offline mode uses empty contract probes, **NOT** real papers.

## Existing work, rights and gaps

- Reuse RLL `src/rll/orcid_vector_model.py` metadata conventions conceptually; no duplicate ORCID database, Crossref enrichment store or CI executor.
- Nature text is governed by publisher rights. Open-access/licensed materials require *per-record* verification before separate content download. Zenodo license metadata describes a record but does not automatically license all linked datasets identically.
- Bibliographic metadata is not likelihood evidence for RLL/ΛCDM. No paper or preprint automatically supports RLL.
- Future: after review, map the bounded catalog into `raf_private.rafdb_federated_events_v1` as source references only, with separate authenticated writer; no client-side `service_role` or implicit cross-project sync.
- Source code status `IMPLEMENTED_UNTESTED` until exact-head CI. Physical runtime and autonomous retrieval `TOKEN_VAZIO`. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

**Rollback:** close the draft PR or revert additive paths; no dataset, existing workflow, tables or source observations are mutated.

Provider documentation: https://www.crossref.org/documentation/retrieve-metadata/rest-api/ and https://developers.zenodo.org/
