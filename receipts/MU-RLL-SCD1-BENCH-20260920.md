# Receipt — MU-RLL-SCD1-BENCH-20260920

**Timestamp:** 2026-09-20T22:51:00-03:00  
**State:** ANALYSIS_RUN_NORMALIZED_CORPUS  
**claim_allowed:** false

## Scope
Exact reconstruction of the normalized verse corpus for Genesis, Matthew and John across ENG/SPA/POR. Editorial/source formatting and notes are outside this gate.

## Result
- Common verse references: 3,483
- Normalized records: 10,449
- Verbose JSON: 1,642,359 bytes
- SCD1 shared-reference seed: 1,273,254 bytes
- Plain text only: 1,213,948 bytes
- SCD1 vs verbose JSON: -369,105 bytes (-22.474%)
- SCD1 vs plain text: +59,306 bytes (+4.885%)
- Exact normalized reconstruction: PASS
- Baseline/reconstructed SHA-256: `960d1c6601229ff5dee138e21e826724e94ef4952536dcf97db5b46b70e82c8f`
- Seed SHA-256: `2a42fd5e159df8a258c5f0a4e9780c2bc656f653efb6c1f5d6149f5359f85f98`

## Evidence
- Script: `PapersPub/09_language_entropy_formalism/benchmark_scd1.py`
- Result: `PapersPub/09_language_entropy_formalism/results/SCD1_20260920.json`
- Source commits and SHA-256 values: recorded in the result JSON.
- ENG: World English Bible, public domain.
- SPA: Reina-Valera 1909, public domain.
- POR: Bíblia Livre; source repo license authority used conservatively as CC BY 3.0 Brasil. eBible metadata reports CC BY 4.0; discrepancy remains explicit.

## Interpretation boundary
PASS supports structural metadata deduplication and exact reconstruction of the declared normalized representation. It does not support universal semantic compression, superiority to gzip/zstd/brotli, or thermodynamic negative entropy.

## Next gate
Run generic compression baselines on identical bytes, account for model/schema/dictionary cost, and repeat on a non-religious parallel corpus.
