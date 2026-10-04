# RAFAELIA Source Intake V1 — 2026-10-04

Author: RAFAEL MELO REIS

## Governance

This registry records three source packages as **source material only**.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

No package in this registry is promoted to scientific evidence or an RLL model claim by inclusion alone. `claim_allowed=false` until a dedicated validation route closes the relevant evidence gaps.

## Sources

### SRC-RLL-20261004-001 — Manifesto-publico-main (1).zip

- SHA-256: `bf30da9182ae2472b2d18158a6f9e3bc1a179b5a63b422d9683941499a094fb5`
- observed role: multimodal documentary/source package
- contents observed: Markdown, LICENSE, DOCX/PDF and image assets
- RLL state: `SOURCE_BOUND / NOT_EVIDENCE`
- sensitivity: contains personal/sensitive documentary material; public projection must be redacted
- claim_allowed: `false`

### SRC-RLL-20261004-002 — Matriz_Simbiotica_Aurora_Boreal_Plantas_RAFCODE_SIGMA.zip

- SHA-256: `174b5db1a6698eb2fa8096572a4e9039b3fb6bed89822fbb7d0bf641f3a4aa30`
- observed role: visual/conceptual source package
- contents observed: five PNG assets
- conceptual relations observed: plants, photosynthesis, atmosphere, ionization, magnetic field, aurora, life
- RLL state: `SOURCE_BOUND / VISUAL_CONCEPT / NOT_EVIDENCE`
- claim_allowed: `false`

### SRC-RLL-20261004-003 — RAFAELIA_RUIDOukkk_VETORES_AMOR_CRUZADO.zip

- SHA-256: `a2f9632a9b538d609c4b6745f27725627a626246a770dd8a6881107c28fa1e5f`
- observed role: numerical vector/matrix source package
- inner object observed: `vetores_amor_cruzado.csv`
- observed matrix shape: `7777 x 128`
- semantic schema: `TOKEN_VAZIO`
- producer/generation rule: `TOKEN_VAZIO`
- RLL state: `SOURCE_BOUND / NUMERIC_MATRIX / SEMANTICS_PENDING`
- claim_allowed: `false`

## RLL routing

These sources may be used by RLL only through an explicit route:

`SOURCE -> PARSER -> NORMALIZATION -> PROVENANCE -> EVIDENCE_TEST -> RECEIPT -> CLAIM_GATE`

Until such a route produces reproducible evidence, the source packages remain inputs/candidates rather than scientific validation.

## Intended Drive custody

Raw ZIP bytes are kept outside Git history in Google Drive custody. GitHub stores only stable identities, roles, semantic state, provenance pointers and validation contracts.

## F_gap

- Drive object IDs: `TOKEN_VAZIO_PENDING_WRITE_READBACK`
- source-to-RLL scientific mapping: `TOKEN_VAZIO`
- independent reproduction: `TOKEN_VAZIO`
- scientific claim promotion: `BLOCKED`
