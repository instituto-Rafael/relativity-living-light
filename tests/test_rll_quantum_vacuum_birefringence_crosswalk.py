from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_rll_quantum_vacuum_birefringence_crosswalk import PATH, audit, validate


class QuantumVacuumBirefringenceCrosswalkTests(unittest.TestCase):
    def test_light_profile_keeps_claim_boundary_closed(self) -> None:
        data = validate(profile="light")
        self.assertTrue(data["append_only"])
        self.assertFalse(data["claim_allowed"])
        self.assertFalse(data["policy"]["external_paper_is_rll_confirmation"])
        self.assertFalse(data["policy"]["repository_ci_may_write_repository"])
        self.assertFalse(data["policy"]["repository_ci_may_ingest_external_data"])

    def test_deep_profile_requires_all_testable_routes_and_gaps(self) -> None:
        data = validate(profile="deep")
        self.assertEqual(len(data["testable_routes"]), 3)
        self.assertEqual(len(data["token_vazio"]), 4)
        self.assertTrue(all(item["state"].startswith("TOKEN_VAZIO") for item in data["token_vazio"]))
        self.assertTrue(all(item["claim_allowed"] is False for item in data["testable_routes"]))

    def test_audit_writes_artifacts_not_repository_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "artifacts"
            receipt = audit("light", output_dir)
            self.assertFalse(receipt["repository_write_attempted"])
            self.assertFalse(receipt["external_data_ingestion_attempted"])
            persisted = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted["input_path"], PATH.relative_to(PATH.parents[2]).as_posix())
            self.assertEqual((output_dir / "input.sha256").read_text(encoding="utf-8").count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
