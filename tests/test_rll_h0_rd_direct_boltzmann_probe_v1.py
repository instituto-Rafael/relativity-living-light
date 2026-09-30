from __future__ import annotations

import unittest

from tools.rll_h0_rd_direct_boltzmann_probe_v1 import (
    MODEL_CPL,
    MODEL_LCDM,
    MODEL_RLL,
    MODEL_WCDM,
    probe,
)


def fake_ablation():
    cells = []
    for index in range(6):
        models = {
            MODEL_LCDM: {"parameters": {"H0": 67.0, "Om": 0.31, "OL": 0.69, "Ob_h2": 0.0224, "sigma8": 0.8}, "rd_mpc": 148.0, "best_attempt_success": True},
            MODEL_WCDM: {"parameters": {"H0": 68.0, "Om": 0.30, "OL": 0.70, "w": -0.9, "Ob_h2": 0.0224, "sigma8": 0.8}, "rd_mpc": 148.1, "best_attempt_success": True},
            MODEL_CPL: {"parameters": {"H0": 69.0, "Om": 0.29, "OL": 0.71, "w0": -0.9, "wa": 0.2, "Ob_h2": 0.0224, "sigma8": 0.8}, "rd_mpc": 148.2, "best_attempt_success": True},
            MODEL_RLL: {"parameters": {"H0": 68.0, "Om": 0.30, "OL": 0.69, "Os0": 0.01, "zt": 1.0, "wt": 0.3, "Ob_h2": 0.0224, "sigma8": 0.8}, "rd_mpc": 148.3, "best_attempt_success": True},
        }
        cells.append({"run_id": f"cell-{index}", "H0_policy": "broad_free", "rd_policy": "derived_for_all", "models": models})
    return {"state": "VERIFIED_INTERNAL_H0_RD_SENSITIVITY", "cells": cells}


def fake_evaluator(parameters, model):
    offsets = {MODEL_LCDM: 0.0, MODEL_WCDM: 0.1, MODEL_CPL: 0.2}
    return 147.0 + offsets[model] + (parameters["H0"] - 67.0) * 0.01


class DirectBoltzmannProbeTests(unittest.TestCase):
    def test_probe_evaluates_18_standard_vectors_and_blocks_six_rll(self):
        payload = probe(fake_ablation(), evaluator=fake_evaluator)
        self.assertEqual(payload["summary"]["direct_camb_evaluated"], 18)
        self.assertEqual(payload["summary"]["rll_mapping_blocked"], 6)
        self.assertEqual(len(payload["standard_model_direct_evaluations"]), 18)
        self.assertEqual(len(payload["rll_blocked_vectors"]), 6)
        self.assertFalse(payload["claim_allowed"])
        self.assertIsNone(payload["resolved_token"])

    def test_rll_is_not_sent_to_standard_evaluator(self):
        seen = []
        def evaluator(parameters, model):
            seen.append(model)
            self.assertNotEqual(model, MODEL_RLL)
            return 147.0
        probe(fake_ablation(), evaluator=evaluator)
        self.assertEqual(set(seen), {MODEL_LCDM, MODEL_WCDM, MODEL_CPL})

    def test_result_reduces_but_does_not_resolve_integration_token(self):
        payload = probe(fake_ablation(), evaluator=fake_evaluator)
        self.assertEqual(payload["reduces_token"], "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION")
        self.assertIsNone(payload["resolved_token"])
        self.assertIn("backend-selectable", " ".join(payload["remaining_close_conditions"]))


if __name__ == "__main__":
    unittest.main()
