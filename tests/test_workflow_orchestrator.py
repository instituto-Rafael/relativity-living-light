from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.workflow_orchestrator import (
    WorkflowSelection,
    apply_overrides,
    branch_from_ref,
    load_and_expand_catalog,
    main,
    mark_remaining_blocked,
    select_workflows,
)


WORKFLOW_TEMPLATE = """\
name: {name}
"on":
  {trigger}:
{dispatch_inputs}
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - run: true
"""


class CatalogFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.catalog_root = root / ".github" / "workflow-orchestrator"
        self.workflow_root = root / ".github" / "workflows"
        (self.catalog_root / "workflows" / "core").mkdir(parents=True)
        (self.catalog_root / "workflows" / "real_data").mkdir(parents=True)
        (self.catalog_root / "workflows" / "science").mkdir(parents=True)
        self.workflow_root.mkdir(parents=True)

    def workflow(
        self,
        filename: str,
        *,
        trigger: str = "workflow_dispatch",
        with_mode_input: bool = False,
    ) -> None:
        dispatch_inputs = ""
        if with_mode_input and trigger == "workflow_dispatch":
            dispatch_inputs = (
                "    inputs:\n"
                "      mode:\n"
                "        required: true\n"
                "        default: audit\n"
            )
        (self.workflow_root / filename).write_text(
            WORKFLOW_TEMPLATE.format(
                name=filename,
                trigger=trigger,
                dispatch_inputs=dispatch_inputs,
            ),
            encoding="utf-8",
        )

    def manifest(
        self,
        filename: str = "10-managed.yml",
        *,
        workflow_id: str = "managed",
        workflow_file: str = "managed.yml",
        enabled: bool = True,
        override_allowlist: str = "[]",
    ) -> None:
        disabled = "" if enabled else "disabled_reason: legacy compatibility only\n"
        content = f"""\
id: {workflow_id}
file: {workflow_file}
stage: 10
specialty: STRUCTURE
enabled: {str(enabled).lower()}
tags: [tower, core, validation]
wait_for_completion: true
timeout_minutes: 20
inputs:
  mode: audit
override_allowlist: {override_allowlist}
claim_allowed: false
publication_effect: NONE
{disabled}"""
        (self.catalog_root / "workflows" / "core" / filename).write_text(
            content, encoding="utf-8"
        )

    def session(self, *, wait: bool = True, fail_fast: bool = True) -> Path:
        path = self.catalog_root / "session.yml"
        path.write_text(
            f"""\
schema: rll.workflow_orchestrator.catalog.v3
profiles:
  transit_refactor:
    include_tags: [tower]
execution:
  mode: sequential
  stage_barrier: true
  max_in_flight: 1
  wait_for_completion: {str(wait).lower()}
  fail_fast: {str(fail_fast).lower()}
workflow_inventory:
  patterns:
    - ../workflows/*.yml
workflow_catalog_dirs:
  - workflows/core
  - workflows/real_data
  - workflows/science
""",
            encoding="utf-8",
        )
        return path


class WorkflowOrchestratorTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], CatalogFixture]:
        temp = tempfile.TemporaryDirectory()
        fixture = CatalogFixture(Path(temp.name))
        fixture.workflow("managed.yml", with_mode_input=True)
        fixture.workflow("standalone.yml")
        fixture.workflow("event.yml", trigger="pull_request")
        fixture.workflow("unified-workflow-session-orchestrator.yml")
        fixture.manifest()
        fixture.session()
        return temp, fixture

    def test_inventory_is_complete_but_execution_is_explicit(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        catalog = load_and_expand_catalog(fixture.catalog_root / "session.yml")
        selected = select_workflows(catalog, "transit_refactor")
        self.assertEqual([item.workflow_id for item in selected], ["managed"])
        classifications = {
            row["file"]: row["classification"]
            for row in catalog["workflow_inventory_rows"]
        }
        self.assertEqual(classifications["managed.yml"], "TOWER_MANAGED")
        self.assertEqual(
            classifications["standalone.yml"], "STANDALONE_DISPATCHABLE"
        )
        self.assertEqual(classifications["event.yml"], "EVENT_DRIVEN")
        self.assertEqual(
            classifications["unified-workflow-session-orchestrator.yml"],
            "ORCHESTRATOR_SELF",
        )

    def test_managed_workflow_requires_manual_dispatch(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.workflow("managed.yml", trigger="pull_request")
        with self.assertRaisesRegex(ValueError, "lacks workflow_dispatch"):
            load_and_expand_catalog(fixture.catalog_root / "session.yml")

    def test_execution_wait_and_fail_fast_are_mandatory(self) -> None:
        for wait, fail_fast, message in [
            (False, True, "wait_for_completion"),
            (True, False, "fail_fast"),
        ]:
            with self.subTest(wait=wait, fail_fast=fail_fast):
                temp, fixture = self.make_fixture()
                try:
                    fixture.session(wait=wait, fail_fast=fail_fast)
                    with self.assertRaisesRegex(ValueError, message):
                        load_and_expand_catalog(
                            fixture.catalog_root / "session.yml"
                        )
                finally:
                    temp.cleanup()

    def test_duplicate_manifest_id_is_rejected(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.workflow("second.yml", with_mode_input=True)
        fixture.manifest(
            "20-second.yml", workflow_id="managed", workflow_file="second.yml"
        )
        with self.assertRaisesRegex(ValueError, "duplicate workflow id"):
            load_and_expand_catalog(fixture.catalog_root / "session.yml")

    def test_unknown_manifest_input_is_rejected(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        manifest = fixture.catalog_root / "workflows" / "core" / "10-managed.yml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                "  mode: audit", "  mode: audit\n  invented: unsafe"
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "unknown workflow inputs"):
            load_and_expand_catalog(fixture.catalog_root / "session.yml")

    @staticmethod
    def selection(*, allowlist: tuple[str, ...] = ()) -> WorkflowSelection:
        return WorkflowSelection(
            workflow_id="real_run",
            file="real.yml",
            stage=10,
            specialty="REAL_DATA",
            wait_for_completion=True,
            timeout_minutes=30,
            inputs={"mode": "audit_only"},
            override_allowlist=allowlist,
            claim_allowed=False,
            publication_effect="NONE",
        )

    def test_overrides_are_default_deny(self) -> None:
        with self.assertRaisesRegex(ValueError, "forbidden input"):
            apply_overrides(
                [self.selection()], '{"real_run": {"mode": "full"}}'
            )

    def test_allowlisted_override_is_applied(self) -> None:
        selected = apply_overrides(
            [self.selection(allowlist=("mode",))],
            '{"real_run": {"mode": "audit"}}',
        )
        self.assertEqual(selected[0].inputs, {"mode": "audit"})

    def test_override_rejects_unknown_workflow_and_nested_value(self) -> None:
        invalid = [
            ('{"missing": {"mode": "audit"}}', "unselected workflow"),
            ('{"real_run": {"mode": {"unsafe": true}}}', "non-null scalars"),
        ]
        for payload, message in invalid:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(ValueError, message):
                    apply_overrides(
                        [self.selection(allowlist=("mode",))], payload
                    )

    def test_branch_ref_is_validated_and_commit_sha_is_rejected(self) -> None:
        self.assertEqual(branch_from_ref("refs/heads/rll/lab"), "rll/lab")
        for value in ["", "../main", "bad ref", "a//b", "a@{b", "f" * 40]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    branch_from_ref(value)

    def test_fail_fast_marks_every_downstream_specialty_blocked(self) -> None:
        payload = {
            "workflows": [
                {"state": "FAIL", "status": "completed", "conclusion": "failure", "residuals": []},
                {"state": "NOT_STARTED", "status": "not_requested", "conclusion": "not_requested", "residuals": []},
                {"state": "NOT_STARTED", "status": "not_requested", "conclusion": "not_requested", "residuals": []},
            ]
        }
        mark_remaining_blocked(payload, 1, "structure")
        self.assertEqual(
            [row["state"] for row in payload["workflows"]],
            ["FAIL", "BLOCKED", "BLOCKED"],
        )
        self.assertTrue(
            all(
                row["residuals"] == ["UPSTREAM_BLOCK:structure"]
                for row in payload["workflows"][1:]
            )
        )

    def test_dry_run_writes_a_complete_non_promotional_receipt(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        output = fixture.root / "artifacts"
        code = main(
            [
                "--catalog",
                str(fixture.catalog_root / "session.yml"),
                "--profile",
                "transit_refactor",
                "--ref",
                "rll/lab",
                "--wait",
                "--fail-fast",
                "--dry-run",
                "--output-dir",
                str(output),
            ]
        )
        self.assertEqual(code, 0)
        receipt = json.loads(
            (output / "orchestration_receipt.json").read_text(encoding="utf-8")
        )
        for field in [
            "schema",
            "commit_sha",
            "workflow",
            "job",
            "claim_allowed",
            "scientific_gate",
            "publication_ready",
            "publication_effect",
            "inputs_sha256",
            "decision",
            "residuals",
        ]:
            self.assertIn(field, receipt)
        self.assertEqual(receipt["decision"], "OBSERVED_LIMITED")
        self.assertIs(receipt["claim_allowed"], False)
        self.assertEqual(receipt["scientific_gate"], "BLOCKED")
        self.assertIs(receipt["publication_ready"], False)
        self.assertEqual(receipt["publication_effect"], "NONE")
        self.assertEqual(receipt["workflows"][0]["state"], "OBSERVED_LIMITED")
        self.assertTrue((output / "workflow_inventory.tsv").is_file())
        self.assertTrue((output / "ORCHESTRATION_REPORT.md").is_file())

    def test_missing_fail_fast_is_a_receipted_blocker(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        output = fixture.root / "blocked"
        code = main(
            [
                "--catalog",
                str(fixture.catalog_root / "session.yml"),
                "--profile",
                "transit_refactor",
                "--ref",
                "rll/lab",
                "--wait",
                "--dry-run",
                "--output-dir",
                str(output),
            ]
        )
        self.assertEqual(code, 2)
        receipt = json.loads(
            (output / "orchestration_receipt.json").read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["decision"], "BLOCKED")
        self.assertIn("--wait and --fail-fast", receipt["residuals"][0])

    def test_preflight_receipt_uses_explicit_head_sha(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        output = fixture.root / "head-sha"
        expected_sha = "a" * 40
        with patch.dict(
            "os.environ", {"ORCHESTRATION_COMMIT_SHA": expected_sha}, clear=False
        ):
            code = main(
                [
                    "--catalog",
                    str(fixture.catalog_root / "session.yml"),
                    "--profile",
                    "transit_refactor",
                    "--ref",
                    "rll/lab",
                    "--wait",
                    "--fail-fast",
                    "--dry-run",
                    "--output-dir",
                    str(output),
                ]
            )
        self.assertEqual(code, 0)
        receipt = json.loads(
            (output / "orchestration_receipt.json").read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["commit_sha"], expected_sha)


if __name__ == "__main__":
    unittest.main()
