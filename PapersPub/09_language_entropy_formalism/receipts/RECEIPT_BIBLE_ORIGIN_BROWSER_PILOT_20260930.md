# Receipt — Bible Origin Browser Pilot V1 — 2026-09-30

**μID:** `MU-RLL-BIBLE-ORIGIN-BROWSER-PILOT-20260930`  
**State:** `OBSERVED_UNPROMOTED / claim_allowed=false`  
**Parent:** `BIBLE_ORIGIN_TRILANG_PROTOCOL_V1.md`

## SOURCE

Official eBible surfaces used:

- Hebrew Masoretic OT: `https://ebible.org/hbo/` — public domain.
- Genesis 1: `https://ebible.org/hbo/GEN01.htm`.
- Tischendorf Greek NT: `https://ebible.org/grc-tisch/` — public domain.
- Matthew 1: `https://ebible.org/grc-tisch/MAT01.htm`.
- John 1: `https://ebible.org/grc-tisch/JHN01.htm`.
- Daniel 2 target route: `https://ebible.org/hbo/DAN02.htm`.

A search result from `/heb/DAN02.htm` was **rejected** for the Aramaic measurement because it was not the pinned `hbo` witness. The official `hbo/DAN02.htm` route was resolved, but its chapter body was not exposed by the current parser, so:

```text
ARC_SOURCE_BODY = TOKEN_VAZIO
ARC_METRIC      = NOT_RUN
```

## EXECUTION

Local pilot harness:

```text
Unicode normalization = NFC
whitespace            = collapsed
window                 = first 1200 codepoints
codecs                 = gzip-9, bz2-9, lzma-9
lossless gate          = decompressed bytes == input bytes
```

The local sample hashes identify the normalized windows manually transferred from the browser-visible pages. They are **not** hashes of official downloaded source artifacts.

## EVIDENCE

### Greek, same edition, same script, equal window

| Metric | Matthew 1 | John 1 |
|---|---:|---:|
| H0 char (bits/symbol) | 4.865523 | 4.985082 |
| H1 char conditional | 2.023798 | 2.707464 |
| C1 local predictability | 0.584053 | 0.456887 |
| gzip/raw | 0.255149 | 0.361974 |
| bz2/raw | 0.232451 | 0.317312 |
| lzma/raw | 0.284153 | 0.387920 |

Within this **pilot window**, John has higher H0/H1, lower local predictability and is less compressible under all three codecs.

This is compatible with the pre-registered directional hypothesis for this window only.

### Critical confound

Matthew 1 is a genealogy with extreme lexical/syntactic repetition. Therefore:

```text
PILOT_DIRECTIONAL_OBSERVATION != WHOLE_BOOK_RESULT
PILOT_DIRECTIONAL_OBSERVATION != SEMANTIC_ENTROPY
PILOT_DIRECTIONAL_OBSERVATION != PHYSICAL_ENTROPY
```

### Hebrew control

Genesis 1, equal 1200-codepoint window:

```text
H0_char = 5.039936
H1_char = 2.736321
C1      = 0.457072
gzip/raw= 0.336547
bz2/raw = 0.290096
lzma/raw= 0.347064
```

No Hebrew↔Greek ranking is promoted because alphabet size, pointing/diacritics and UTF-8 representation are confounds.

## PROVIDER / CI

The isolated workflow `.github/workflows/rll-bible-origin-v1.yml` is materialized. Current connector queries expose pull-request-associated workflow runs only; no such run was observed for the queried heads.

```text
CI_PROVIDER_PASS = TOKEN_VAZIO
CI_PROVIDER_FAIL = TOKEN_VAZIO
CI_PROVIDER_OBSERVABILITY = PARTIAL
LOCAL_PILOT = OBSERVED_UNPROMOTED
```

## ROLLBACK

Close draft PR #1028 and delete the research branch after review if required. No main-branch file, ZIPRAF ABI, source corpus or prior SCD1 receipt was overwritten.

## R3

```text
F_ok   = same-edition Matthew/John pilot measured; lossless codecs verified locally; wrong Aramaic witness rejected
F_gap  = source-file hashes, automated ingestion, canonical Aramaic body, complete-book equal-window distribution, provider CI observation
F_next = pin downloadable hbo/grc source artifacts and run complete-book/resampled benchmark before any claim promotion
```
