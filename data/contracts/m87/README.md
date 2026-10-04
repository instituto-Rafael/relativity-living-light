# M87* execution locks — index

Start at: `docs/strong_gravity/START_HERE_SGPT_M87.md`.

Do not treat this directory as a bag of optional files. The execution order is:

1. `source_regime_admissibility.v1.json`
2. `process_timescale_registry.v1.json`
3. `data_custody_and_transform_dag.v1.json`
4. `statistical_analysis_lock.v1.json`
5. `reproducibility_environment_lock.v1.json`
6. `claim_ladder.v1.json`

Validator: `tools/validate_sgpt_m87_execution_locks.py`.

Focused CI: `.github/workflows/sgpt-m87-execution-locks.yml`.

Truth boundary:

```text
TOKEN_VAZIO != 0
PASS_LOCKS_CONTRACT_ONLY != SCIENTIFIC_VALIDATION
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
```

A lock can prevent an invalid analysis. It cannot by itself validate astrophysics.
