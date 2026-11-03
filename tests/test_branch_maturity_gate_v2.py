from pathlib import Path
import subprocess
from tools.branch_maturity_gate_v2 import (
    contains_claim_true,
    changed,
    deleted,
    evaluate,
    file_has_claim_true,
    valid_transition,
)


def test_topology():
    assert valid_transition("feature/x", "rll/lab")
    assert valid_transition("rll/lab", "rll/integration")
    assert valid_transition("rll/integration", "rll/release")
    assert valid_transition("rll/release", "main")
    assert not valid_transition("feature/x", "main")


def test_claim_true_in_policy_blocks(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/state.json").write_text('{"claim_allowed": true}\n', encoding="utf-8")
    data = evaluate(tmp_path, "rll/integration", "rll/release", ["data/state.json", "artifacts/receipt.json"])
    assert data["decision"] == "BLOCKED"
    assert "CLAIM_ALLOWED_TRUE:data/state.json" in data["residuals"]


def test_nested_yaml_claim_true_blocks(tmp_path: Path):
    (tmp_path / "governance").mkdir()
    (tmp_path / "governance/policy.yml").write_text("outer:\n  scientific:\n    claim_allowed: true\n", encoding="utf-8")
    data = evaluate(tmp_path, "feature/x", "rll/lab", ["governance/policy.yml"])
    assert data["decision"] == "BLOCKED"
    assert "CLAIM_ALLOWED_TRUE:governance/policy.yml" in data["residuals"]


def test_quoted_documentation_marker_is_not_active_claim(tmp_path: Path):
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github/workflow-contract.yml").write_text(
        "schema: rll.workflow_contract.v1\nclaim_allowed: false\ndocumentation:\n  required_markers:\n    governance.md:\n      - \"claim_allowed=true\"\n",
        encoding="utf-8",
    )
    data = evaluate(tmp_path, "feature/x", "rll/lab", [".github/workflow-contract.yml"])
    assert data["decision"] == "PASS"
    assert not any(x.startswith("CLAIM_ALLOWED_TRUE") for x in data["residuals"])


def test_malformed_structured_policy_fails_closed(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/state.json").write_text('{"claim_allowed": false,', encoding="utf-8")
    data = evaluate(tmp_path, "feature/x", "rll/lab", ["data/state.json"])
    assert data["decision"] == "BLOCKED"
    assert "STRUCTURED_PARSE_ERROR:data/state.json" in data["residuals"]


def test_string_truthy_value_on_claim_key_blocks(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/state.toml").write_text('claim_allowed = "yes"\n', encoding="utf-8")
    data = evaluate(tmp_path, "feature/x", "rll/lab", ["data/state.toml"])
    assert data["decision"] == "BLOCKED"
    assert "CLAIM_ALLOWED_TRUE:data/state.toml" in data["residuals"]


def test_yaml_and_toml_claim_assignments_still_block():
    assert contains_claim_true("claim_allowed: true\n")
    assert contains_claim_true("claim_allowed = true\n")
    assert contains_claim_true('x: 1\n"claim_allowed": true\n')


def test_quoted_documentation_marker_is_not_assignment(tmp_path: Path):
    (tmp_path/".github").mkdir()
    path=tmp_path/".github/workflow-contract.yml"
    path.write_text('required_markers:\n  file.md:\n    - "claim_allowed=true"\n', encoding="utf-8")
    assert not contains_claim_true(path.read_text(encoding="utf-8"))
    data=evaluate(tmp_path,"feature/x","rll/lab",[".github/workflow-contract.yml"])
    assert data["decision"]=="PASS"
    assert not any(x.startswith("CLAIM_ALLOWED_TRUE") for x in data["residuals"])


def test_documented_claim_true_string_does_not_promote_claim(tmp_path: Path):
    contract=tmp_path/"contract.yml"
    contract.write_text('claim_allowed: false\nrequired_markers:\n  - "claim_allowed=true"\n',encoding="utf-8")
    assert file_has_claim_true(contract) is False


def test_nested_json_claim_true_still_blocks(tmp_path: Path):
    policy=tmp_path/"state.json"
    policy.write_text('{"outer":{"claim_allowed":true}}\n',encoding="utf-8")
    assert file_has_claim_true(policy) is True


def test_release_requires_evidence_or_gap(tmp_path: Path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/x.py").write_text("pass\n", encoding="utf-8")
    data = evaluate(tmp_path, "rll/integration", "rll/release", ["tools/x.py"])
    assert "RELEASE_REQUIRES_EVIDENCE_OR_EXPLICIT_GAP" in data["residuals"]


def test_lab_to_main_shortcut_stays_blocked(tmp_path: Path):
    data = evaluate(tmp_path, "rll/lab", "main", ["docs/receipt.md"])
    assert data["decision"] == "BLOCKED"
    assert "INVALID_BRANCH_TRANSITION" in data["residuals"]


def test_final_stage_core_deletion_requires_review_even_with_receipt(tmp_path: Path):
    for base, head in [("rll/release", "rll/integration"), ("main", "rll/release")]:
        data = evaluate(
            tmp_path, head, base,
            ["data/cosmology.csv", "governance/receipts/review.md"],
            deleted_files=["data/cosmology.csv"],
        )
        assert data["decision"] == "BLOCKED"
        assert "CRITICAL_DELETION_REQUIRES_REVIEW:data/cosmology.csv" in data["residuals"]
        assert data["deleted_files"] == ["data/cosmology.csv"]
        assert data["claim_allowed"] is False


def test_noncritical_document_retirement_remains_allowed(tmp_path: Path):
    data = evaluate(
        tmp_path, "rll/release", "main", ["docs/retired.md"],
        deleted_files=["docs/retired.md"],
    )
    assert data["decision"] == "PASS"
    assert data["deleted_files"] == ["docs/retired.md"]


def test_lab_stage_retains_experimental_change_freedom(tmp_path: Path):
    data = evaluate(
        tmp_path, "work/scoped", "rll/lab", ["data/fixture.csv"],
        deleted_files=["data/fixture.csv"],
    )
    assert data["decision"] == "PASS"


def test_git_diff_exposes_deleted_source_in_both_lists(tmp_path: Path):
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, text=True,
            capture_output=True,
        ).stdout.strip()

    git("init", "-q")
    (tmp_path / "data").mkdir()
    (tmp_path / "data/source.txt").write_text("frozen source\n", encoding="utf-8")
    git("add", "data/source.txt")
    git("-c", "user.name=CI", "-c", "user.email=ci@example.org", "commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    git("rm", "-q", "data/source.txt")
    git("-c", "user.name=CI", "-c", "user.email=ci@example.org", "commit", "-qm", "remove")
    head = git("rev-parse", "HEAD")
    assert "data/source.txt" in changed(base, head)
    assert deleted(base, head) == ["data/source.txt"]
