# RLL | Barontini 2026 | Relational-time data intake V1

**Type:** independent external laboratory-evidence intake; not a cosmological likelihood. **Date:** 2026-11-09. **State:** IMPLEMENTED_LOCAL_TESTED for intake code; TOKEN_VAZIO for upstream files verified locally; claim_allowed=false.

## Primary sources and rights

- G. Barontini, *Testing the problem of time with cold atoms*, Physical Review Research **8**, L022047 (2026), DOI [10.1103/1h9j-df4k](https://doi.org/10.1103/1h9j-df4k).
- [Author's arXiv manuscript 2509.07745v3](https://arxiv.org/abs/2509.07745).
- [Author's data on Zenodo 19651064](https://zenodo.org/records/19651064), DOI 10.5281/zenodo.19651064. Seven files and pinned MD5: data/contracts/rll_barontini_relational_time.v1.json.
- Article is publisher-described CC BY 4.0. The dataset's reuse license is **not positively verified** from visible Zenodo metadata. Store only metadata/links/checksums/original code, **not third-party source bytes**, pending rights review.

## Boundaries

Barontini tested an internal entropic-time coordinate in a well-isolated ultracold Bose-Einstein condensate, comparing observed/unobserved sectors across cycles of expansion and recollapse. This is a **laboratory analog**, not an RLL cosmological data point, a recreation of the universe, or direct cosmic-time measurement.

SOURCE (paper/dataset) != ARTIFACT (manifest/receipt) != EXECUTION (tests/audit) != EVIDENCE (measured source) != CLAIM (physical inference).

No changes to Pantheon+, DESI, CMB, RLL-vs-LCDM likelihoods or parameters.

## Observed formats and falsifiers

| Files | Columns | Audit |
| --- | --- | --- |
| Fig2Fig3V0, V03, V06, V09, V1 | t, tau, phi, sigma | Digests, finiteness, zero sigma, out-of-order t, tau ties, duplicate t |
| Fig3numerics | column, sigma | 2-column finite rows; record incomplete rows |
| Fig4 | unlabelled numeric matrix | Rectangularity, finiteness; axes/units are not inferred |

Published V0 sample has **t rows out of ascending order** and **equal tau values**. Source rows are **never sorted or rewritten**. Sort by t only in memory to calculate non-destructive diagnostic counters. Distinguish zero sigma from a valid positive weight; do not divide by sigma without an explicit policy.

## Execution: offline first

~~~sh
# Offline audit: fails closed (exit 2) if original source files are absent.
python3 scripts/rll_barontini_time_intake.py \
  --data-dir data/real/relational_time/barontini_19651064

# Explicitly permitted download: fetch exactly 7 pinned filenames over HTTPS.
# Source files stay outside Git until rights are reviewed.
python3 scripts/rll_barontini_time_intake.py --fetch \
  --data-dir data/real/relational_time/barontini_19651064 \
  --receipt results/relational_time/barontini_intake_v1.json

# Offline adversarial tests, Python stdlib only:
python3 -m unittest discover -s tests -p 'test_rll_barontini_time_intake.py' -v
~~~

The receipt is create-only and never overwrites an old result. Fetch is opt-in and never overwrites a mismatched source. No external file is downloaded by CI tests. Local generated source files and receipts should be kept untracked, not automatically committed.

## 6Sigma / evidence gates

1. **G0 SOURCE:** primary journal + dataset DOI and published MD5 list located — PASS_METADATA_SCOPED.
2. **G1 CODE:** 11 tests passed in an isolated local stdlib runner — PASS_LOCAL; GitHub exact-head CI is TOKEN_VAZIO until actually observed.
3. **G2 REAL BYTES:** download and verify seven upstream files and their SHA256 — TOKEN_VAZIO_NOT_MATERIALIZED.
4. **G3 REPRODUCE:** reconstruct published entropic-time evolution/figures and uncertainties following the original method, not a guessed entropy formula — NOT_RUN.
5. **G4 TRANSFER:** preregister units, scale bridges, baselines and falsifiers before using as motivation for RLL physics — TOKEN_VAZIO; claim_allowed=false.

**Rollback:** additive paths on a draft branch only; retain original data, main, claim gates and prior receipts. This is a custody/import diagnostic, not experimental validation of RLL.

**R3:** F_ok = primary sources and integrity constraints pinned; code tests PASS_LOCAL. F_gap = real-source bytes, rights, reproductions and scale bridge. F_next = opt-in ingestion → receipt → independent replication → falsifiers.
