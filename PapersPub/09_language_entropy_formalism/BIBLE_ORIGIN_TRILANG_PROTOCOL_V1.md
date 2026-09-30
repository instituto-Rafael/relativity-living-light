# RLL — Bible Origin-Language Entropy / Coherence / ZIPRAF Protocol V1

**Date:** 2026-09-30  
**State:** `PROTOCOL_MATERIALIZED / DATA_NOT_INGESTED / SELFTEST_GATE_MATERIALIZED / EXECUTION_NOT_OBSERVED / claim_allowed=false`  
**Authority:** RLL experiment/protocol only. This file does not redefine ZIPRAF ABI, BitRAF semantics, biblical textual criticism, phonological reconstruction, or physical theory.

## 0. Invariants

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TEXT_SOURCE != NORMALIZED_TEXT != PHONEME_MODEL != AUDIO != NEUROSCIENCE
LOGICAL_ADDRESS_DENSITY != PHYSICAL_COMPRESSION
RECONSTRUCTIBLE_NORMALIZATION != RECONSTRUCTIBLE_SOURCE_EDITION
ANALOGY != PHYSICAL_COUPLING
TOKEN_VAZIO != 0
IMPLEMENTED_UNTESTED != PASS
```

## 1. Intent

Build a falsifiable multilingual benchmark using biblical corpora because they offer unusually deep editorial history, dense cross-reference structure, many translations, and stable verse/chapter identifiers.

The experiment measures:

- Shannon entropy at byte/code-point level;
- first-order conditional entropy;
- a declared local predictability/coherence statistic;
- exact lossless compression with generic codecs;
- order sensitivity against deterministic shuffled nulls;
- shared-reference structural representations;
- ZIPRAF logical indexing as a separate representation layer;
- later, grapheme/phoneme/acoustic layers under separate gates.

No metric is allowed to stand in for semantic truth, theology, thermodynamic entropy, quantum coherence, or human understanding.

## 2. Two orthogonal corpora

### 2.1 Parallel corpus — predecessor evidence

A previous RLL state executed SCD1 on:

```text
books = Genesis, Matthew, John
languages = English, Spanish, Portuguese
records = 10,449
intersection verses = 3,483
```

Pinned predecessor evidence:
- RLL commit containing executed benchmark: `3a34d6f3841857d2a1802a2902cbb9176f026122`
- result path: `PapersPub/09_language_entropy_formalism/results/SCD1_20260920.json`
- corrected G3 receipt: `PapersPub/09_language_entropy_formalism/RECEIPT_G3_METHOD_CORRECTION_20260921.md`

Observed predecessor result:
- verbose normalized JSON: 1,642,359 bytes;
- shared-reference seed: 1,273,254 bytes;
- plain text only: 1,213,948 bytes;
- seed vs verbose: -369,105 bytes (-22.474%);
- seed vs plain text: +59,306 bytes (+4.885%);
- exact normalized reconstruction: PASS;
- G1 reconstruction: PASS;
- G2 strong compression claim: FAIL;
- G3 corrected null scope: PASS;
- global scientific claim: blocked.

Interpretation: structural deduplication helped against verbose records, but did **not** beat plain text in that run.

### 2.2 Origin-language corpus — V1 target

The historical language classes are not forced into an artificial 3x3 parallel matrix.

```text
HBO = Biblical Hebrew
ARC = Biblical Aramaic passages in the Hebrew Bible textual witness
GRC = Koine/Ancient Greek New Testament
```

Initial public-domain candidates are recorded in `data/BIBLE_ORIGIN_SOURCE_MANIFEST_V1.json`.

Important boundary:
- Genesis is primarily Hebrew.
- Matthew and John are represented by Greek New Testament witnesses.
- Biblical Aramaic is sampled only from passages actually classified as Aramaic; it is not promoted to a whole-Bible "original Aramaic" layer.

This avoids comparing invented parallel originals.

## 3. Hypotheses, including John

### H-JOHN-1
John has measurably different information structure from Genesis and Matthew under one or more preregistered metrics.

### H0-JOHN
After controlling for sample size, Unicode treatment, book length, and representation, John is not distinguishable beyond the null distribution.

The lexical/theological fact that John begins with `Logos` is context for the hypothesis, not evidence of higher entropy.

Comparisons must use equal-size windows or resampling so book length does not decide the result.

## 4. Metrics

For symbol random variable X:

[
H_0(X)=-sum_x p(x)log_2 p(x)
]

For adjacent symbols:

[
H_1 = H(X_tmid X_{t-1})
]

Declared local predictability/coherence statistic:

[
C_1 =
egin{cases}
1-H_1/H_0,&H_0>0\
0,&H_0=0
end{cases}
]

and:

[
I_1 = 1-C_1
]

Here `C1` and `I1` are computational statistics only. They are **not** semantic coherence/incoherence.

Alphabet redundancy statistic:

[
R_Sigma = 1-rac{H_0}{log_2 |Sigma|}
]

when (|Sigma|>1).

### Candidate "centripia" / order-gain metric

Because "centripia" is not assumed to be a standard information-theory quantity, V1 records only a project-defined candidate:

[
C_{ord}=rac{widetilde L_{null}-L_{obs}}{widetilde L_{null}}
]

where:
- (L_{obs}) is compressed length of the ordered corpus;
- (widetilde L_{null}) is the median compressed length across deterministic verse-order permutations preserving the same verse texts;
- positive values mean the observed order compressed better than the null median.

State: `CANDIDATE_PROJECT_METRIC`. It must not be called thermodynamic syntropy/negentropy.

## 5. Compression baselines

V1 implementation uses stdlib codecs where available:
- gzip/DEFLATE;
- bz2;
- lzma/xz.

Every reported compressed size includes the produced compressed byte stream for that corpus representation. Exact decompression equality is mandatory.

Future optional baselines:
- zstd;
- brotli;
- a structure-aware dictionary codec;
- ZIPRAF-compatible container/index adapter.

Decoder/schema/dictionary/index/provenance costs must be counted whenever they are required for reconstruction.

## 6. ZIPRAF boundary

Observed producer source `termux-app-rafacodephi/rmr/Rrr/zipraf_index.h` explicitly describes its 8 reading modes x 33 density levels as logical structure over unchanged physical ZIP bytes and labels the mechanism **NOT compression**.

Therefore:

```text
ZIPRAF_LOGICAL_DENSITY = separate measured axis
ZIPRAF_PHYSICAL_BYTE_REDUCTION = TOKEN_VAZIO until a codec run proves it
```

The RLL experiment may emit a deterministic `mode|density|offset|len|policy` mapping or consume an external ZIPRAF adapter, but must never convert addressable logical space into a byte-compression ratio.

## 7. Relation to triple-matrix geometry

Current mathematical authority:
`rafaelmeloreisnovo/Matem-tica-/docs/formal/TRIPLE_MATRIX_GEODESIC_BALL_TORUS_FORMALIZATION_V0_2026-09-30.md`.

That artifact defines three layers (Phi_a), 100 nominal crossings per layer, and leaves the inter-layer joint relation (sim_J) as `TOKEN_VAZIO_RULE`.

For this language benchmark, a **candidate** three-layer data organization is:

```text
M1 = provenance/reference layer
M2 = text/token representation layer
M3 = transform/evidence layer
```

This is a software/data-model analogy only. It is not the same object as the geometric (Phi_a) construction unless an explicit typed mapping is later defined and tested.

## 8. Phonetics and acoustics

### G-PHON-0 — grapheme preservation
Preserve raw Unicode source plus NFC normalization as distinct artifacts. Diacritics/cantillation/accents must be measurable, not silently stripped.

### G-PHON-1 — phoneme model
Ancient Hebrew/Aramaic/Koine Greek pronunciation requires a named reconstruction convention/version. Output is `MODEL_DERIVED`, not native-speaker ground truth.

### G-PHON-2 — modern speech perception
Native-language perception effects must be tested on modern speakers/data under separate protocols. Literature supports language-specific phonetic category effects, but broad claims such as "speakers of language X cannot hear the middle/end of words" are not accepted without contrast-specific evidence.

### G-PHON-3 — acoustics
For licensed audio with known sampling metadata:
- duration;
- F0 distribution where estimable;
- spectral entropy;
- formant/segment features;
- timing/stress/prosody;
- reconstruction/model error.

Text entropy and acoustic entropy remain different observables.

## 9. Neuro/cognition boundary

Behavioral and neuroimaging literature can motivate hypotheses about:
- L1-specific speech-category perception;
- second-language learning effects;
- reading/writing direction and spatialized time processing.

Those findings are external evidence about human cognition. They are not evidence that a compressor, a biblical text, or ZIPRAF changes neural representations.

## 10. Physical analogy boundary

The experiment does not infer physical laws from text organization.

```text
language graph != atomic interaction
compression ratio != mass-energy conversion
semantic coherence != quantum coherence
text adjacency != Hamiltonian coupling
```

Physical analogies may generate testable mathematical models only after variables, units, operators, and falsifiers are declared.

## 11. Gates

| Gate | Requirement | Initial state |
|---|---|---|
| G0 SOURCE | pinned source edition + license + acquisition ref | PARTIAL |
| G1 RAW | raw bytes preserved + checksum | TOKEN_VAZIO |
| G2 NORMALIZE | deterministic Unicode/text normalization + checksum | TOKEN_VAZIO |
| G3 METRICS | entropy/compression/null metrics generated | NOT_RUN |
| G4 RECON | decompression/reconstruction equality | NOT_RUN |
| G5 BOOK | equal-window Genesis/Matthew/John comparison | NOT_RUN |
| G6 ZIPRAF | logical-density adapter measured separately | TOKEN_VAZIO |
| G7 PHON | reconstruction convention + grapheme/phoneme data | TOKEN_VAZIO |
| G8 AUDIO/NEURO | licensed human data + preregistered analysis | TOKEN_VAZIO |

`claim_allowed=false` while any claim-specific gate is missing.

## 12. Execution entrypoint

```bash
python3 PapersPub/09_language_entropy_formalism/bible_origin_benchmark_v1.py --selftest

