from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_rll_execution_fabric_termux_replay import (
    DETERMINISTIC_FILES,
    ROOT_CHECKSUM_FILES,
    validate_directory,
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TermuxExecutionFabricReplayTests(unittest.TestCase):
    def test_synthetic_capsule_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "run1").mkdir()
            (root / "run2").mkdir()
            plan = "schema: rll.rx.execution_plan.v1\nclaim_allowed: false\n"
            (root / "execution_plan_source.yml").write_text(plan, encoding="utf-8")
            (root / "RUN.log").write_text("synthetic validator fixture\n", encoding="utf-8")

            run_receipt = {
                "status": "PASS",
                "physics_contract": "RX-STRUCTURE-D-PARITY-V1",
                "qualified_regimes": ["REGIME:G5", "REGIME:G6"],
                "claim_allowed": False,
            }
            for run in ("run1", "run2"):
                for name in DETERMINISTIC_FILES:
                    (root / run / name).write_text(json.dumps({"name": name}, sort_keys=True) + "\n", encoding="utf-8")
                (root / run / "receipt.json").write_text(json.dumps(run_receipt) + "\n", encoding="utf-8")

            lines = []
            for name in DETERMINISTIC_FILES:
                lines.append("%s  %s" % (sha(root / "run1" / name), name))
            content = "\n".join(lines) + "\n"
            (root / "RUN1_DETERMINISTIC.sha256").write_text(content, encoding="utf-8")
            (root / "RUN2_DETERMINISTIC.sha256").write_text(content, encoding="utf-8")

            receipt = {
                "schema": "rll.rx.termux_execution_fabric_receipt.v1",
                "generated_at": "2026-09-23T00:00:00Z",
                "repository": "instituto-Rafael/relativity-living-light",
                "workstream": "WS16",
                "state": "PASS_PHYSICAL_RX_EXECUTION_FABRIC",
                "git": {"code_commit": "a" * 40},
                "runtime": {
                    "uname": "Linux localhost Android armv7l",
                    "android_release": "10",
                    "device_model": "fixture",
                    "abi": "armeabi-v7a",
                    "python": "Python 3.11",
                },
                "execution": {
                    "run_id": "engineering-parity-g5-v1",
                    "physics_contract": "RX-STRUCTURE-D-PARITY-V1",
                    "qualified_regimes": ["REGIME:G5", "REGIME:G6"],
                    "dispersion_operator": "dataset_declared_covariance_operator",
                    "formula_selection_basis": "declared_applicability_only",
                    "repeat_deterministic_artifacts_identical": True,
                    "deterministic_manifest_sha256": sha(root / "RUN1_DETERMINISTIC.sha256"),
                    "plan_sha256": sha(root / "execution_plan_source.yml"),
                    "run_log_sha256": sha(root / "RUN.log"),
                },
                "actions_comparison_state": "TOKEN_VAZIO_PENDING_ACTIONS_RECEIPT_COMPARISON",
                "training": False,
                "ai_runtime": False,
                "claim_allowed": False,
            }
            (root / "TERMUX_RECEIPT.json").write_text(json.dumps(receipt) + "\n", encoding="utf-8")

            root_lines = []
            for name in sorted(ROOT_CHECKSUM_FILES):
                root_lines.append("%s  %s" % (sha(root / name), name))
            (root / "CHECKSUMS.sha256").write_text("\n".join(root_lines) + "\n", encoding="utf-8")

            validated = validate_directory(root)
            self.assertEqual(validated["state"], "PASS_PHYSICAL_RX_EXECUTION_FABRIC")
            self.assertFalse(validated["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
