from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.rll_act_dr6_posterior_contract_v1 import build


class ActPosteriorContractTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        extracted = root / "extracted"
        extracted.mkdir()
        (extracted / "actlite_lcdm_camb.input.yaml").write_text(
            "likelihood:\n  act_dr6_cmbonly.ACTDR6CMBonly: null\n  planck_2018_lowl.EE_sroll2: null\n"
            "theory:\n  camb: null\n"
            "params:\n"
            "  ombh2:\n    prior: {min: 0.005, max: 0.1}\n    ref: {dist: norm, loc: 0.0224, scale: 0.0001}\n    proposal: 0.0001\n"
            "  H0:\n    prior: {min: 40, max: 100}\n    ref: {dist: norm, loc: 67, scale: 1}\n    proposal: 1\n"
            "  ns:\n    prior: {min: 0.8, max: 1.2}\n"
            "sampler:\n  mcmc:\n    Rminus1_stop: 0.01\n    proposal_scale: 2.4\n",
            encoding="utf-8",
        )
        (extracted / "actlite_lcdm_camb.updated.yaml").write_text(
            "sampler:\n  mcmc:\n    Rminus1_stop: 0.01\n    Rminus1_cl_stop: 0.2\n"
            "params: {}\n",
            encoding="utf-8",
        )
        (extracted / "actlite_lcdm_camb.covmat").write_text("1 0 0\n0 1 0\n0 0 1\n", encoding="utf-8")
        (extracted / "actlite_lcdm_camb.minimum").write_text("minimum\n", encoding="utf-8")
        (extracted / "actlite_lcdm_camb.progress").write_text("progress\n", encoding="utf-8")
        header = "# weight minuslogpost ombh2 H0 ns\n"
        (extracted / "actlite_lcdm_camb.1.txt").write_text(
            header + "1 100 0.022 66.5 0.96\n2 90 0.0224 67.4 0.965\n",
            encoding="utf-8",
        )
        (extracted / "actlite_lcdm_camb.2.txt").write_text(
            header + "1 95 0.0223 67.2 0.964\n",
            encoding="utf-8",
        )
        return extracted

    def test_freezes_sampler_priors_and_best_reference_point(self):
        with tempfile.TemporaryDirectory() as td:
            payload = build(self.fixture(Path(td)), "https://example.invalid/act.tar.gz")
        self.assertEqual(payload["state"], "OFFICIAL_ACT_DR6_LCDM_POSTERIOR_CONTRACT_FROZEN")
        self.assertEqual(payload["parameters"]["count_sampled"], 3)
        self.assertEqual(payload["reference_chains"]["chain_file_count"], 2)
        self.assertEqual(payload["reference_chains"]["total_noncomment_rows"], 3)
        self.assertEqual(payload["reference_chains"]["best_observed_minuslogpost"], 90.0)
        self.assertEqual(payload["reference_chains"]["best_observed_sampled_parameters"]["H0"], 67.4)
        self.assertEqual(payload["mcmc_contract"]["Rminus1_stop"], 0.01)
        self.assertEqual(payload["mcmc_contract"]["Rminus1_cl_stop"], 0.2)
        self.assertFalse(payload["claim_allowed"])
        self.assertIsNone(payload["resolved_token"])

    def test_missing_sampled_parameter_in_chain_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            extracted = self.fixture(root)
            chain = extracted / "actlite_lcdm_camb.1.txt"
            chain.write_text("# weight minuslogpost ombh2 H0\n1 10 0.022 67\n", encoding="utf-8")
            (extracted / "actlite_lcdm_camb.2.txt").unlink()
            with self.assertRaisesRegex(ValueError, "missing sampled params"):
                build(extracted, "https://example.invalid/act.tar.gz")

    def test_duplicate_input_yaml_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            extracted = self.fixture(root)
            (extracted / "duplicate.input.yaml").write_text("params: {}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                build(extracted, "https://example.invalid/act.tar.gz")


if __name__ == "__main__":
    unittest.main()
