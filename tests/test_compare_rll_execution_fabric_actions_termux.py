from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.compare_rll_execution_fabric_actions_termux import compare
from tools.validate_rll_execution_fabric_termux_replay import (
    DETERMINISTIC_FILES,
    ROOT_CHECKSUM_FILES,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixture(root: Path) -> tuple[Path, Path]:
    actions = root / "actions"
    termux = root / "termux"
    actions.mkdir()
    (termux / "run1").mkdir(parents=True)
    (termux / "run2").mkdir(parents=True)

    plan = "schema: rll.rx.execution_plan.v1\nclaim_allowed: false\n"
    (termux / "execution_plan_source.yml").write_text(plan, encoding="utf-8")
    (termux / "RUN.log").write_text("physical fixture\n", encoding="utf-8")

    run_receipt = {
        "status": "PASS",
        "run_id": "engineering-parity-g5-v1",
        "physics_contract": "RX-STRUCTURE-D-PARITY-V1",
        "qualified_regimes": ["REGIME:G5", "REGIME:G6"],
        "dispersion_operator": "dataset_declared_covariance_operator",
        "formula_selection_basis": "declared_applicability_only",
        "claim_allowed": False,
    }
    (actions / "receipt.json").write_text(json.dumps(run_receipt) + "\n", encoding="utf-8")

    lines = []
    for name in DETERMINISTIC_FILES:
        payload = json.dumps({"name": name}, sort_keys=True) + "\n"
        (actions / name).write_text(payload, encoding="utf-8")
        (termux / "run1" / name).write_text(payload, encoding="utf-8")
        (termux / "run2" / name).write_text(payload, encoding="utf-8")
        lines.append("%s  %s" % (sha(termux / "run1" / name), name))
    det = "\n".join(lines) + "\n"
    (termux / "RUN1_DETERMINISTIC.sha256").write_text(det, encoding="utf-8")
    (termux / "RUN2_DETERMINISTIC.sha256").write_text(det, encoding="utf-8")

    for run in ("run1", "run2"):
        (termux / run / "receipt.json").write_text(json.dumps(run_receipt) + "\n", encoding="utf-8")

    physical = {
        "schema": "rll.rx.termux_execution_fabric_receipt.v1",
        "generated_at": "2026-09-24T00:00:00Z",
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
            "run_id": run_receipt["run_id"],
            "physics_contract": run_receipt["physics_contract"],
            "qualified_regimes": run_receipt["qualified_regimes"],
            "dispersion_operator": run_receipt["dispersion_operator"],
            "formula_selection_basis": run_receipt["formula_selection_basis"],
            "repeat_deterministic_artifacts_identical": True,
            "deterministic_manifest_sha256": sha(termux / "RUN1_DETERMINISTIC.sha256"),
            "plan_sha256": sha(termux / "execution_plan_source.yml"),
            "run_log_sha256": sha(termux / "RUN.log"),
        },
        "actions_comparison_state": "TOKEN_VAZIO_PENDING_ACTIONS_RECEIPT_COMPARISON",
        "training": False,
        "ai_runtime": False,
        "claim_allowed": False,
    }
    (termux / "TERMUX_RECEIPT.json").write_text(json.dumps(physical) + "\n", encoding="utf-8")

    root_lines = []
    for name in sorted(ROOT_CHECKSUM_FILES):
        root_lines.append("%s  %s" % (sha(termux / name), name))
    (termux / "CHECKSUMS.sha256").write_text("\n".join(root_lines) + "\n", encoding="utf-8")
    return actions, termux


class ActionsTermuxParityTests(unittest.TestCase):
    def test_matching_capsules_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            actions, termux = make_fixture(Path(tmp))
            result = compare(actions, termux)
            self.assertEqual(result["state"], "PASS_ACTIONS_TERMUX_DETERMINISTIC_PARITY")
            self.assertEqual(result["matched_file_count"], len(DETERMINISTIC_FILES))
            self.assertTrue(result["physical_execution_proven"])
            self.assertFalse(result["claim_allowed"])

    def test_single_deterministic_mutation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            actions, termux = make_fixture(Path(tmp))
            (actions / DETERMINISTIC_FILES[0]).write_text('{"changed": true}\n', encoding="utf-8")
            result = compare(actions, termux)
            self.assertEqual(result["state"], "FAIL_ACTIONS_TERMUX_PARITY")
            self.assertTrue(any("deterministic mismatch" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
