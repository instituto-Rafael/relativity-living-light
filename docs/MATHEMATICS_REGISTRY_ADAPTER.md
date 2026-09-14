# RLL Mathematics/Papers/Theorems Registry Adapter

Status: `IMPLEMENTED_EMULATED_CONSUMER`  
Claim gate: `claim_allowed=false`

This adapter consumes the cross-repository registry proposed in `rafaelmeloreisnovo/Matem-tica-#7` and enforces a fail-closed boundary:

```text
mathematics -> implementation -> execution -> evidence -> physical claim
```

No arrow is inferred automatically.

## Vector invariant

```text
uncoupled vector -> value=null + TOKEN_VAZIO_UNCOUPLED_VECTOR
```

A zero vector is accepted only when every component was explicitly measured or derived as zero.

## RLL use classes

- `MATHEMATICAL_ONLY`: exact/discrete result without required physical adapter.
- `MODEL_OR_DETERMINISTIC_ONLY`: executable/synthetic computation, not observation.
- `CONTEXT_ONLY_TOKEN_VAZIO`: physical correspondence remains open.
- `OBSERVATIONAL_INFERENCE_READY`: real-data inference pipeline with sourced vector and falsifier; this is not physical truth.
- `BLOCKED`: malformed provenance, invalid vector state or claim promotion.

## Emulation boundary

The local emulation validates the consumer and negative controls using a representative fixture. It does **not** download DESI/Pantheon+/Planck, rerun MCMC, ingest laboratory measurements or promote any claim.

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_mathematics_registry_adapter.py' -v
PYTHONPATH=src python tools/emulate_mathematics_registry_adapter.py
```
