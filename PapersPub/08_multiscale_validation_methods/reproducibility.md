# Reproducibility — Seven-Dimensional Epistemic-Computational Formalism

**Status:** `analysis_run`  
**Claim gate:** `claim_allowed=false`

## 1. Reproducible scope

This package reproduces exact finite invariants only:

- character multiplicities and multinomial counts;
- empirical Shannon entropy;
- array, pair, block and tensor counts;
- row-major index coverage;
- 7×6 construction of 42 operator-state hyperforms;
- base-seven conversion;
- BITRAF64 Unicode length, alphabet, frequency and entropy;
- geometric contraction/expansion constants.

It does not reproduce a physical cosmology, causal discovery, molecular magnetism, fluid experiment or cryptographic security proof.

## 2. Minimum environment

- Python 3.11 or newer;
- Python standard library only;
- UTF-8 filesystem;
- Unicode NFC normalization;
- no network access required.

Recorded preparation environment:

```text
CPython 3.13.5
Linux x86_64
Unicode database 15.1.0
```

The output should be numerically identical within the tolerances encoded in the script. Platform and Python version metadata may differ.

## 3. Canonical command

From repository root:

```bash
python3 PapersPub/08_multiscale_validation_methods/scripts/validate_formalism.py
```

Expected exit code:

```text
0
```

Expected summary:

```json
{
  "checks_total": 44,
  "checks_passed": 44,
  "checks_failed": 0,
  "exact_invariants_status": "PASS"
}
```

## 4. Independent output path

To avoid overwriting the tracked report during review:

```bash
python3 PapersPub/08_multiscale_validation_methods/scripts/validate_formalism.py \
  --output /tmp/canon_cosmos_7d_validation.json
```

Compare substantive results:

```bash
python3 - <<'PY'
import json
from pathlib import Path

tracked = json.loads(Path(
    "PapersPub/08_multiscale_validation_methods/results/validation_report.json"
).read_text(encoding="utf-8"))
local = json.loads(Path("/tmp/canon_cosmos_7d_validation.json").read_text(encoding="utf-8"))

assert tracked["results"] == local["results"]
assert tracked["summary"] == local["summary"]
print("PASS: results and claim states match")
PY
```

Runtime metadata is intentionally excluded from equality because platform strings may differ.

## 5. Manual verification equations

```text
C(40,2) = 780
C(21,2) = 210
780 × 210 = 163800
8 × 5 × 7 × 3 = 840
(8−1)(5−1) × 4! = 672
(7−1)(3−1) × 4! = 288
C(8,2)C(5,2) × 4! = 6720
C(7,2)C(3,2) × 4! = 1512
7 × 6 = 42
35 decimal = 50 base 7
245 decimal = 500 base 7
```

## 6. Unicode and BITRAF controls

The BITRAF string must be read as Unicode code points after NFC normalization. A review implementation must report:

```text
length = 64
alphabet = {Σ, Ω, Δ, Φ, B, I, T, R, A, F}
frequency vector in declared order = [6,7,9,9,5,5,4,7,4,8]
```

Byte length is not used as character length because Greek symbols occupy multiple UTF-8 bytes.

## 7. Scientific FAILSAFE

The validator returns credit only for exact checks. It explicitly records:

```text
poincare_recurrence       = TOKEN_VAZIO
causal_component          = TOKEN_VAZIO
magnetic_molecular_claim  = TOKEN_VAZIO
bitraf_security           = TOKEN_VAZIO
physical_cosmos_claim     = PROHIBITED_BY_SCOPE
```

A future implementation must not convert any of these states to `PASS` merely because the arithmetic checks succeed.

## 8. FAILOVER

- If Unicode normalization differs, preserve raw input and report both raw and normalized code-point sequences.
- If a bibliography source cannot be accessed, retain its DOI metadata and mark full-text verification `TOKEN_VAZIO`.
- If actual A/B cell values are introduced, recompute distinct value permutations rather than assuming 24 per block.
- If memory becomes part of the recurrent state, retest finite-measure and measure-preservation assumptions for the augmented space.
- If an empirical dataset is added, create a new versioned manifest rather than mutating this symbolic-input report.

## 9. ROLLBACK

This paper package is isolated in `PapersPub/08_multiscale_validation_methods`. Rollback is performed by reverting the paper commits or deleting newly generated untracked reports. No legacy scientific result, dataset or workflow is modified by the validator.

## 10. Promotion gates

Promotion from `analysis_run` to `review_ready` requires:

1. independent execution of the validator;
2. bibliography/DOI verification;
3. human mathematical review of recurrence and normalization sections;
4. license and author-name confirmation;
5. full complete hashes for any deposited release;
6. journal-format conversion and language review;
7. explicit decision on whether the Portuguese parabolic appendix remains in the submission or only in supplementary material.

Promotion to `submitted` requires a dated preprint/periódico submission receipt. A GitHub PR or DOI reservation alone does not satisfy this gate.
