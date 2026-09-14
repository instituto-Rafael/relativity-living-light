from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "close_scientific_cycle.py"
spec = importlib.util.spec_from_file_location("close_cycle", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_verified_bayes_contract() -> None:
    assert module.verified_bayes({
        "state": "VERIFIED",
        "claim_allowed": False,
        "bayes_mode": "inference",
        "evidence_path": "results/structure_d/bayes_evidence_inference.csv",
    })
    assert not module.verified_bayes({"state": "TOKEN_VAZIO"})


def test_verified_replication_contract() -> None:
    assert module.verified_replication({
        "state": "PASS_INDEPENDENT_REPLICATION",
        "claim_allowed": False,
        "same_inputs": True,
        "same_model_contract": True,
        "numerical_tolerance_pass": True,
    })
    assert not module.verified_replication({
        "state": "PASS_INDEPENDENT_REPLICATION",
        "claim_allowed": True,
    })
