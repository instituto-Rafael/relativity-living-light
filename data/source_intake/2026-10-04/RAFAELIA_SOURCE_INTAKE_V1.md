# RAFAELIA Source Intake V1 — 2026-10-04

Author: RAFAEL MELO REIS

## Governance

This registry records three packages as source material only.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

Inclusion, Drive custody or hashing does not promote a package into scientific evidence. `claim_allowed=false` until a dedicated validation route closes the relevant gaps.

## Sources

### SRC-RLL-20261004-001 — Manifesto-publico-main (1).zip

- Drive metadata identity, size and parent: `VERIFIED_METADATA_READBACK`
- declared SHA-256: `bf30da9182ae2472b2d18158a6f9e3bc1a179b5a63b422d9683941499a094fb5`
- independent byte hash: `TOKEN_VAZIO_HASH_READBACK`
- observed role: multimodal documentary/source package
- RLL state: `SOURCE_BOUND / NOT_EVIDENCE`
- sensitivity: contains personal/sensitive documentary material; public projection requires redaction
- claim_allowed: `false`

### SRC-RLL-20261004-002 — Matriz_Simbiotica_Aurora_Boreal_Plantas_RAFCODE_SIGMA.zip

- Drive metadata identity, size and parent: `VERIFIED_METADATA_READBACK`
- declared SHA-256: `174b5db1a6698eb2fa8096572a4e9039b3fb6bed89822fbb7d0bf641f3a4aa30`
- independent byte hash: `TOKEN_VAZIO_HASH_READBACK`
- observed role: visual/conceptual source package
- declared/previously observed contents: five PNG assets
- RLL state: `SOURCE_BOUND / VISUAL_CONCEPT / NOT_EVIDENCE`
- claim_allowed: `false`

### SRC-RLL-20261004-003 — RAFAELIA_RUIDOukkk_VETORES_AMOR_CRUZADO.zip

- Drive metadata identity, size and parent: `VERIFIED_METADATA_READBACK`
- verified SHA-256: `a2f9632a9b538d609c4b6745f27725627a626246a770dd8a6881107c28fa1e5f`
- inner object: `vetores_amor_cruzado.csv`
- inner size: `18821256` bytes
- observed shape: `7777 x 128` data cells by row/column, plus one header row
- semantic schema: `TOKEN_VAZIO`
- producer/generation rule: `TOKEN_VAZIO`
- RLL state: `SOURCE_BOUND / NUMERIC_MATRIX / SEMANTICS_PENDING`
- claim_allowed: `false`

## RLL routing

A package may enter RLL only through:

`SOURCE -> PARSER -> NORMALIZATION -> PROVENANCE -> EVIDENCE_TEST -> RECEIPT -> CLAIM_GATE`

Until this route produces reproducible evidence, the packages remain inputs or candidates rather than validation.

## Drive custody readback

Raw ZIP bytes remain outside Git history in Drive folder `13B9hxoGZB5P552fF6DsOVl3vbrsYVmeW`. Stable object IDs, names, sizes and parent membership were read back. Source 003 was downloaded and independently rehashed; sources 001 and 002 were not independently rehashed in this reconciliation.

GitHub stores identities, bounded observations, semantic state, provenance pointers and validation contracts. See `DRIVE_BINDINGS_V1.md` for exact object IDs.

## F_gap

- Drive object IDs: `VERIFIED_METADATA_READBACK`
- source 003 hash and shape: `VERIFIED_LOCAL_READBACK`
- sources 001 and 002 independent byte hashes: `TOKEN_VAZIO_HASH_READBACK`
- source-to-RLL scientific mapping: `TOKEN_VAZIO`
- semantic schema for source 003: `TOKEN_VAZIO`
- independent scientific reproduction: `TOKEN_VAZIO`
- scientific claim promotion: `BLOCKED`
