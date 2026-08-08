from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.rll_act_dr6_posterior_contract_v2 import build


class ActPosteriorContractV2Tests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        extracted = root / "extracted"
        extracted.mkdir()
        (extracted / "actlite_lcdm_camb.input.yaml").write_text(
            "likelihood:\n  act_dr6_cmbonly.ACTDR6CMBonly: null\n  planck_2018_lowl.EE_sroll2: null\n"
            "theory:\n  camb: null\n"
            "params:\n"
            "  ombh2:\n    prior: {min: 0.005, max: 0.1}\n    ref: {dist: norm, loc: 0.0224, scale: 0.0001}\n"
            "  theta_MC_100:\n    prior: {min: 0.5, max: 10}\n    renames: [theta]\n"
            "  ns:\n    prior: {min: 0.8, max: 1.2}\n"
            "sampler:\n  mcmc:\n    Rminus1_stop: 0.01\n    proposal_scale: 2.4\n",
            encoding="utf-8",
        )
        (extracted / "actlite_lcdm_camb.updated.yaml").write_text(
            "sampler:\n  mcmc:\n    Rminus1_stop: 0.01\n    Rminus1_cl_stop: 0.2\nparams: {}\n",
            encoding="utf-8",
        )
        (extracted / "actlite_lcdm_camb.minimize.input.yaml").write_text(
            "sampler:\n  minimize: {}\nparams: {}\n", encoding="utf-8"
        )
        (extracted / "actlite_lcdm_camb.minimize.updated.yaml").write_text(
            "sampler:\n  minimize: {}\nparams: {}\n", encoding="utf-8"
        )
        (extracted / "actlite_lcdm_camb.covmat").write_text("1 0 0\n0 1 0\n0 0 1\n", encoding="utf-8")
        (extracted / "actlite_lcdm_camb.minimum").write_text("minimum\n", encoding="utf-8")
        (extracted / "actlite_lcdm_camb.progress").write_text("progress\n", encoding="utf-8")
        header = "# weight minuslogpost ombh2 theta ns\n"
        (extracted / "actlite_lcdm_camb.1.txt").write_text(
            header + "1 100 0.0220 1.04 0.960\n2 90 0.0224 1.041 0.965\n",
            encoding="utf-8",
        )
        (extracted / "actlite_lcdm_camb.2.txt").write_text(
            header + "1 95 0.0223 1.040 0.964\n",
            encoding="utf-8",
        )
        return extracted

    def test_freezes_replay_authority_even_with_alias_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            payload = build(self.fixture(Path(td)), "https://example.invalid/act.tar.gz")
        self.assertEqual(payload["state"], "OFFICIAL_ACT_DR6_LCDM_POSTERIOR_CONTRACT_FROZEN")
        self.assertEqual(payload["parameters"]["count_sampled"], 3)
        self.assertEqual(payload["parameters"]["mapped_to_reference_chain"], ["ombh2", "ns"])
        self.assertEqual(payload["parameters"]["unmapped_to_reference_chain"], ["theta_MC_100"])
        self.assertFalse(payload["parameters"]["mapping_is_required_for_replay"])
        self.assertEqual(payload["reference_chains"]["total_noncomment_rows"], 3)
        self.assertEqual(payload["reference_chains"]["best_observed_minuslogpost"], 90.0)
        self.assertEqual(payload["mcmc_contract"]["Rminus1_stop"], 0.01)
        self.assertEqual(payload["mcmc_contract"]["Rminus1_cl_stop"], 0.2)
        self.assertEqual(len(payload["authority"]["auxiliary_minimize_configs"]), 2)
        self.assertFalse(payload["claim_allowed"])
        self.assertIsNone(payload["resolved_token"])

    def test_non_dict_prior_is_still_sampled_if_non_null(self):
        with tempfile.TemporaryDirectory() as td:
            extracted = self.fixture(Path(td))
            text = (extracted / "actlite_lcdm_camb.input.yaml").read_text(encoding="utf-8")
            text = text.replace("prior: {min: 0.8, max: 1.2}", "prior: [0.8, 1.2]")
            (extracted / "actlite_lcdm_camb.input.yaml").write_text(text, encoding="utf-8")
            payload = build(extracted, "https://example.invalid/act.tar.gz")
        self.assertIn("ns", payload["parameters"]["sampled"])

    def test_no_sampled_prior_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            extracted = self.fixture(Path(td))
            (extracted / "actlite_lcdm_camb.input.yaml").write_text(
                "likelihood:\n  act_dr6_cmbonly.ACTDR6CMBonly: null\n"
                "theory:\n  camb: null\nparams:\n  H0: {value: 67}\n"
                "sampler:\n  mcmc:\n    Rminus1_stop: 0.01\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "no parameters with explicit non-null priors"):
                build(extracted, "https://example.invalid/act.tar.gz")

    def test_no_chain_data_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            extracted = self.fixture(Path(td))
            for path in extracted.glob("*.txt"):
                path.write_text("# weight minuslogpost ombh2 theta ns\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no finite samples"):
                build(extracted, "https://example.invalid/act.tar.gz")

    def test_second_non_minimize_yaml_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            extracted = self.fixture(Path(td))
            (extracted / "duplicate.input.yaml").write_text("params: {}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-minimize"):
                build(extracted, "https://example.invalid/act.tar.gz")


if __name__ == "__main__":
    unittest.main()
