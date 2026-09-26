from __future__ import annotations

import unittest

from tools.rx_physics_v2_decision_packet import build


class RxPhysicsV2DecisionPacketTests(unittest.TestCase):
    def test_packet_has_zero_background_decision_blockers(self):
        packet = build()
        self.assertEqual(packet["target_contract"], "RX-PHYSICS-CANONICAL-V2")
        self.assertEqual(packet["target_state"], "VERSIONED_BACKGROUND_CONTRACT_PENDING_FINALIZER")
        self.assertEqual(packet["state"], "READY_CANONICAL_V2_BACKGROUND_FINALIZATION")
        self.assertFalse(packet["claim_allowed"])
        self.assertEqual(packet["blocking_axes"], [])
        axes = {row["axis"]: row for row in packet["axes"]}
        self.assertEqual(axes["omega_r"]["selected_option"], "derived_standard_relativistic_radiation")
        self.assertEqual(axes["hz_dataset"]["selected_option"], "independent_cosmic_chronometers_28")
        self.assertEqual(axes["growth_mode"]["selected_option"], "perturbation_backend_fsigma8")
        self.assertEqual(axes["distance_integration"]["selected_option"], "log1p_simpson_with_preregistered_tolerance")
        self.assertTrue(all(row["decision_terminal"] for row in axes.values()))

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
