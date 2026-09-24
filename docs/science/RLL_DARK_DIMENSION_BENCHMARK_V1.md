# DARK_DIMENSION_BENCHMARK_V1

## Scope

This adapter imports the **Dark Dimension** literature as an external comparator for RLL. It does not assert that RLL is five-dimensional and does not treat a structural resemblance as observational evidence.

The benchmark is deliberately split into two layers:

1. **PBH dimensional crossover benchmark** — deterministic and stdlib-only.
2. **DESI DR2 + supernova likelihood parity** — not yet executed and therefore `TOKEN_VAZIO`.

## External references

- Anchordoqui, Bedroya, Lüst, *Primordial black holes are five dimensional*, accepted by Physical Review D (2026), DOI `10.1103/g12h-93th`, arXiv:`2506.14874`.
- Bedroya, Obied, Vafa, Wu, *Evolving dark sector and the dark dimension scenario*, accepted by Physical Review D (2026), DOI `10.1103/1rsq-cv2m`.

The first source supports a five-dimensional PBH conclusion **within the Dark Dimension Scenario**. It does not establish a direct detection of an extra dimension.

The second supplies a contemporary dark-sector comparator confronted with DESI DR2 plus supernova samples. It does not prove likelihood parity with the RLL repository.

## Structural diagnostic

Define

[
\chi = \frac{r_h}{R_\perp}.
]

This repository uses only asymptotic routing:

- `chi >= separation_factor` -> `EFFECTIVE_4D_ASYMPTOTIC`;
- `chi <= 1/separation_factor` -> `FIVE_D_SENSITIVE_ASYMPTOTIC`;
- otherwise -> `CROSSOVER_TOKEN_VAZIO`.

Default `separation_factor=10` is a conservative routing convention, **not** a physical Gregory-Laflamme threshold. The order-one region requires the full model-specific higher-dimensional stability calculation.

## Command

```bash
python3 tools/run_dark_dimension_benchmark_v1.py \
  --horizon-scale-m 1e-7 \
  --compact-radius-m 1e-6
```

The resulting receipt always keeps:

```text
likelihood_parity        = TOKEN_VAZIO_NOT_EXECUTED
desi_dr2_sn_fit          = TOKEN_VAZIO_NOT_EXECUTED
rll_plus_dark_dimension  = BLOCKED_UNTIL_G5_PARITY
claim_allowed            = false
```

## Parity gate before any combined model

`RLL_PLUS_DARK_DIMENSION` stays blocked until the comparator consumes the same frozen observational blocks, covariance, nuisance treatment, priors policy and parameter-count accounting used by the canonical RLL tournament.

Required future sequence:

```text
structural limits
-> source provenance
-> frozen DD background model
-> same DESI DR2/SN data
-> same covariance/nuisance policy
-> AIC/AICc/BIC + posterior/evidence receipts
-> only then consider RLL_PLUS_DD
```

## Epistemic boundary

```text
SOURCE != MODEL != IMPLEMENTATION != EXECUTION != EVIDENCE != CLAIM
```

A structural PASS means the adapter behaves as declared. It is not evidence for a dark dimension, PBHs, or RLL.
