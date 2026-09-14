# Real-data materialization audit

This audit scans configured Structure-D datasets plus data files up to five path levels for synthetic/mock/example markers.
It does not rename synthetic fixtures as real data; it records an explicit route to committed real replacements or leaves a gap visible.

## Summary

- Real replacements ready: 5
- Real replacements missing: 0
- Configured datasets without route: 0
- Inventory-only filesystem markers: 20

## Failsafe / failover / rollback

- Production routes must point to `data/real/**` or a documented external URL.
- Synthetic fixtures are retained for regression tests and rollback; they are not deleted.
- Audit artifacts are written atomically and create `*.bak` when replacing prior outputs.
- If a real source is missing or fails validation, keep the previous artifact and mark the route as pending instead of fabricating data.

## Configured synthetic-to-real routes

| dataset_id | status | synthetic_path | real_replacement_id | real_path |
| --- | --- | --- | --- | --- |
| fsigma8 | real_replacement_ready | data/inputs/structure_d/fsigma8.csv | real_fsigma8 | data/real/cosmology/fsigma8_growth_real.csv |
| fsigma8_cov_synth | real_replacement_ready | data/synthetic/structure_d/fsigma8_cov.csv | real_fsigma8 | data/real/cosmology/fsigma8_growth_real.csv |
| hz | real_replacement_ready | data/inputs/structure_d/Hz.csv | real_hz | data/real/Hz_data_real.csv |
| hz_cov_synth | real_replacement_ready | data/synthetic/structure_d/Hz_cov.csv | real_hz | data/real/Hz_data_real.csv |
| real_bao | real_replacement_ready | data/real/BAO_data_real.csv | real_desi_dr2_bao | data/real/cosmology/desi_dr2_bao_primary_points.csv |
