from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import deep_yaml_audit as mod


class DeepYamlAuditTests(unittest.TestCase):
    def audit_reconciliation_job(
        self,
        *,
        job_if: str,
        job_permissions: str = "      contents: write\n      pull-requests: write",
    ) -> set[str]:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / ".github/workflows/reconcile.yml"
            path.parent.mkdir(parents=True)
            condition = f"    if: {job_if}\n" if job_if else ""
            text = f"""\
name: reconcile
on: [pull_request, workflow_dispatch]
permissions:
  contents: read
concurrency:
  group: reconcile-${{{{ github.ref }}}}
jobs:
  propose:
{condition}    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions:
{job_permissions}
    steps:
      - run: python tools/propose.py
"""
            path.write_text(text, encoding="utf-8")
            record = mod.FileRecord(
                path=".github/workflows/reconcile.yml",
                category="github_workflow",
                sha256="x",
                bytes=len(text),
                lines=len(text.splitlines()),
            )
            doc = mod.parse_documents(text, workflow=True)[0]
            contract = {
                "workflow_classes": {
                    "reconciliation": {
                        "default_permissions": {"contents": "read"},
                        "manual_write_permissions": {
                            "contents": "write",
                            "pull-requests": "write",
                        },
                        "write_jobs_manual_dispatch_only": True,
                    }
                },
                "managed_workflows": {
                    record.path: {"class": "reconciliation", "require": []}
                },
                "security": {
                    "write_permissions_require_explicit_workflow_class": [
                        "orchestrator",
                        "reconciliation",
                    ]
                },
            }
            mod.audit_workflow(record, root, doc, contract)
            return {item.code for item in record.findings}

    def test_duplicate_key_fails_closed(self) -> None:
        with self.assertRaises(mod.DuplicateKeyError):
            mod.parse_documents("a: 1\na: 2\n", workflow=False)

    def test_secure_managed_workflow_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / ".github/workflows/audit.yml"
            path.parent.mkdir(parents=True)
            text = """\
name: audit
on: [pull_request]
permissions:
  contents: read
concurrency:
  group: audit-${{ github.ref }}
jobs:
  audit:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          persist-credentials: false
      - run: python tools/audit.py
      - if: always()
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          path: artifacts/
          retention-days: 30
"""
            path.write_text(text, encoding="utf-8")
            record = mod.FileRecord(path=".github/workflows/audit.yml", category="github_workflow", sha256="x", bytes=len(text), lines=len(text.splitlines()))
            doc = mod.parse_documents(text, workflow=True)[0]
            contract = {
                "workflow_classes": {"structural": {"allowed_permissions": {"contents": "read"}}},
                "managed_workflows": {
                    record.path: {
                        "class": "structural",
                        "require": ["permissions", "concurrency", "job_timeout", "checkout_without_persistent_credentials", "always_upload_receipt", "externalized_algorithm"],
                    }
                },
            }
            mod.audit_workflow(record, root, doc, contract)
            self.assertEqual([], record.findings)

    def test_dangerous_workflow_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / ".github/workflows/risky.yml"
            path.parent.mkdir(parents=True)
            text = """\
name: risky
on:
  workflow_dispatch:
    inputs:
      path:
        required: true
permissions:
  contents: write
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          FILE="${{ inputs.path }}"
          python thing.py || true
          chi2 = 93.81
"""
            path.write_text(text, encoding="utf-8")
            record = mod.FileRecord(path=".github/workflows/risky.yml", category="github_workflow", sha256="x", bytes=len(text), lines=len(text.splitlines()))
            doc = mod.parse_documents(text, workflow=True)[0]
            mod.audit_workflow(record, root, doc, {})
            codes = {item.code for item in record.findings}
            self.assertTrue({
                "MUTABLE_ACTION_REFERENCE",
                "UNTRUSTED_EXPRESSION_IN_RUN",
                "FAILURE_SWALLOWED",
                "SCIENTIFIC_RESULT_OR_PARAMETER_EMBEDDED",
                "JOB_WRITE_PERMISSION_UNGOVERNED",
            }.issubset(codes))

    def test_reconciliation_write_job_is_allowed_only_with_manual_guard(self) -> None:
        codes = self.audit_reconciliation_job(
            job_if="github.event_name == 'workflow_dispatch' && inputs.mode == 'propose'"
        )
        self.assertNotIn("JOB_WRITE_PERMISSION_UNGOVERNED", codes)
        self.assertNotIn("WRITE_JOB_NOT_MANUAL_DISPATCH_ONLY", codes)

    def test_reconciliation_write_job_without_manual_guard_fails_closed(self) -> None:
        codes = self.audit_reconciliation_job(job_if="")
        self.assertIn("WRITE_JOB_NOT_MANUAL_DISPATCH_ONLY", codes)

    def test_reconciliation_write_job_rejects_undeclared_scope(self) -> None:
        codes = self.audit_reconciliation_job(
            job_if="github.event_name == 'workflow_dispatch'",
            job_permissions="      actions: write",
        )
        self.assertIn("JOB_WRITE_PERMISSION_UNGOVERNED", codes)

    def test_inventory_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            summary = root / "data/results/repo_inventory_summary.json"
            summary.parent.mkdir(parents=True)
            summary.write_text(json.dumps({"yml_yaml_files": 1, "github_workflow_yml_files": 0}), encoding="utf-8")
            records = [
                mod.FileRecord(path="a.yml", category="configuration_or_ledger", sha256="1", bytes=1, lines=1),
                mod.FileRecord(path="b.yml", category="configuration_or_ledger", sha256="2", bytes=1, lines=1),
            ]
            findings = []
            mod.audit_cross_file(root, records, findings)
            self.assertIn("VERSIONED_INVENTORY_STALE", {item.code for item in findings})


if __name__ == "__main__":
    unittest.main()
