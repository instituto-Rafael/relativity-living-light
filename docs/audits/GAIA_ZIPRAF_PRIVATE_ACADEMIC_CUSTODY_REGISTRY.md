# GAIA, ZIPRAF and Rafaelia Private — Academic Custody Registry

## Purpose

This registry connects three supporting repositories to the RLL scientific pipeline without confusing their functions.

```text
Rafaelia_Private
private pointer / key governance
        ↓ reviewed metadata only
GAIA_phi
bibliography / tokenization / vector index / custody receipts
        ↓ evidence candidates
ZIPRAF_OMEGA_FULL
format / compression / hashchain prototype results
        ↓ benchmark candidates
RLL
hypothesis / units / falsifier / data / statistics / replication / publication
```

## Role matrix

| Repository | Role | What it can prove | What it cannot prove alone |
|---|---|---|---|
| `GAIA_phi` | academic index and vector forest | deterministic ingestion, token IDs, retrieval projections, provenance receipts | scientific truth, authenticated ORCID ownership, human semantics |
| `ZIPRAF_OMEGA_FULL` | historical prototype and format/hashchain laboratory | existence of code, format behavior and a specific measured run | universal performance, TRL, physical/biological law, blockchain consensus |
| `Rafaelia_Private` | private pointer and key-governance vault | existence/integrity of a private artifact through reviewed digests | public content, independent replication, scientific validation |
| `RLL` | scientific and publication authority | claim-bounded analysis when all gates pass | proof merely from repository ownership or bibliography count |

## ORCID and DOI

The RLL already provides a read-only ORCID/DOI/DataCite pipeline. The ORCID iD remains `TOKEN_VAZIO_ORCID_ID` until authenticated and confirmed by the owner. The reference DOI is `10.5281/zenodo.17188137`.

Supporting repositories may prepare candidate bibliographic records, but they do not write to ORCID automatically. DOI resolution proves metadata identity and preservation; it does not validate a scientific claim.

## Vector interoperability

Three distinct vector categories are preserved:

1. GAIA legacy 3-D hash projection — deterministic addressing;
2. GAIA 32-D token hash projection — deterministic retrieval index;
3. RLL `rll-hash32-v1` — deterministic cross-source retrieval profile.

None of these is promoted as a learned semantic embedding. Learned embeddings must record model name, version, weights/artifact hash, tokenizer, dimensions, license and execution receipt.

## Historical determinism

Every cross-repository record includes the repository, exact commit, canonical metadata, content digests and previous chain hash. Corrections append a superseding record instead of silently replacing history.

Triple digest profiles are accepted for algorithm diversity:

- SHA-256;
- SHA3-512;
- BLAKE2b-256.

A hashchain remains a hashchain. RLL does not use the word blockchain until distributed consensus and independent validators actually exist.

## Turing/LLM boundary

The deterministic kernel validates schemas, hashes, commands and receipts. The LLM may search, classify, propose relations and draft text. It cannot certify its own result, hold signing keys or turn a generated sentence into evidence.

## Promotion gate

A candidate reaches scientific review only after:

```text
identity
→ provenance
→ bibliography deduplication
→ explicit hypothesis
→ units and domain
→ falsifier
→ data/code hashes
→ execution receipt
→ statistical diagnostics
→ independent reproduction
→ human review
```

Failure at any stage preserves `TOKEN_VAZIO` or another typed non-promoted state.

## Proposed supporting heads

- GAIA_phi PR #49 — `109f69c6f95c273078d005734d7d634441ae21c6`;
- ZIPRAF_OMEGA_FULL PR #33 — `44bdeacd6a5fab391bb4f5c07050f774da76d67e`;
- Rafaelia_Private PR #192 — `031d89ac4249f79aaf55ae84bdbc6d54993431ae`.

These remain review candidates and are not treated as merged authority.

## R3

- **F_ok:** RLL already has DOI, ORCID read-only ingestion, vector indexing, hash-gated project sources and claim boundaries.
- **F_gap:** authenticated ORCID, cross-repository signatures, independent validator/replication and reviewed quantitative ZIPRAF receipts.
- **F_next:** merge only after the three supporting repositories expose compatible role manifests and local tests.
