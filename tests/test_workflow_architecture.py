from pathlib import Path

import yaml

from tools.workflow_architecture import (
    audit_repository,
    load_contract,
    parse_all_yaml,
    write_reports,
)


VALID_WORKFLOW = '''name: Managed gate
"on":
  pull_request:
permissions:
  contents: read
concurrency:
  group: managed-${{ github.ref }}
  cancel-in-progress: true
jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Validate
        run: python tools/check.py
      - name: Upload receipt
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: receipt
          path: artifacts/
'''


def _repo(tmp_path: Path, workflow_text: str = VALID_WORKFLOW) -> Path:
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflow-architecture").mkdir(parents=True)
    (tmp_path / ".github/workflows/managed.yml").write_text(workflow_text, encoding="utf-8")
    contract = {
        "schema": "rll.github_actions_architecture.v1",
        "claim_allowed": False,
        "managed_workflows": {
            ".github/workflows/managed.yml": {
                "class": "structural",
                "require": [
                    "permissions",
                    "concurrency",
                    "job_timeout",
                    "checkout_without_persistent_credentials",
                    "always_upload_receipt",
                    "externalized_algorithm",
                ],
            }
        },
        "policy": {
            "thresholds": {
                "max_inline_run_lines_managed": 4,
                "max_inline_run_lines_legacy_warning": 10,
            }
        },
    }
    (tmp_path / ".github/workflow-architecture/invariants.v1.yml").write_text(
        yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
    )
    return tmp_path


def _codes(findings):
    return {item.code for item in findings}


def test_valid_managed_workflow_has_no_architecture_errors(tmp_path):
    root = _repo(tmp_path)
    contract = load_contract(root, Path(".github/workflow-architecture/invariants.v1.yml"))
    findings = audit_repository(root, contract)
    assert not [item for item in findings if item.severity == "ERROR"]
    assert "MUTABLE_ACTION_REFERENCE" in _codes(findings)


def test_missing_permissions_and_timeout_fail_closed(tmp_path):
    text = VALID_WORKFLOW.replace("permissions:\n  contents: read\n", "").replace(
        "    timeout-minutes: 10\n", ""
    )
    root = _repo(tmp_path, text)
    contract = load_contract(root, Path(".github/workflow-architecture/invariants.v1.yml"))
    codes = _codes(audit_repository(root, contract))
    assert "MANAGED_PERMISSIONS_MISSING" in codes
    assert "MANAGED_TIMEOUT_MISSING" in codes


def test_checkout_credentials_are_fail_closed(tmp_path):
    root = _repo(tmp_path, VALID_WORKFLOW.replace("persist-credentials: false", "persist-credentials: true"))
    contract = load_contract(root, Path(".github/workflow-architecture/invariants.v1.yml"))
    assert "CHECKOUT_CREDENTIALS_PERSIST" in _codes(audit_repository(root, contract))


def test_untrusted_context_in_run_is_rejected(tmp_path):
    text = VALID_WORKFLOW.replace(
        "run: python tools/check.py",
        'run: echo "${{ github.event.pull_request.title }}"',
    )
    root = _repo(tmp_path, text)
    contract = load_contract(root, Path(".github/workflow-architecture/invariants.v1.yml"))
    assert "UNTRUSTED_CONTEXT_IN_RUN" in _codes(audit_repository(root, contract))


def test_oversized_inline_program_is_rejected_for_managed_workflow(tmp_path):
    long_block = "run: |\n" + "".join(f"          echo {i}\n" for i in range(6))
    root = _repo(tmp_path, VALID_WORKFLOW.replace("run: python tools/check.py", long_block))
    contract = load_contract(root, Path(".github/workflow-architecture/invariants.v1.yml"))
    assert "OVERSIZED_INLINE_PROGRAM" in _codes(audit_repository(root, contract))


def test_pull_request_target_is_rejected(tmp_path):
    root = _repo(tmp_path, VALID_WORKFLOW.replace("pull_request:", "pull_request_target:"))
    contract = load_contract(root, Path(".github/workflow-architecture/invariants.v1.yml"))
    assert "PULL_REQUEST_TARGET_FORBIDDEN" in _codes(audit_repository(root, contract))


def test_reports_preserve_claim_boundary_and_residuals(tmp_path):
    root = _repo(tmp_path)
    contract_path = Path(".github/workflow-architecture/invariants.v1.yml")
    contract = load_contract(root, contract_path)
    rows = parse_all_yaml(root)
    findings = audit_repository(root, contract)
    payload = write_reports(root / "artifacts", root, contract_path, rows, findings)
    assert payload["claim_allowed"] is False
    assert payload["publication_effect"] == "NONE"
    assert payload["decision"] == "PASS"
    assert payload["architecture_warnings"] >= 1
    assert (root / "artifacts/workflow_architecture_report.json").exists()
    assert (root / "artifacts/WORKFLOW_ARCHITECTURE_REPORT.md").exists()
    assert (root / "artifacts/yaml_parse_report.tsv").exists()
