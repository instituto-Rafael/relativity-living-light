# DESI DR2 BAO public likelihood files

This directory materializes the small public DESI DR2 BAO mean/covariance files
used by the Cobaya BAO likelihood, plus Zenodo record metadata for the official
DESI DR2 Results II supplement.

## Why this exists

The user request was to include real DESI data, not just methodology. The full
Zenodo supplement is about 1.3 GB, so this repository keeps the compact public
likelihood text files needed by the local validation engine and records the
heavy archive in `MANIFEST.json` for full external reproduction.

## Sources

- DESI DR2 Results II paper: `https://arxiv.org/abs/2503.14738`
- DESI DR2 papers page: `https://data.desi.lbl.gov/doc/papers/dr2/`
- Public BAO likelihood files: `https://github.com/CobayaSampler/bao_data/tree/master/desi_bao_dr2`
- Official supplementary record: `https://zenodo.org/records/16644577`

## Files used by `validacao_real/fetch_real_data.py`

- `desi_gaussian_bao_ALL_GCcomb_mean.txt`
- `desi_gaussian_bao_ALL_GCcomb_cov.txt`

Those two files provide the 13 DESI DR2 BAO observables and their covariance
matrix. The validation script converts `*_over_rs` labels to the RLL convention
`*_over_rd` while preserving numerical values and covariance.

## Reproduce the materialization

```bash
python3 scripts/download_desi_dr2_bao_cobaya.py
```
