# DESI DR2 BAO public likelihood files

This directory materializes the small public DESI DR2 BAO mean/covariance files used by the Cobaya BAO likelihood, with explicit byte/SHA-256 custody and a fail-closed materializer.

## Why this exists

PR #385 contained useful DESI DR2 materialization work inside a much wider workflow/directory refactor that was not safe to merge as-is. The repository therefore promotes only the additive technical delta and preserves the newer `main` orchestration unchanged.

## Sources

- DESI DR2 Results II paper: `https://arxiv.org/abs/2503.14738`
- DESI DR2 papers page: `https://data.desi.lbl.gov/doc/papers/dr2/`
- Public BAO likelihood files: `https://github.com/CobayaSampler/bao_data/tree/master/desi_bao_dr2`
- Official supplementary record: `https://zenodo.org/records/16644577`

## Canonical ALL likelihood

The two files already promoted earlier are normalized TSV representations of the public 13-observation joint likelihood:

- `desi_gaussian_bao_ALL_GCcomb_mean.tsv`
- `desi_gaussian_bao_ALL_GCcomb_cov.tsv`

`MANIFEST.json` records both their local normalized hashes and the hashes/byte counts of the corresponding upstream `.txt` files. The two hash domains are deliberately not conflated.

## Exact upstream subset files

The remaining PR #385 technical data are kept byte-for-byte as upstream `.txt` files for:

- BGS BRIGHT;
- LRG z=0.4–0.6;
- LRG z=0.6–0.8;
- LRG+ELG;
- ELG z=1.1–1.6;
- QSO;
- Lyman-alpha.

Each subset has a mean vector and covariance matrix. Their upstream SHA-256 and byte counts are pinned in `MANIFEST.json`.

## Offline verification

```bash
python3 scripts/materialize_desi_dr2_bao_cobaya.py --verify-only --json
```

Expected state when all 16 committed likelihood files match custody:

```text
READY_COMMITTED_SMALL_LIKELIHOOD
files_ok=16
claim_allowed=false
```

## Network materialization

Network access is never implicit. To recover a missing non-normalized subset file:

```bash
python3 scripts/materialize_desi_dr2_bao_cobaya.py --download-missing --json
```

Downloaded bytes are rejected unless both the pinned byte count and SHA-256 match. The normalized `ALL` TSV pair is never reconstructed automatically from a mutable remote; if either local canonical file is missing or corrupt, the tool returns `TOKEN_VAZIO_NORMALIZED_CORE_REQUIRES_LOCAL_RECOVERY`.

## Claim boundary

These are real public likelihood data and custody checks. Materialization success is **not** model validation, Bayesian evidence, a preference for RLL, or permission to promote a scientific claim. `claim_allowed=false` remains invariant until the independent scientific gates are satisfied.
