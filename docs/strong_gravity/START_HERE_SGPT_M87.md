# START HERE — SGPT M87* Fire Test V1

**Audience:** humans + AI agents  
**Scope:** navigation only; no scientific claim promotion  
**Authority:** `instituto-Rafael/relativity-living-light`  
**Claim:** `claim_allowed=false`

## One route

```text
INTENT
 -> PREREGISTRATION
 -> EXTERNAL SOURCE EVIDENCE / CUSTODY
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
| 0.1 | Published source-state bindings and domain references | `data/evidence/m87/source_state_evidence.v1.json` |
| 0.2 | Dataset identity, rights metadata and byte-custody state | `data/evidence/m87/data_custody_metadata.v1.json` |
| 1 | Decide which physics is admissible for M87* | `data/contracts/m87/source_regime_admissibility.v1.json` |
| 2 | Bind process clocks/rates | `data/contracts/m87/process_timescale_registry.v1.json` |
| 3 | Bind bytes -> observables -> likelihood provenance | `data/contracts/m87/data_custody_and_transform_dag.v1.json` |
| 4 | Freeze metrics/priors/stopping/model selection | `data/contracts/m87/statistical_analysis_lock.v1.json` |
| 5 | Freeze environment and independence semantics | `data/contracts/m87/reproducibility_environment_lock.v1.json` |
| 6 | Bound the strongest permitted scientific statement | `data/contracts/m87/claim_ladder.v1.json` |

## Validators / executors

```text
tools/validate_sgpt_m87_firetest.py
tools/validate_sgpt_m87_execution_locks.py
tools/validate_sgpt_m87_external_evidence.py
tools/evaluate_sgpt_m87_source_regimes.py
```

## Truth boundary

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
IMPLEMENTED_UNTESTED != PASS
PASS_LOCKS_CONTRACT_ONLY != SCIENTIFIC_VALIDATION
PARTIAL_REGIME_EXECUTION_EVIDENCE_BOUND != SGPT_VALIDATED
```

## Fail-closed rule

If source-bound evidence does not establish a regime, rate, byte hash, covariance, metric, environment or reproduction condition, leave it `TOKEN_VAZIO`.

If a process is physically excluded by a declared source-domain argument, use `OUT_OF_DOMAIN` or `NOT_APPLICABLE_WITH_JUSTIFICATION`, never `PASS`.

A provider access failure is an operational observation only; it is not scientific evidence.

## M87* scope firewall

The session discussed physics from multiple regimes. M87* must not inherit dense-matter, nuclear, pycnonuclear, electron-capture or spin-QED modules from merger remnants, neutron-star crusts or generic thought experiments unless the source-regime evidence establishes applicability.

Published EHT ranges for `B`, `T_e`, `n_e` and `dot_M` are model-dependent constraints and must not be relabelled as direct measurements.

## Promotion rule

A useful diagnostic is not automatically new physics. Promotion follows the claim ladder and cannot jump directly from software success to a physics claim.

## Current next action

Execute the external-evidence/regime workflow. Only regimes that survive that gate may request process-specific rates. Large VLBI file hashes, exact covariance/likelihood, pair balance, source spin and independent reproduction remain `TOKEN_VAZIO` until their own provenance closes.
