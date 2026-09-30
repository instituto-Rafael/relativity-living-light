# Reproducibility

## Environment

Python 3.11+ and PyYAML >= 6.0.

## Local execution

```bash
python scripts/validate_multilayer_circle_polygon_geometry_v1.py \
  --spec data/contracts/rll_multilayer_circle_polygon_geometry_v1.yml \
  --output results/RLL_MULTILAYER_CIRCLE_POLYGON_GEOMETRY_V1.json

python -m unittest tests/test_multilayer_circle_polygon_geometry_v1.py -v
```

Expected local summary:

```json
{"failed": 0, "passed": 120, "scenarios": 20, "tests_total": 120}
```

## CI

Workflow:

`.github/workflows/rll-multilayer-circle-polygon-geometry-v1.yml`

It runs the unit test, regenerates a CI result and uploads checksums/results as a GitHub Actions artifact. It does not push generated data back into the repository.

## Fail-safe

Any failed identity produces process exit code 1. Missing YAML or malformed input also fails explicitly.

## Rollback

Git history is the rollback mechanism. Corrections must supersede earlier records rather than erase them.

## Claim boundary

A passing mathematical suite does not authorize a physical/cosmological claim.
