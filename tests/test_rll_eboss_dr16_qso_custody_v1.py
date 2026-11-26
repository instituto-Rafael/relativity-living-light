"""Synthetic negative controls; upstream real bytes are not redistributed."""
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import rll_eboss_dr16_qso_custody_v1 as q

V = b"1.48 10 DM_over_rs\n1.48 5 DH_over_rs\n1.48 0.5 f_sigma8"
C = b"4 1 0.2\n1 2 0.1\n0.2 0.1 1"


class QsoCustodyTests(unittest.TestCase):
    def test_marginal_not_conditional(self):
        obs, full, marginal = q.parse(V, C)
        self.assertEqual(marginal, [[4., 1.], [1., 2.]])
        self.assertEqual(q.chi2_bao(obs[:2], [10., 5.], marginal), 0.)
        self.assertAlmostEqual(q.chi2_bao(obs[:2], [9., 4.], marginal), 4/7)

    def test_order_and_nonfinite(self):
        for bad in (V.replace(b"DM_over_rs", b"DH_over_rs"), V.replace(b"10", b"nan"), V.replace(b"1.48", b"1.49")):
            with self.assertRaises(ValueError):
                q.parse(bad, C)

    def test_bad_covariance(self):
        for bad in (b"1 2 0\n2 1 0\n0 0 1", b"1 0 0\n1 1 0\n0 0 1", b"1 0 0\n0 1 0", b"1 0 0\n0 nan 0\n0 0 1"):
            with self.assertRaises(ValueError):
                q.parse(V, bad)
        with self.assertRaises(ValueError):
            q.chi2_bao([1., 1.], [math.inf, 1.], [[1., 0.], [0., 1.]])

    def test_custody_and_claim_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / q.NAMES[0]).write_bytes(V)
            (root / q.NAMES[1]).write_bytes(C)
            with self.assertRaises(ValueError):
                q.build(root)
            with patch.object(q, "BLOBS", (q.git_blob(V), q.git_blob(C))):
                receipt = q.build(root)
                self.assertIsNone(receipt["chi2_bao"])
                self.assertFalse(receipt["claim_allowed"])
                self.assertFalse(receipt["promotion_allowed"])
                self.assertEqual(receipt["model_selection"], "NOT_RUN")
                (root / q.NAMES[0]).write_bytes(V+b" ")
                with self.assertRaises(ValueError):
                    q.build(root)


if __name__ == "__main__":
    unittest.main()
