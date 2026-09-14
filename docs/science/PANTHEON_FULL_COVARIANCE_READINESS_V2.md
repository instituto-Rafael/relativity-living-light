# Pantheon+ Full-Covariance Readiness V2

**State:** catalog verified / diagonal diagnostic ready / full covariance `TOKEN_VAZIO` / `claim_allowed=false`

## Why this gate exists

The official Pantheon+SH0ES distance catalog is committed in RLL, while the two
large official covariance matrices are intentionally excluded from Git because
they are too large for ordinary review diffs.

That creates two distinct executable states which must never be conflated:

```text
catalog + diagonal uncertainties
    → diagonal diagnostic route

catalog + verified STAT+SYS covariance
    → full covariance likelihood route
```

Before V2, `verify_pantheon_inputs.py` treated the covariance files as optional
and reported `all_present` from required-file presence only. A valid catalog
could therefore look globally ready even though the full likelihood remained
impossible.

V2 removes that ambiguity.

## Canonical location

```text
data/real/cosmology/pantheon_plus/
  Pantheon+_Data/4_DISTANCES_AND_COVAR/
```

The verifier defaults to this materialized official-release directory rather
than the older staging path `data/pantheon`.

## Catalog contract

```text
file              Pantheon+SH0ES.dat
size              579283 bytes
SHA-256           1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8
total rows         1701
Cepheid calibrators  77
cosmology rows      1624
```

Required fields:

```text
zHD
MU_SH0ES
MU_SH0ES_ERR_DIAG
IS_CALIBRATOR
```

The catalog is accepted for a diagonal diagnostic only when all of the following
match:

- exact byte size;
- pinned SHA-256;
- required header fields;
- total row count;
- calibrator count;
- cosmology-sample count;
- calibrator values restricted to `0` or `1`.

A one-byte mutation is rejected before any scientific calculation.

## Full covariance contract

The full likelihood requires:

```text
Pantheon+SH0ES_STAT+SYS.cov
Pantheon+SH0ES_STAT+SYS.cov.sha256
```

The sidecar is mandatory because file presence alone is not custody. The
verifier checks:

1. a syntactically valid 64-hex SHA-256 sidecar;
2. exact covariance-file hash equality;
3. declared matrix dimension `1701`;
4. exactly `1701² = 2,893,401` covariance values.

States are typed:

```text
TOKEN_VAZIO_FULL_COVARIANCE
TOKEN_VAZIO_COVARIANCE_SHA256_POLICY
BLOCKED_COVARIANCE_SHA256
BLOCKED_COVARIANCE_DIMENSION
BLOCKED_COVARIANCE_VALUE_COUNT
READY_FULL_COVARIANCE
```

The statistical-only matrix is tracked separately and never substituted for
`STAT+SYS` without an explicit route decision.

## Current repository receipt

```text
route_state                       TOKEN_VAZIO_FULL_COVARIANCE
diagonal_diagnostic_ready         true
full_covariance_likelihood_ready  false
catalog rows                      1701
cosmology rows                    1624
STAT+SYS covariance present       false
STATONLY covariance present       false
claim_allowed                     false
```

Machine-readable receipt:

```text
artifacts/pantheon/pantheon_input_readiness_v2.json
```

## Commands

Inspect without promoting claims:

```bash
python3 scripts/verify_pantheon_inputs.py --json
```

Require the catalog-only diagnostic boundary:

```bash
python3 scripts/verify_pantheon_inputs.py --require-diagonal-diagnostic
```

Require the complete official covariance route:

```bash
python3 scripts/verify_pantheon_inputs.py --require-full-covariance
```

On the current repository state, the last command exits with status `3`. This is
a successful fail-closed gate, not a broken script.

## Tests

`tests/test_verify_pantheon_inputs_v2.py` verifies:

- current catalog size, hash and 1701/77/1624 partition;
- explicit `TOKEN_VAZIO_FULL_COVARIANCE` state;
- default and diagonal-required success;
- full-covariance-required failure;
- one-byte catalog tamper rejection;
- covariance bytes without a pinned hash remaining `TOKEN_VAZIO`;
- hash-verified covariance with wrong shape being blocked.

## Scientific boundary

The existing diagonal Pantheon+ calculations remain useful diagnostics, but they
do not include official off-diagonal statistical and systematic covariance.
Therefore:

```text
diagonal_diagnostic_ready != full_covariance_likelihood_ready
catalog_present != covariance_present
1624 diagonal residuals != official full likelihood
claim_allowed=false
```

The next promotable event is concrete: materialize the official
`Pantheon+SH0ES_STAT+SYS.cov`, pin its SHA-256 sidecar, pass the 1701×1701 shape
gate, and only then connect it to the covariance-aware likelihood implementation.
