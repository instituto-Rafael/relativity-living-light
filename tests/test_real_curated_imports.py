from __future__ import annotations

import unittest

from scripts.fetch_real_sources import CURATED_LOCAL_REAL


class CuratedRealImportTests(unittest.TestCase):
    def test_curated_imports_cover_canonical_cosmology_inputs(self) -> None:
        self.assertEqual(
            {str(path) for path in CURATED_LOCAL_REAL.values()},
            {
                "data/real/Hz_data_real.csv",
                "data/real/cosmology/desi_dr2_bao_primary_points.csv",
                "data/real/cosmology/desi_dr2_bao_covariance_summary.csv",
                "data/real/cosmology/fsigma8_growth_real.csv",
                "data/real/CMB_shift_real.json",
            },
        )
