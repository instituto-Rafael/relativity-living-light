from pathlib import Path
from tools.branch_maturity_gate_v2 import evaluate, valid_transition


def test_topology():
    assert valid_transition("feature/x","rll/lab")
    assert valid_transition("rll/lab","rll/integration")
    assert valid_transition("rll/integration","rll/release")
    assert valid_transition("rll/release","main")
    assert not valid_transition("feature/x","main")


def test_claim_true_in_policy_blocks(tmp_path: Path):
    (tmp_path/"data").mkdir(); (tmp_path/"data/state.json").write_text('{"claim_allowed": true}\n')
    data=evaluate(tmp_path,"rll/integration","rll/release",["data/state.json","artifacts/receipt.json"])
    assert data["decision"]=="BLOCKED"
    assert any(x.startswith("CLAIM_ALLOWED_TRUE") for x in data["residuals"])


def test_release_requires_evidence_or_gap(tmp_path: Path):
    (tmp_path/"tools").mkdir(); (tmp_path/"tools/x.py").write_text("pass\n")
    data=evaluate(tmp_path,"rll/integration","rll/release",["tools/x.py"])
    assert "RELEASE_REQUIRES_EVIDENCE_OR_EXPLICIT_GAP" in data["residuals"]
