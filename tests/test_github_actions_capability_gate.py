from pathlib import Path

import yaml

from tools.github_actions_capability_gate import audit, write_reports


REQUIRED = [
    "workflow_syntax_and_events",
    "least_privilege_token",
    "immutable_action_pinning",
    "concurrency_and_timeouts",
    "reusable_workflows",
    "artifacts_and_receipts",
    "dependency_review",
    "codeql_actions_python",
    "dependabot_actions",
    "code_ownership",
    "security_policy",
    "branch_rulesets",
    "required_status_checks",
    "protected_environments",
    "secret_scanning_push_protection",
    "artifact_attestations",
    "oidc_boundary",
    "audit_log_and_settings_evidence",
]


def _repo(tmp_path: Path) -> Path:
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflow-architecture").mkdir(parents=True)
    (tmp_path / ".github/CODEOWNERS").write_text("* @owner\n", encoding="utf-8")
    (tmp_path / ".github/SECURITY.md").write_text("# Security\n", encoding="utf-8")
    (tmp_path / ".github/dependabot.yml").write_text("version: 2\nupdates: []\n", encoding="utf-8")
    workflow = """name: Assurance
'on':
  pull_request:
permissions:
  contents: read
concurrency:
  group: assurance-${{ github.ref }}
jobs:
  platform-capability-contract:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@1111111111111111111111111111111111111111
  dependency-review:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/dependency-review-action@2222222222222222222222222222222222222222
  codeql:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: github/codeql-action/init@3333333333333333333333333333333333333333
"""
    (tmp_path / ".github/workflows/github-platform-assurance.yml").write_text(workflow, encoding="utf-8")
    contract = {"inventory": {"active_workflows": 1}}
    (tmp_path / ".github/workflow-contract.yml").write_text(yaml.safe_dump(contract), encoding="utf-8")
    implemented = {
        "dependabot_actions": [".github/dependabot.yml"],
        "code_ownership": [".github/CODEOWNERS"],
        "security_policy": [".github/SECURITY.md"],
        "dependency_review": [".github/workflows/github-platform-assurance.yml"],
        "codeql_actions_python": [".github/workflows/github-platform-assurance.yml"],
    }
    capabilities = []
    for capability_id in REQUIRED:
        if capability_id in implemented:
            capabilities.append({
                "id": capability_id,
                "state": "IMPLEMENTED_REPOSITORY",
                "evidence": implemented[capability_id],
            })
        else:
            capabilities.append({
                "id": capability_id,
                "state": "TOKEN_VAZIO_EXTERNAL_SETTING",
                "setting_scope": "repository",
                "verified": False,
                "f_next": "Inspect the repository setting and append a receipt.",
                "evidence": [],
            })
    matrix = {
        "schema": "rll.github_actions_capabilities.v1",
        "claim_allowed": False,
        "capabilities": capabilities,
    }
    (tmp_path / ".github/workflow-architecture/github-actions-capabilities.v1.yml").write_text(
        yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8"
    )
    return tmp_path


def _codes(findings):
    return {item.code for item in findings}


def test_valid_capability_contract_passes(tmp_path):
    root = _repo(tmp_path)
    findings, payload = audit(
        root,
        Path(".github/workflow-architecture/github-actions-capabilities.v1.yml"),
        Path(".github/workflow-contract.yml"),
    )
    assert not [item for item in findings if item.severity == "ERROR"]
    assert payload["decision"] == "PASS"
    assert payload["residual_state"] == "TOKEN_VAZIO_EXTERNAL_SETTINGS"


def test_missing_required_capability_fails(tmp_path):
    root = _repo(tmp_path)
    path = root / ".github/workflow-architecture/github-actions-capabilities.v1.yml"
    matrix = yaml.safe_load(path.read_text(encoding="utf-8"))
    matrix["capabilities"] = matrix["capabilities"][1:]
    path.write_text(yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8")
    findings, _ = audit(root, path.relative_to(root), Path(".github/workflow-contract.yml"))
    assert "REQUIRED_CAPABILITIES_MISSING" in _codes(findings)


def test_implemented_evidence_must_exist(tmp_path):
    root = _repo(tmp_path)
    path = root / ".github/workflow-architecture/github-actions-capabilities.v1.yml"
    matrix = yaml.safe_load(path.read_text(encoding="utf-8"))
    matrix["capabilities"][0]["state"] = "IMPLEMENTED_REPOSITORY"
    matrix["capabilities"][0]["evidence"] = ["missing.file"]
    path.write_text(yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8")
    findings, _ = audit(root, path.relative_to(root), Path(".github/workflow-contract.yml"))
    assert "EVIDENCE_MISSING" in _codes(findings)


def test_external_setting_needs_next_step_and_cannot_claim_verified(tmp_path):
    root = _repo(tmp_path)
    path = root / ".github/workflow-architecture/github-actions-capabilities.v1.yml"
    matrix = yaml.safe_load(path.read_text(encoding="utf-8"))
    matrix["capabilities"][0]["verified"] = True
    matrix["capabilities"][0]["f_next"] = ""
    path.write_text(yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8")
    findings, _ = audit(root, path.relative_to(root), Path(".github/workflow-contract.yml"))
    codes = _codes(findings)
    assert "FALSE_EXTERNAL_VERIFICATION" in codes
    assert "EXTERNAL_NEXT_STEP" in codes


def test_assurance_action_must_use_full_sha(tmp_path):
    root = _repo(tmp_path)
    path = root / ".github/workflows/github-platform-assurance.yml"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "actions/checkout@1111111111111111111111111111111111111111",
        "actions/checkout@v4",
    ), encoding="utf-8")
    findings, _ = audit(
        root,
        Path(".github/workflow-architecture/github-actions-capabilities.v1.yml"),
        Path(".github/workflow-contract.yml"),
    )
    assert any(item.code == "MUTABLE_ACTION_REFERENCE" and item.severity == "ERROR" for item in findings)


def test_workflow_count_is_contractual(tmp_path):
    root = _repo(tmp_path)
    contract = root / ".github/workflow-contract.yml"
    contract.write_text(yaml.safe_dump({"inventory": {"active_workflows": 2}}), encoding="utf-8")
    findings, _ = audit(
        root,
        Path(".github/workflow-architecture/github-actions-capabilities.v1.yml"),
        Path(".github/workflow-contract.yml"),
    )
    assert "WORKFLOW_COUNT_MISMATCH" in _codes(findings)


def test_report_preserves_claim_boundary(tmp_path):
    root = _repo(tmp_path)
    _, payload = audit(
        root,
        Path(".github/workflow-architecture/github-actions-capabilities.v1.yml"),
        Path(".github/workflow-contract.yml"),
    )
    write_reports(payload, root / "artifacts")
    assert payload["claim_allowed"] is False
    assert payload["publication_effect"] == "NONE"
    assert (root / "artifacts/github_actions_capability_report.json").is_file()
    assert (root / "artifacts/GITHUB_PLATFORM_ASSURANCE_REPORT.md").is_file()
