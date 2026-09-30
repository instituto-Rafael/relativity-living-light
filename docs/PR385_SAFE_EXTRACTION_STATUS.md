# PR385 safe extraction status

Status date: 2026-08-07

PR #385 remains unsafe to merge as a whole because its historical workflow/directory refactor is far behind current `main`. Safe extraction is therefore additive only: no workflow overwrite, no directory moves, no deletions.

## Extracted earlier

- `data/real/cosmology/desi_bao_dr2_cobaya/README.md`
- `data/real/cosmology/desi_bao_dr2_cobaya/desi_gaussian_bao_ALL_GCcomb_mean.tsv`
- `data/real/cosmology/desi_bao_dr2_cobaya/desi_gaussian_bao_ALL_GCcomb_cov.tsv`
- `scripts/check_desi_dr2_bao_covariance.py`
- `tests/test_desi_dr2_bao_covariance_loader.py`

## Promoted from the remaining technical ahead delta

- full `MANIFEST.json` custody contract, adapted to distinguish upstream hashes from the normalized local `ALL` TSV hashes;
- 14 exact upstream subset mean/covariance files for BGS, LRG, LRG+ELG, ELG, QSO and Lyman-alpha;
- `scripts/materialize_desi_dr2_bao_cobaya.py`, with opt-in network access, pinned byte/SHA-256 verification and atomic writes;
- `tests/test_desi_dr2_cobaya_materialization_v2.py`, covering the 16-file custody surface, subset dimensions, offline verification and fail-closed claim boundary.

## Deliberately not promoted

The following historical PR #385 changes are not treated as current technical progress because they would overwrite or relocate newer repository architecture:

- replacement of `.github/workflows/START_MANUAL_HERE.yml`;
- removal/move of files out of `.github/workflows`;
- legacy `validacao_real/` directory relocation;
- legacy report/image/archive moves;
- old orchestration text that predates the current execution/governance stack.

## Claim boundary

DESI DR2 small public likelihood materialization and covariance custody are present. This closes a data-integrity gap; it does not close the independent model-selection, perturbation, Bayes, replication or publication gates.

```text
claim_allowed=false
publication_ready=false
materialization_is_scientific_validation=false
```

## TOKEN_VAZIO preserved

- `TOKEN_VAZIO_HEAVY_ARCHIVE_NOT_REQUIRED_FOR_COMMITTED_SMALL_LIKELIHOOD`: the large Zenodo archive is not committed merely to duplicate the small likelihood files;
- any future workflow/orchestration extraction from #385 requires a fresh isolated diff against current `main`, not branch-level resurrection.

## Verify

```bash
python3 scripts/materialize_desi_dr2_bao_cobaya.py --verify-only --json
python3 -m pytest -q tests/test_desi_dr2_bao_covariance_loader.py tests/test_desi_dr2_cobaya_materialization_v2.py
```
