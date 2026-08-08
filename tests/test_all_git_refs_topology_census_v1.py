from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/audit_all_git_refs_v1.py"
spec = importlib.util.spec_from_file_location("ref_census", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_classify_identical():
    assert module.classify_counts(0, 0) == "IDENTICAL_TO_BASELINE"


def test_classify_absorbed_ahead_zero():
    assert module.classify_counts(12, 0) == "ANCESTOR_OF_BASELINE_AHEAD_ZERO"


def test_classify_descendant():
    assert module.classify_counts(0, 3) == "DESCENDANT_OF_BASELINE"


def test_classify_diverged():
    assert module.classify_counts(7, 2) == "DIVERGED_FROM_BASELINE"


def test_historical_denominator_is_measurement_reference_not_asserted_current_count():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "HISTORICAL_DENOMINATOR = 582" in source
    assert "observed == HISTORICAL_DENOMINATOR" in source
    assert "current_observed_ref_count" in source
    assert "no ref may disappear from the census" in source