python3 PapersPub/09_language_entropy_formalism/bible_origin_benchmark_v1.py   --input corpus.jsonl   --permutations 32   --seed 144000   --out results/BIBLE_ORIGIN_ENTROPY_V1.json
```

Input JSONL row:

```json
{"ref":"JHN.1.1","book":"John","language":"grc","text":"...","source_id":"grc_tischendorf"}
```

CI gate: `.github/workflows/rll-bible-origin-v1.yml` performs syntax compilation plus deterministic synthetic `--selftest`; this is implementation evidence only and cannot promote corpus/scientific gates.\n\nNo source text is committed by this protocol.

## 13. Rollback

- branch/PR can be closed without altering main;
- source corpora remain external/pinned;
- no ZIPRAF ABI mutation;
- no existing SCD1 predecessor result is overwritten;
- corrections append a successor receipt instead of editing historical evidence silently.

## R3

```text
F_ok   = protocol separates parallel/origin corpora, real compression/logical density, text/phonetics/neuro, and hypothesis/evidence
F_gap  = public-domain acquisition pins/checksums, real origin corpus, ZIPRAF adapter, phoneme model, audio/neuro datasets
F_next = ingest pinned Hebrew Masoretic + Tischendorf Greek sources, classify Aramaic passages, run equal-window book metrics and generic codec baselines
```
