from pathlib import Path

from tools.branch_maturity_gate_v2 import evaluate, valid_transition


def test_topology():
    assert valid_transition("feature/x", "rll/lab")
    assert valid_transition("rll/lab", "rll/integration")
    assert valid_transition("rll/integration", "rll/release")
    assert valid_transition("rll/release", "main")
    assert not valid_transition("feature/x", "main")


def test_claim_true_in_policy_blocks(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/state.json").write_text('{"claim_allowed": true}\n', encoding="utf-8")
    data = evaluate(
        tmp_path,
        "rll/integration",
        "rll/release",
        ["data/state.json", "artifacts/receipt.json"],
    )
    assert data["decision"] == "BLOCKED"
    assert "CLAIM_ALLOWED_TRUE:data/state.json" in data["residuals"]


def test_nested_yaml_claim_true_blocks(tmp_path: Path):
    (tmp_path / "governance").mkdir()
    (tmp_path / "governance/policy.yml").write_text(
        "outer:\n  scientific:\n    claim_allowed: true\n",
        encoding="utf-8",
    )
    data = evaluate(
        tmp_path,
        "feature/x",
        "rll/lab",
        ["governance/policy.yml"],
    )
    assert data["decision"] == "BLOCKED"
    assert "CLAIM_ALLOWED_TRUE:governance/policy.yml" in data["residuals"]


def test_quoted_documentation_marker_is_not_active_claim(tmp_path: Path):
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github/workflow-contract.yml").write_text(
        "schema: rll.workflow_contract.v1\n"
        "claim_allowed: false\n"
        "documentation:\n"
        "  required_markers:\n"
        "    governance.md:\n"
        "      - \"claim_allowed=true\"\n",
        encoding="utf-8",
    )
    data = evaluate(
        tmp_path,
        "feature/x",
        "rll/lab",
        [".github/workflow-contract.yml"],
    )
    assert data["decision"] == "PASS"
    assert not any(x.startswith("CLAIM_ALLOWED_TRUE") for x in data["residuals"])


def test_malformed_structured_policy_fails_closed(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/state.json").write_text('{"claim_allowed": false,', encoding="utf-8")
    data = evaluate(
        tmp_path,
        "feature/x",
        "rll/lab",
        ["data/state.json"],
    )
    assert data["decision"] == "BLOCKED"
    assert "STRUCTURED_PARSE_ERROR:data/state.json" in data["residuals"]


def test_string_truthy_value_on_claim_key_blocks(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/state.toml").write_text('claim_allowed = "yes"\n', encoding="utf-8")
    data = evaluate(
        tmp_path,
        "feature/x",
        "rll/lab",
        ["data/state.toml"],
    )
    assert data["decision"] == "BLOCKED"
    assert "CLAIM_ALLOWED_TRUE:data/state.toml" in data["residuals"]


def test_release_requires_evidence_or_gap(tmp_path: Path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/x.py").write_text("pass\n", encoding="utf-8")
    data = evaluate(tmp_path, "rll/integration", "rll/release", ["tools/x.py"])
    assert "RELEASE_REQUIRES_EVIDENCE_OR_EXPLICIT_GAP" in data["residuals"]
