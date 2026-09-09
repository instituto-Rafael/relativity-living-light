# Reproducibility — Giza Continuous Academic Intake

**State:** `METHOD_READY / SCIENTIFIC_EXECUTION_PENDING / claim_allowed=false`

## Local deterministic gate

```bash
python3 scripts/validate_giza_academic_intake.py \
  --root . \
  --output artifacts/giza-academic-intake/report.json
```

This gate checks package presence, SHA-256 inventory, required DOI identifiers, anti-plagiarism boundary markers, mandatory adversarial citation routing, and global claim-state guards.

## Optional online bibliographic metadata check

```bash
python3 scripts/validate_giza_academic_intake.py \
  --root . \
  --output artifacts/giza-academic-intake/report.json \
  --online-crossref
```

The online check queries DOI metadata only. Network failure is recorded as `TOKEN_VAZIO_NETWORK_METADATA` and does not convert a scientific claim to pass/fail.

## Scientific reconstruction gate — not yet executable

A historical sky reconstruction may start only after the following are available:

1. source-bound four-shaft centerlines or defensible terminal axes;
2. per-segment or aggregate geometric uncertainty;
3. declared Giza coordinates/reference frame;
4. stellar catalog with astrometric parameters;
5. long-term precession implementation including the Vondrak et al. corrigendum;
6. full-star or magnitude-limited control catalog;
7. assignment policy for culturally constrained candidate stars;
8. look-elsewhere correction;
9. independent reproduction route.

## Required scientific outputs

A future executable run must emit at minimum:

```text
input_manifest.json
shaft_geometry.sha256
astrometry_model.json
candidate_targets.json
control_catalog.json
residuals_by_epoch.csv
joint_chi2_by_epoch.csv
null_distribution.json
sensitivity_analysis.json
receipt.json
```

The receipt must preserve source hashes, software commit, command, environment, epoch convention, precession model/version, uncertainty model, result and falsifier state.

## Non-equivalences

```text
workflow PASS != archaeological validation
DOI resolved != source claim correct
preprint found != peer review
one stellar match != timestamp
common numerical constant != common historical mechanism
```
