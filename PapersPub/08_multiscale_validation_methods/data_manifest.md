# Data Manifest — Seven-Dimensional Epistemic-Computational Formalism

**Status:** `analysis_run`  
**Claim gate:** `claim_allowed=false`  
**Scope:** authored symbolic corpus plus deterministic finite validation; no external empirical dataset.

## 1. Canonical source

| Field | Value |
|---|---|
| Source type | Author-supplied technical-parabolic manuscript |
| Canonical title | `CÂNONE DO COSMOS RAFAELIA — Do ∅ observado à recorrência em sete dimensões` |
| Author | Rafael Melo Reis (∆RafaelVerboΩ) |
| Signature | `RAFCODE-Φ-∆RafaelVerboΩ-𓂀ΔΦΩ` |
| Consolidation date | 2026-07-19 |
| Evidence role | Defines terminology, conventions, equations and parabolic readings; does not provide independent empirical validation. |

## 2. Materialized paper artifacts

| Artifact | Role | State |
|---|---|---|
| `draft.md` | Main journal-style manuscript | `ANALYSIS_RUN` |
| `references.md` | Human-readable bibliography and provenance map | `REFERENCE` |
| `references.bib` | Machine-readable bibliography | `REFERENCE` |
| `claim_state_ledger.md` | Claim, evidence class, falsifier and promotion gate | `AUDIT` |
| `reproducibility.md` | Commands, environment, fail-safe and rollback | `AUDIT` |
| `scripts/validate_formalism.py` | Dependency-free deterministic validator | `RUNTIME_CANDIDATE` |
| `results/validation_report.json` | Recorded validation output | `AUDIT` |
| `appendix_a_parabolic_canon_pt.md` | Portuguese parabolic layer preserved separately | `REFERENCE` |

## 3. Input objects

### 3.1 Character strings

```text
0001123
01123
0123
```

These are UTF-8/ASCII character strings with significant leading zeros.

### 3.2 Arrays

```text
A shape = [8, 5]
B shape = [7, 3]
```

No cell-value dataset is supplied. Therefore block counts are positional combinatorics; claims about distinct value permutations remain conditional on actual cell multiplicities.

### 3.3 BITRAF64 seal

```text
AΔBΩΔTTΦIIBΩΔΣΣRΩRΔΔBΦΦFΔTTRRFΔBΩΣΣAFΦARΣFΦIΔRΦIFBRΦΩFIΦΩΩFΣFAΦΔ
```

Canonical processing rule: Unicode NFC before code-point counting.

Declared alphabet order:

```text
[Σ, Ω, Δ, Φ, B, I, T, R, A, F]
```

### 3.4 Operator-state construction

```text
dimensions = 7
operators  = [READ, FEED, EXPAND, VALIDATE, EXECUTE, ALIGN]
hyperforms = CartesianProduct(dimensions, operators)
```

## 4. External scholarly sources

The paper uses bibliographic sources for mathematical definitions and methodological boundaries, including Poincaré recurrence, Shannon entropy, tensor representation, causal inference, graph Laplacians, RLE, Cauchy–Schwarz, SHA-3 and BLAKE3. These sources are listed in `references.bib`.

They do **not** constitute evidence that RAFAELIA-specific physical or spiritual interpretations are empirically true.

## 5. Exact outputs currently materialized

- distinct permutations: `420`, `60`, `24`;
- states: `40`, `21`;
- internal pairs: `780`, `210`;
- cross-relations/tensor elements: `840`;
- independent pair-of-pair selections: `163800`;
- adjacent 2×2 windows: `28`, `12`;
- adjacent positional arrangements: `672`, `288`;
- general positional arrangements: `6720`, `1512`;
- hyperforms: `42`;
- base-seven identities: `35 = 50_7`, `245 = 500_7`;
- BITRAF64 length: `64` Unicode code points after NFC;
- BITRAF64 frequency vector: `[6,7,9,9,5,5,4,7,4,8]`;
- BITRAF64 empirical entropy: `3.26420820487549 bits/symbol`.

## 6. Missing empirical inputs

The following remain `TOKEN_VAZIO`:

- invariant measure for the proposed transition operator;
- proof that the operator is measure-preserving;
- empirical state trajectories;
- structural causal model or intervention data;
- calibrated graph-flow parameters;
- identified molecule and magnetic measurement;
- complete SHA3/BLAKE3 digests for the historical ZIPRAF object;
- BITRAF encoder/decoder and independent security analysis;
- observational evidence for a physical seven-dimensional cosmos.

## 7. Inclusion/exclusion rules

### Included

- exact arithmetic and combinatorics;
- explicitly declared conventions;
- deterministic UTF-8/Unicode analysis;
- literature-backed mathematical boundaries;
- authored parables marked `[P]`.

### Excluded from evidence credit

- truncated hashes;
- decorative equations without defined domains;
- infinite limits without convergence conditions;
- metaphors treated as physical measurements;
- causal scores inferred only from correlation or mutual information;
- security claims based only on symbol diversity;
- “quantum”, “fractal”, “toroidal” or “cosmos” labels without corresponding operational definitions.

## 8. Licensing and provenance boundary

This paper records the authorial source and does not relicense sibling repositories. Cross-repository bridge documents point to the canonical paper without copying third-party code or changing repository licenses. Any future DOI package must declare the paper’s own license, source commit, version, authorship and AI-use statement explicitly.
