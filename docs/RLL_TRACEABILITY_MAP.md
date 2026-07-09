# RLL Traceability Map

Status: central linkage map.

Purpose: connect each RLL claim, artifact family and provenance question to the document where it is treated.

This file is an index of responsibility. It does not prove every claim by itself. It tells where each claim must be verified, where evidence lives, and what remains TOKEN_VAZIO.

## 1. Core rule

Every item must be treated in one of four states:

| State | Meaning |
|---|---|
| VERIFIED | read in tag, commit, file, release, result or manifest |
| DECLARED_BY_AUTHOR | declared by Rafael but not yet independently verified in repo/files |
| TOKEN_VAZIO | required evidence not yet located |
| CONTRADICTION | evidence conflicts with claim |

No unsupported inference should be promoted to fact.

## 2. Central chain

```text
RLL v1.0.0 tag / 2025 formula
→ early images / CSVs / data stations
→ possible mobile-Termux execution provenance
→ 2026 DESI/CPL/AICc validation
→ joint-real likelihood and claim gate
→ uploaded validation/Bayes artifact custody
→ presentation / academic framing
```

## 3. Where each thing is treated

| Thing / question | Status now | Treated in | What to verify next |
|---|---|---|---|
| Public anteriority of RLL | VERIFIED | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | compare tag with DOI/Zenodo package |
| Tag `v1.0.0` formula | VERIFIED | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | locate all files in tag snapshot |
| `Ω_s0` / superposition term | VERIFIED in README tag | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | first commit/file ancestry ledger |
| `f(a)` transition | VERIFIED in README tag | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | exact definition and later code evolution |
| DE→matter transition language | VERIFIED in README tag | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | map to later `e2_rll_logistic` |
| magnetic term `Ω_B0 a^-4` | VERIFIED in README tag | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | determine whether it remained active or became latent |
| plasma term `Ω_P0 a^-4` | VERIFIED in README tag | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | determine whether it remained active or became latent |
| H(z), Δμ, w_eff, fσ8, rotation, lensing observables | VERIFIED as planned observables in README tag | `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` | locate actual images, CSVs and scripts |
| Images from early tag/project | TOKEN_VAZIO | future `docs/RLL_V1_IMAGE_CSV_PROVENANCE.md` | inventory tag and DOI files |
| CSVs for models, entropy, growth, curves | TOKEN_VAZIO | future `docs/RLL_V1_IMAGE_CSV_PROVENANCE.md` | locate paths and hashes |
| Data stations | DECLARED_BY_AUTHOR / TOKEN_VAZIO | future `docs/RLL_DATA_STATIONS_MAP.md` | define station nodes formula→input→script→output |
| Calculations done on Rafael's own cellphone | DECLARED_BY_AUTHOR | `docs/RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md` | find logs, screenshots, metadata, Termux paths |
| Termux/mobile execution | DECLARED_BY_AUTHOR / TOKEN_VAZIO | `docs/RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md` | find `termux-info`, shell logs, Android paths or generated artifact metadata |
| `1234.zip` chunks | PARTIALLY VERIFIED by uploaded checksum/text listing | future `docs/RLL_1234_CHUNK_TEXT_AUDIT.md` | read text chunks and map formulas/timestamps/claims |
| `567.zip` chunks | TOKEN_VAZIO | future chunk audit | inspect after `1234.zip` |
| `8910.zip` chunks | TOKEN_VAZIO | future chunk audit | inspect after `567.zip` |
| DOI/Zenodo package | TOKEN_VAZIO in repo docs | future `docs/RLL_DOI_ZENODO_CHAIN_OF_CUSTODY.md` | compare DOI files against tag |
| DESI linkage | VERIFIED as 2026 work | existing and future DESI docs | map first DESI commit and materialization commits |
| CPL/wCDM/AICc fairness | VERIFIED in 2026 code/docs | existing missing-calculations and fairness docs | preserve distinction from 2025 tag |
| Joint-real result and claim gate | VERIFIED in current result files | current result docs and future summary | keep `claim_allowed=false` where appropriate |
| Uploaded validation/Bayes package, 2026-07-09 | VERIFIED as uploaded artifact custody / CLAIM_BOUNDED | `results/coerente/2026-07-09_uploaded_validation_bayes/README.md` and `results/coerente/2026-07-09_uploaded_validation_bayes/audit_manifest.json` | add raw observational data, covariance, priors, likelihood, script, environment and convergence diagnostics before scientific validation claims |
| False positives | DECLARED_BY_AUTHOR / TOKEN_VAZIO | future `docs/RLL_FALSE_POSITIVE_LEDGER.md` | locate failed outputs/logs/rejected hypotheses |
| Non-post-hoc formulation | PARTIALLY VERIFIED | future `docs/RLL_NON_POSTHOC_FORMULATION_AUDIT.md` | connect formula date → data date → result date |

