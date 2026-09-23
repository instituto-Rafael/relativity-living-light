# RECEIPT — MU-RLL-G123-SEED-COMPRESSION-NULL-20260921

**Autor:** RAFAEL MELO REIS  
**Estado:** `ANALYSIS_RUN / claim_allowed=false`  
**PR:** #939  
**Workflow run:** `35560384933`  
**Workflow artifact:** `10621413680` — `rll-language-g123-20260921`  
**Artifact ZIP digest:** `sha256:741257e12266d9ffd015bd7f8896bbe1c6b7c0686c903861e6eb8192739689e1`  
**Runner commit executed:** `206bc4c672d3d0d1abd98c24d304193dc2161c2e`

## G1 — Seed Reconstruction

**PASS**

- 9/9 source SHA-256 values matched the pinned source manifest.
- Intersection: 3,483 aligned verse references.
- Normalized records: 10,449.
- Exact reconstruction: `true`.
- Baseline SHA-256 = reconstructed SHA-256:
  `960d1c6601229ff5dee138e21e826724e94ef4952536dcf97db5b46b70e82c8f`.

Interpretation: the declared SCD1 seed is sufficient to reconstruct the normalized canonical record representation used by this gate. This does not reconstruct source editorial metadata stripped before normalization.

## G2 — Total-Cost Compression

**Strong claim: FAIL**

Payload bytes:

| representation | raw | gzip-9 | zstd-19 | brotli-11 |
|---|---:|---:|---:|---:|
| plain | 1,213,948 | 378,330 | 324,564 | 317,003 |
| SCD1 seed | 1,273,254 | 389,332 | 327,723 | 320,306 |
| verbose JSON | 1,642,359 | 468,012 | 374,427 | 366,235 |

Declared custom overhead:
- schema contract: 184 B
- repository-local decoder implementation upper bound: 4,281 B
- best SCD1 compressed payload: 320,306 B
- SCD1 + counted custom overhead: 324,771 B
- best generic-compressed plain baseline: 317,003 B
- external generic codec runtime cost: `TOKEN_VAZIO_EXTERNAL_RUNTIME`

Therefore the strong claim that SCD1 beats the best generic-compressed plain-text baseline after counted custom overhead is **false in this run**.

## G3 — Null / Shuffle Controls

**PASS for the preregistered null criterion.**

Preregistered metric: zstd-19 compressed SCD1 seed bytes.  
Canonical: **327,723 B**.  
32 deterministic permutations per null family, seed `20260921`.

| null family | min | median | max | p(one-sided) |
|---|---:|---:|---:|---:|
| common order shuffle | 348,233 | 348,539 | 348,924 | 0.030303 |
| independent language shuffle | 341,519 | 341,710.5 | 341,924 | 0.030303 |
| label permutation | 342,607 | 342,894.5 | 343,122 | 0.030303 |

No null sample compressed to a size less than or equal to the canonical representation in any of the three families.

This supports an ordering/structure effect **within this declared corpus and metric**. It does not establish a universal semantic law.

## External nonreligious parallel control — UDHR

Source: `thammegowda/014-udhr-dataset@281fb4d07b442d2da95ca057e47c2809c56f68f3`.

Rows selected:
- ENG: `eng`
- SPA: `spa`
- POR: `por_BR`

- aligned segments: 90
- normalized records: 270
- exact reconstruction: `true`
- baseline SHA-256 = reconstruction SHA-256:
  `10083f07fc785be7811dd9d06d1620bbf3689729a2e5985f2116d1b409deba32`

Payload bytes:

| representation | raw | gzip-9 | zstd-19 | brotli-11 |
|---|---:|---:|---:|---:|
| plain | 33,064 | 11,033 | 10,506 | 9,254 |
| SCD1 seed | 34,417 | 11,399 | 10,829 | 9,493 |
| verbose JSON | 43,326 | 12,262 | 11,502 | 10,134 |

The external-domain control reproduces the same broad pattern: structural SCD1 is smaller than verbose JSON but remains larger than plain text and its generic compressed variants.

## Boundaries

- `SINTROPIA_OPERACIONAL != ENTROPIA_TERMODINAMICA_NEGATIVA`
- `TOKEN_VAZIO != ZERO`
- compression payload != total system cost
- single-corpus null result != universal semantic law
- `claim_allowed=false`

## R3

`F_ok`: G1 exact reconstruction and source custody passed; G3 preregistered null controls passed; UDHR external-domain reconstruction succeeded.

`F_gap`: the strong G2 compression claim failed; generic codec runtime size remains TOKEN_VAZIO; null families test structural/order effects, not physical entropy or universal semantics.

`F_next`: treat G2 failure as a design constraint; next scientific work should separate (a) reconstructibility, (b) metadata/provenance utility, and (c) compression efficiency, rather than combining them into one superiority claim.
