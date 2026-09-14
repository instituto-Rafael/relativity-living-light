from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/rll-evidence-runner"
sys.path.insert(0, str(PRODUCT / "src"))

from rll_evidence.pantheon_fit_three_model import (
    CPL,
    LCDM,
    RLL,
    build_result,
    distance_modulus,
    e2,
    prepare_data,
)


class PantheonThreeModelCPLV1Tests(unittest.TestCase):
    def synthetic_data(self):
        z_hd = np.array([0.005, 0.007, 0.02, 0.04, 0.08, 0.15, 0.3, 0.5, 0.8, 1.1])
        z_hel = z_hd + 0.0002
        calibrator = np.array([True, True] + [False] * 8)
        ceph = np.array([31.0, 32.0] + [-9.0] * 8)
        covariance = np.diag(np.full(10, 0.03**2))
        empty = prepare_data(
            z_hd, z_hel, np.zeros(10), ceph, calibrator, covariance, integration_points=512
        )
        mu = distance_modulus(empty, LCDM, [70.0, 0.3])
        return prepare_data(
            z_hd, z_hel, mu - 19.25, ceph, calibrator, covariance, integration_points=512
        )

    def test_cpl_is_flat_at_z_zero(self) -> None:
        value = float(e2(CPL, np.array([0.0]), [70.0, 0.3, -1.0, 0.0])[0])
        self.assertAlmostEqual(value, 1.0, places=12)

    def test_cpl_nests_lcdm_at_w0_minus_one_wa_zero(self) -> None:
        z = np.array([0.0, 0.1, 0.5, 1.0, 2.0])
        lcdm = e2(LCDM, z, [70.0, 0.3])
        cpl = e2(CPL, z, [70.0, 0.3, -1.0, 0.0])
        np.testing.assert_allclose(cpl, lcdm, rtol=0.0, atol=1.0e-12)

    def test_rll_dispatch_is_preserved(self) -> None:
        z = np.array([0.0, 0.2, 1.0])
        values = e2(RLL, z, [70.0, 0.3, 0.02, 1.0, 0.3])
        self.assertTrue(np.all(np.isfinite(values)))
        self.assertAlmostEqual(float(values[0]), 1.0, places=12)

    def test_three_model_build_uses_one_covariance_and_keeps_claim_blocked(self) -> None:
        data = self.synthetic_data()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "Pantheon.dat"
            covariance = root / "Pantheon.cov"
            output = root / "result.json"

            with catalog.open("w", encoding="utf-8") as handle:
                handle.write("zHD zHEL m_b_corr CEPH_DIST IS_CALIBRATOR\n")
                for row in zip(
                    data.z_hd, data.z_hel, data.m_b_corr, data.ceph_dist, data.is_calibrator
                ):
                    handle.write(
                        "{} {} {} {} {}\n".format(
                            row[0], row[1], row[2], row[3], int(row[4])
                        )
                    )

            with covariance.open("w", encoding="utf-8") as handle:
                handle.write(str(data.n) + "\n")
                for value in data.covariance.ravel():
                    handle.write("{:.17g}\n".format(value))

            payload = build_result(
                catalog,
                covariance,
                output,
                seeds=[11, 23],
                maxiter=60,
                integration_points=512,
            )

            self.assertFalse(payload["claim_allowed"])
            self.assertEqual([row["model"] for row in payload["rows"]], [LCDM, CPL, RLL])
            self.assertIn("cpl_minus_baseline", payload["comparison"])
            self.assertIn("rll_minus_baseline", payload["comparison"])
            self.assertEqual(payload["comparison"]["baseline"], LCDM)
            self.assertIn("diagnostics", payload["inputs"]["covariance"])


if __name__ == "__main__":
    unittest.main()
