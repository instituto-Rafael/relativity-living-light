from __future__ import annotations

import unittest

from tools.rx_physics_v2_decision_packet import build


class RxPhysicsV2DecisionPacketTests(unittest.TestCase):
    def test_packet_preserves_only_remaining_scientific_decisions(self):
        packet = build()
        self.assertEqual(packet["target_contract"], "RX-PHYSICS-CANONICAL-V2")
        self.assertEqual(packet["target_state"], "TOKEN_VAZIO_CONTRACT")
        self.assertFalse(packet["claim_allowed"])
        self.assertEqual(packet["blocking_axes"], ["omega_r", "growth_mode"])
        axes = {row["axis"]: row for row in packet["axes"]}
        self.assertEqual(
            axes["hz_dataset"]["selected_option"],
            "independent_cosmic_chronometers_28",
        )
        self.assertTrue(axes["hz_dataset"]["decision_terminal"])
        self.assertEqual(
            axes["distance_integration"]["selected_option"],
            "log1p_simpson_with_preregistered_tolerance",
        )
        self.assertTrue(axes["distance_integration"]["decision_terminal"])

    def test_integrated_sound_horizon_directions_are_not_reopened(self):
        packet = build()
        axes = {row["axis"]: row for row in packet["axes"]}
        self.assertEqual(
            axes["bao_sound_horizon"]["selected_option"],
            "rd_integrated_REQUIRED_BY_EXISTING_V2_CONTRACT",
        )
        self.assertEqual(
            axes["cmb_acoustic_mode"]["selected_option"],
            "rs_star_REQUIRED_BY_EXISTING_V2_CONTRACT",
        )


if __name__ == "__main__":
    unittest.main()
