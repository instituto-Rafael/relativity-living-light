from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.rll_desi_dr2_reference_loglike_probe_v1 import CONTROL_POINTS, build


class DesiDr2ReferenceLoglikeProbeTests(unittest.TestCase):
    def test_executes_all_declared_controls_without_promoting_token(self):
        with tempfile.TemporaryDirectory() as td:
            seen = []
            def evaluator(path, point):
                seen.append(point["id"])
                return -10.0 - len(seen)
            payload = build(Path(td), evaluator=evaluator)
        self.assertEqual(seen, [point["id"] for point in CONTROL_POINTS])
        self.assertEqual(len(payload["control_points"]), 3)
        self.assertFalse(payload["claim_allowed"])
        self.assertIsNone(payload["resolved_token"])
        self.assertEqual(payload["reduces_token"], "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION")

    def test_control_points_include_lcdm_and_nonlambda_cpl(self):
        models = {point["model"] for point in CONTROL_POINTS}
        self.assertEqual(models, {"LCDM", "CPL"})
        cpl = next(point for point in CONTROL_POINTS if point["model"] == "CPL")
        self.assertIn("w", cpl["params"])
        self.assertIn("wa", cpl["params"])
        self.assertNotEqual(cpl["params"]["w"], -1.0)

    def test_missing_packages_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing"
            with self.assertRaisesRegex(ValueError, "packages path"):
                build(missing, evaluator=lambda path, point: -1.0)


if __name__ == "__main__":
    unittest.main()