## 4. Required future files

The following files are reserved as next documentation nodes:

| File | Purpose |
|---|---|
| `docs/RLL_V1_TAG_FILE_INVENTORY.md` | full inventory of files present in `v1.0.0` |
| `docs/RLL_FORMULA_ANCESTRY_LEDGER.md` | first appearance of each formula component |
| `docs/RLL_V1_IMAGE_CSV_PROVENANCE.md` | image and CSV provenance from tag/DOI |
| `docs/RLL_DATA_STATIONS_MAP.md` | station map linking formula→input→script→output |
| `docs/RLL_1234_CHUNK_TEXT_AUDIT.md` | text-only audit of `1234.zip` chunks |
| `docs/RLL_DOI_ZENODO_CHAIN_OF_CUSTODY.md` | DOI/Zenodo package vs GitHub tag comparison |
| `docs/RLL_FALSE_POSITIVE_LEDGER.md` | failed/partial/rejected results |
| `docs/RLL_NON_POSTHOC_FORMULATION_AUDIT.md` | final non-post-hoc evidence chain |

## 5. Claim language router

### If speaking about 2025 tag

Use:

> The `v1.0.0` tag documents the RLL base formulation, including a Friedmann-extension term, `Ω_s0`, `f(a)`, DE→matter transition language, magnetic/plasma terms and planned observables.

Do not use:

> The tag proves RLL is correct.

### If speaking about mobile/Termux

Use:

> The author declares mobile/Termux execution; this remains under provenance audit until logs, scripts, paths, metadata or hashes are located.

Do not use:

> The repository already proves all calculations were run on a cellphone.

### If speaking about DESI/CPL/AICc

Use:

> DESI/CPL/AICc validation is later 2026 maturity work applied to an earlier RLL base formulation.

Do not use:

> RLL beats CPL because it has anteriority.

### If speaking about uploaded validation/Bayes artifacts

Use:

> The 2026-07-09 uploaded validation/Bayes package is verified as artifact custody with hashes and claim boundary; in this artifact, RLL is numerically close to LCDM, while χ² and Bayes factor favor LCDM.

Do not use:

> The uploaded Bayes package proves RLL or declares cosmological superiority.

### If speaking about `1234.zip`

Use:

> `1234.zip` is a text-chunk evidence source to be audited separately; checksums/parts must be mapped before conclusions.

Do not use:

> The chunk file proves the scientific claim before reading it.

## 6. Minimal workflow

```text
1. Read source artifact.
2. Record exact path/ref/date/hash.
3. Classify as VERIFIED / DECLARED_BY_AUTHOR / TOKEN_VAZIO / CONTRADICTION.
4. Link it to the correct document.
5. Only then allow interpretation.
```

## 7. Current summary

The project now has four active documentation layers:

1. `docs/RLL_V1_TAG_ANCESTRALITY_AUDIT.md` — what the 2025 tag proves.
2. `docs/RLL_MOBILE_TERMUX_PROVENANCE_LEDGER.md` — what remains to prove about mobile/Termux execution.
3. `docs/RLL_NEXT_WORK_DOCUMENTATION_PLAN.md` — what documents must be built next.
4. `results/coerente/2026-07-09_uploaded_validation_bayes/` — what the uploaded validation/Bayes package proves as artifact custody, and what it does not prove scientifically.

This map binds those layers and prevents the project from scattering claims across unrelated files.
