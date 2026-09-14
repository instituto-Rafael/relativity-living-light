from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate_six_sigma_real_data_controls.py"


def load_module():
    spec = importlib.util.spec_from_file_location("six_sigma_controls_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def complete_corpus() -> str:
    return """
    DMAIC
    claim_boundary
    checksums
    strict_real_data
    artifact_only_reviewed_pr_required
    baseline
    artifact
    No superiority claim unless real-data metrics pass predefined thresholds
    """


def test_current_artifact_only_commit_policy_is_accepted() -> None:
    module = load_module()
    assert module.missing_controls(complete_corpus()) == []


def test_legacy_commit_term_remains_accepted() -> None:
    module = load_module()
    corpus = complete_corpus().replace("artifact_only_reviewed_pr_required", "commit_light_artifacts")
    assert module.missing_controls(corpus) == []


def test_missing_semantic_control_is_reported() -> None:
    module = load_module()
    corpus = complete_corpus().replace("strict_real_data", "")
    assert module.missing_controls(corpus) == ["strict real-data mode"]
