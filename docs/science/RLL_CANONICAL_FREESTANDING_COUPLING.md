# RLL Canonical Freestanding Coupling Region

Status: `IMPLEMENTED / VERIFIED_LOCAL`  
Claim boundary: `claim_allowed=false`

## Purpose

This module is the low-level canonical coupling boundary between already-decoded RLL records and four explicit target regions:

1. cosmological evidence;
2. local geophysical context;
3. exact geometry/mathematics operators;
4. strong-gravity reference context.

It is not another model and it does not parse files. It receives typed records produced by the higher-level adapters and enforces, in C, the chain:

```text
source digest
→ domain
→ physical quantity
→ explicit unit
→ observed/model value
→ uncertainty
→ calibration/clock/model flags
→ target-region policy
→ fixed-point residual/chi-square contribution
→ deterministic receipt
```

## Runtime properties

```text
C11
freestanding
no malloc/heap
no stdio/stdlib/string/math
no implicit unit conversion
no floating point
Q16.16 numeric path
FNV-1a + CRC32 receipt
host + ARMv7 + AArch64 object validation
```

The C object is checked with `nm -u`; an empty undefined-symbol table is required.

## Coupling policy

### Cosmology evidence

Only records satisfying all conditions enter the accumulated fixed-point chi-square:

- domain is cosmology;
- state is observational;
- quantity and unit match exactly;
- uncertainty is positive;
- source count and FNV/CRC provenance are non-zero;
- calibration, raw hashing, uncertainty and registered-model flags are present.

Pantheon+/SN distance modulus, H(z), BAO ratios and `fσ8` can be represented by the declared quantity IDs. The module does not embed or fabricate those datasets; it consumes records after custody and parsing.

### Local geophysics

Stress, acoustic, electric and magnetic channels require calibration, synchronized clock, source digest and uncertainty. They are carried as local context and never added to cosmological chi-square.

### Exact geometry and mathematics

Toroidal/hexagonal/exact operators are preserved as exact computational operators. They do not become physical evidence merely because their arithmetic is exact.

### Synthetic and empty states

- synthetic records are counted as `SYNTHETIC_ONLY`;
- `TOKEN_VAZIO` is counted separately and never converted to zero;
- unit mismatch, malformed provenance, contradictions and blocked states are fail-closed.

## Single validation command

```bash
python3 tools/validate_rll_canonical_freestanding.py --write-report
```

This command compiles the freestanding object, verifies that no external symbols remain, runs deterministic vectors and cross-compiles ARMv7/AArch64 objects. It writes:

```text
artifacts/canonical-coupling/validation.json
```

## Scientific boundary

The receipt proves that records were classified and accumulated under the declared deterministic contract. It does not prove that a dataset is authentic, a calibration is correct, an RLL hypothesis is true or a physical mechanism is causal. Those remain responsibilities of the upstream custody, calibration, likelihood, falsifier and independent-reproduction layers.
