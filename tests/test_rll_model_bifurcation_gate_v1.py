from __future__ import annotations

import copy
import json
import unittest

from tools.ci import rll_model_bifurcation_gate_v1 as gate


def contract() -> dict:
    return json.loads(gate.CONTRACT.read_text(encoding="utf-8"))


def branch_contract() -> dict:
    return json.loads(gate.BRANCH_CONTRACT.read_text(encoding="utf-8"))


class RllModelBifurcationGateV1Tests(unittest.TestCase):
    def test_canonical_contract_passes_scoped_gate(self) -> None:
        self.assertEqual(gate.validate(contract()), [])

    def test_branch_set_is_complete_and_no_winner_is_selected(self) -> None:
        data = contract()
        self.assertEqual(set(data["branches"]), gate.EXPECTED_BRANCHES)
        self.assertTrue(data["selected_physical_winner"].startswith("TOKEN_VAZIO_"))
        self.assertIs(data["claim_allowed"], False)

    def test_untyped_gap_is_rejected(self) -> None:
        data = copy.deepcopy(contract())
        data["branches"]["C"]["gaps"][0] = "unknown"
        self.assertTrue(any(error.startswith("UNTYPED_GAP:C:") for error in gate.validate(data)))

    def test_point_evaluation_cannot_be_promoted_to_fit(self) -> None:
        data = copy.deepcopy(contract())
        data["comparison_contract"]["point_evaluation_is_fit"] = True
        self.assertIn("POINT_EVALUATION_PROMOTED_TO_FIT", gate.validate(data))

    def test_open_branch_cannot_self_promote(self) -> None:
        data = copy.deepcopy(contract())
        data["branches"]["S"]["status"] = "PASS"
        self.assertIn("OPEN_BRANCH_FALSELY_PROMOTED:S", gate.validate(data))

    def test_global_pass_is_forbidden(self) -> None:
        data = copy.deepcopy(contract())
        data["branches"]["F"]["status"] = "PASS_GLOBAL"
        self.assertIn("FORBIDDEN_GLOBAL_PASS:F", gate.validate(data))

    def test_branch_contract_is_complete_and_fail_closed(self) -> None:
        self.assertEqual(gate.validate_branch_contract(branch_contract()), [])

    def test_interaction_sign_invariant_cannot_be_silently_reversed(self) -> None:
        data = copy.deepcopy(branch_contract())
        data["core"]["sign_invariant"] = "q_s>=0"
        self.assertIn("INTERACTION_SIGN_INVARIANT_MISSING", gate.validate_branch_contract(data))

    def test_e1_e2_e3_are_distinct_and_required(self) -> None:
        data = copy.deepcopy(branch_contract())
        del data["result_relation_types"]["E2"]
        self.assertIn("RESULT_RELATION_TYPES_INCOMPLETE", gate.validate_branch_contract(data))


if __name__ == "__main__":
    unittest.main()
