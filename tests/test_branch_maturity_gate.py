from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "branch_maturity_gate.py"
spec = importlib.util.spec_from_file_location("branch_maturity_gate", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_promotion_chain_is_fail_closed() -> None:
    assert module.promotion_for("feat/new-likelihood", "rll/lab").valid
    assert module.promotion_for("rll/lab", "rll/integration").valid
    assert module.promotion_for("rll/integration", "rll/release").valid
    assert module.promotion_for("rll/release", "main").valid
    assert not module.promotion_for("feat/bypass", "main").valid
    assert not module.promotion_for("rll/lab", "main").valid


def test_domain_amplitude_classification() -> None:
    assert "data" in module.domains_for("data/real/bao.csv")
    assert "implementation" in module.domains_for("tools/run_model.py")
    assert "tests" in module.domains_for("tests/test_model.py")
    assert "governance" in module.domains_for(".github/workflow-contract.yml")
    assert "evidence" in module.domains_for("artifacts/evidence_receipt.json")


def test_sensitive_paths_are_rejected() -> None:
    assert module.forbidden_path(".env")
    assert module.forbidden_path("keys/private.pem")
    assert module.forbidden_path(".ssh/id_ed25519")
    assert not module.forbidden_path("docs/environment.md")


def test_release_science_requires_evidence_or_explicit_gap(tmp_path: Path) -> None:
    source = tmp_path / "tools" / "model.py"
    source.parent.mkdir(parents=True)
    source.write_text("claim_allowed = False\n", encoding="utf-8")
    payload = module.evaluate(
        root=tmp_path,
        head_ref="rll/integration",
        base_ref="rll/release",
        base_sha="base",
        head_sha="head",
        tests_status="success",
        architecture_status="success",
        docs_status="success",
        workflow="test",
        job="gate",
        files=["tools/model.py"],
    )
    assert payload["decision"] == "BLOCKED"
    assert any(item["code"] == "EVIDENCE_OR_EXPLICIT_GAP_REQUIRED" for item in payload["residuals"])

    source.write_text("TOKEN_VAZIO\nF_next: execute independent replication\n", encoding="utf-8")
    payload = module.evaluate(
        root=tmp_path,
        head_ref="rll/integration",
        base_ref="rll/release",
        base_sha="base",
        head_sha="head",
        tests_status="success",
        architecture_status="success",
        docs_status="success",
        workflow="test",
        job="gate",
        files=["tools/model.py"],
    )
    assert payload["decision"] == "PASS_RELEASE"
    assert payload["claim_allowed"] is False


def test_claim_allowed_true_is_blocking(tmp_path: Path) -> None:
    policy = tmp_path / "governance" / "policy.yml"
    policy.parent.mkdir(parents=True)
    policy.write_text("claim_allowed: true\n", encoding="utf-8")
    _, findings = module.inspect_files(tmp_path, ["governance/policy.yml"])
    assert any(item.code == "CLAIM_ALLOWED_TRUE" for item in findings)
