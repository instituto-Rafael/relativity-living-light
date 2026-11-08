# 001_PONTEIRO — RLL Entropia Braille × Escritas × FFT V2

**SOURCE:** `data/experiments/rll_cross_script_entropy_v2/parallel_quantity_five_v2.json` — dez línguas e quantidade cinco.

**CODE:** `tools/ci/rll_script_entropy_v2.py`, `tools/ci/rll_visual_fft_v2.py`.

**EVIDENCE:** `data/experiments/rll_cross_script_entropy_v2/entropy_text_v2.json`, `fft_metrics.csv`, `visual_fft_receipt_v2.json`, `visuals/`.

**PROTOCOL:** `docs/workflows/RLL_CROSS_SCRIPT_ENTROPY_BRAILLE_LIBRAS_FFT_V2.md`.

**CI:** existing `.github/workflows/rll-calibration-orchestrator.yml` preflight stage 03 only. Source-linguistic and static-FFT measurements are separate; no cosmology inference.

**STATUS:** 10 natural languages (model-authored, not independently reviewed), Braille (word and numeral), historical Mayan/Egyptian numerals only, same 128x128 synthetic images, **Libras real `TOKEN_VAZIO_REAL_LIBRAS_FRAME`**.

**GATES:** `claim_allowed=false`; semantic cross-modal equivalence NOT_TESTED; 19/19 local Python structural tests on same fixture. No automatic PR source downloads, secrets or production data modifications.

**ROLLBACK:** revert additive PR; V1 multilingual and existing scientific producer unchanged.
