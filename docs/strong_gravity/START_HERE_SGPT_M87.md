# START HERE — SGPT M87* Fire Test V1

**Audience:** humans + AI agents  
**Scope:** navigation only; no scientific claim promotion  
**Authority:** `instituto-Rafael/relativity-living-light`  
**Claim:** `claim_allowed=false`

## One route

```text
INTENT
 -> PREREGISTRATION
 -> REGIME ADMISSIBILITY
 -> PROCESS TIMESCALES
 -> DATA CUSTODY / TRANSFORM DAG
 -> STATISTICAL LOCK
 -> REPRODUCIBILITY LOCK
 -> CLAIM LADDER
 -> EXECUTE
 -> RECEIPTS
 -> G0..G7
```

Do not skip a node because a later artifact exists.

## Canonical files

| Order | Purpose | File |
|---|---|---|
| 0 | Source-specific preregistration | `data/contracts/sgpt_m87_firetest.v1.json` |
| 1 | Decide which physics is admissible for M87* | `data/contracts/m87/source_regime_admissibility.v1.json` |
| 2 | Bind process clocks/rates | `data/contracts/m87/process_timescale_registry.v1.json` |
| 3 | Bind bytes -> observables -> likelihood provenance | `data/contracts/m87/data_custody_and_transform_dag.v1.json` |
| 4 | Freeze metrics/priors/stopping/model selection | `data/contracts/m87/statistical_analysis_lock.v1.json` |
| 5 | Freeze environment and independence semantics | `data/contracts/m87/reproducibility_environment_lock.v1.json` |
| 6 | Bound the strongest permitted scientific statement | `data/contracts/m87/claim_ladder.v1.json` |

## Validators

```text
tools/validate_sgpt_m87_firetest.py
tools/validate_sgpt_m87_execution_locks.py
```

## Truth boundary

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
IMPLEMENTED_UNTESTED != PASS
PASS_LOCKS_CONTRACT_ONLY != SCIENTIFIC_VALIDATION
```

## Fail-closed rule

If source-bound evidence does not establish a regime, rate, byte hash, covariance, metric, environment or reproduction condition, leave it `TOKEN_VAZIO`.

If a process is physically excluded by a declared source-domain argument, use `NOT_APPLICABLE_WITH_JUSTIFICATION`, never `PASS`.

## M87* scope firewall

The session discussed physics from multiple regimes. M87* must not inherit dense-matter, nuclear, pycnonuclear, electron-capture or spin-QED modules from merger remnants, neutron-star crusts or generic thought experiments unless the source-regime lock explicitly establishes applicability.

## Promotion rule

A useful diagnostic is not automatically new physics. Promotion follows the claim ladder and cannot jump directly from software success to a physics claim.

## Next action

Run the execution-lock validator. Then acquire/verify official source bytes and terms before changing any `TOKEN_VAZIO` in data/statistical locks.
