from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.rll_act_dr6_reference_chain_custody_v1 import build, chain_rows


class ActReferenceChainCustodyTests(unittest.TestCase):
    def test_chain_rows_ignores_comments_and_blanks(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "chain.1.txt"
            path.write_text("# header\n\n1 2 3\n4 5 6\n", encoding="utf-8")
            self.assertEqual(chain_rows(path), 2)

    def test_build_requires_chain_and_updated_config(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "actlite_lcdm_camb.tar.gz"
            archive.write_bytes(b"archive")
            extracted = root / "extract"
            extracted.mkdir()
            with self.assertRaisesRegex(ValueError, "chain"):
                build(archive, extracted, "https://example.invalid/reference.tar.gz")

    def test_custody_reduces_but_does_not_resolve_posterior_token(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "actlite_lcdm_camb.tar.gz"
            archive.write_bytes(b"archive")
            extracted = root / "extract"
            extracted.mkdir()
            (extracted / "actlite_lcdm_camb.1.txt").write_text("# header\n1 2 3\n", encoding="utf-8")
            config = extracted / "actlite_lcdm_camb.updated.yaml"
            config.write_text("params: {}\n", encoding="utf-8")
            with patch(
                "tools.rll_act_dr6_reference_chain_custody_v1.compact_config",
                return_value={"parameter_names": [], "sampler_names": ["mcmc"], "theory_names": ["camb"], "likelihood_names": ["act_dr6_cmbonly"], "output": "chain"},
            ):
                payload = build(archive, extracted, "https://example.invalid/reference.tar.gz")
            self.assertFalse(payload["claim_allowed"])
            self.assertIsNone(payload["resolved_token"])
            self.assertEqual(payload["reduces_token"], "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION")
            self.assertEqual(payload["custody"]["chain_file_count"], 1)
            self.assertEqual(payload["custody"]["total_noncomment_chain_rows"], 1)
            self.assertTrue(payload["reference_role"]["official_reference_posterior_available"])
            self.assertFalse(payload["reference_role"]["locally_reproduced_from_frozen_config"])


if __name__ == "__main__":
    unittest.main()
