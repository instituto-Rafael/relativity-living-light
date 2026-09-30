from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.rll_desi_dr2_cobaya_custody_v1 import build


class DesiDr2CustodyTests(unittest.TestCase):
    def test_requires_materialized_desi_files(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "DESI"):
                build(Path(td))

    def test_custody_reduces_availability_gap_without_resolving_joint_reproduction(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "data" / "bao_data"
            data.mkdir(parents=True)
            (data / "desi_dr2_mean.txt").write_text("1 2 3\n", encoding="utf-8")
            (data / "desi_dr2_cov.txt").write_text("1 0\n0 1\n", encoding="utf-8")
            with patch("tools.rll_desi_dr2_cobaya_custody_v1.importlib.metadata.version", return_value="3.5.6"):
                payload = build(root)
            self.assertEqual(payload["custody"]["desi_file_count"], 2)
            self.assertFalse(payload["claim_allowed"])
            self.assertIsNone(payload["resolved_token"])
            self.assertEqual(payload["reduces_token"], "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION")
            self.assertEqual(payload["component"]["alias"], "bao.desi_dr2")
            self.assertIn("joint", " ".join(payload["remaining_close_conditions"]))


if __name__ == "__main__":
    unittest.main()
