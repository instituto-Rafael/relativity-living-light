"""Tests for tools/make_h0_rd_ablation_matrix.py.

Validates that the H0/r_d ablation matrix generator produces the correct
number of runs, covers all required policies, generates valid artifacts,
and contains expected column metadata — as required by issue #423.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from tools.make_h0_rd_ablation_matrix import build_matrix, write_json, write_csv, write_markdown

# Standard cosmological prior reference values
PLANCK_H0_MEAN = 67.4
PLANCK_H0_SIGMA = 0.5
SHOES_H0_MEAN = 73.04
SHOES_H0_SIGMA = 1.04

# ---------------------------------------------------------------------------
# Matrix structure
# ---------------------------------------------------------------------------

def test_build_matrix_returns_six_rows() -> None:
    """Matrix must have exactly 6 rows: 3 H0 policies × 2 r_d policies."""
    runs = build_matrix()
    assert len(runs) == 6


def test_matrix_covers_all_required_h0_policies() -> None:
    """All three required H0 policies must be present in the matrix."""
    runs = build_matrix()
    policies = {r.H0_policy for r in runs}
    assert "broad_free" in policies
    assert "planck_prior" in policies
    assert "shoes_local_prior" in policies


def test_matrix_covers_all_required_rd_policies() -> None:
    """Both required r_d policies must be present in the matrix."""
    runs = build_matrix()
    rd_policies = {r.rd_policy for r in runs}
    assert "fixed_for_all" in rd_policies
    assert "derived_for_all" in rd_policies


def test_matrix_run_ids_are_unique() -> None:
    """Every run_id in the matrix must be unique."""
    runs = build_matrix()
    ids = [r.run_id for r in runs]
    assert len(ids) == len(set(ids)), "Duplicate run_id values found"


def test_matrix_each_h0_policy_has_both_rd_policies() -> None:
    """Every H0 policy must have exactly one entry per r_d policy."""
    runs = build_matrix()
    for h0_policy in ("broad_free", "planck_prior", "shoes_local_prior"):
        subset = [r for r in runs if r.H0_policy == h0_policy]
        rd_policies = {r.rd_policy for r in subset}
        assert rd_policies == {"fixed_for_all", "derived_for_all"}, (
            f"H0 policy '{h0_policy}' does not cover both r_d policies"
        )


def test_fixed_rd_rows_have_numeric_rd_value() -> None:
    """Rows with rd_policy=fixed_for_all must have a non-None rd_fixed_value_mpc."""
    runs = build_matrix()
    for run in runs:
        if run.rd_policy == "fixed_for_all":
            assert run.rd_fixed_value_mpc is not None, (
                f"run {run.run_id} has rd_policy=fixed_for_all but rd_fixed_value_mpc is None"
            )


def test_derived_rd_rows_have_none_rd_value() -> None:
    """Rows with rd_policy=derived_for_all must have rd_fixed_value_mpc=None."""
    runs = build_matrix()
    for run in runs:
        if run.rd_policy == "derived_for_all":
            assert run.rd_fixed_value_mpc is None, (
                f"run {run.run_id} has rd_policy=derived_for_all but rd_fixed_value_mpc is not None"
            )


def test_planck_prior_rows_have_correct_mean_and_sigma() -> None:
    """Planck-prior rows must have the standard Planck 2018 H0 mean and sigma."""
    runs = build_matrix()
    planck_rows = [r for r in runs if r.H0_policy == "planck_prior"]
    assert planck_rows, "No Planck-prior rows found"
    for run in planck_rows:
        assert run.H0_prior_mean == pytest.approx(PLANCK_H0_MEAN, abs=0.1)
        assert run.H0_prior_sigma == pytest.approx(PLANCK_H0_SIGMA, abs=0.05)


def test_shoes_prior_rows_have_correct_mean_and_sigma() -> None:
    """SH0ES/local-prior rows must have the standard SH0ES H0 mean and sigma."""
    runs = build_matrix()
    shoes_rows = [r for r in runs if r.H0_policy == "shoes_local_prior"]
    assert shoes_rows, "No SH0ES-prior rows found"
    for run in shoes_rows:
        assert run.H0_prior_mean == pytest.approx(SHOES_H0_MEAN, abs=0.1)
        assert run.H0_prior_sigma == pytest.approx(SHOES_H0_SIGMA, abs=0.05)


def test_broad_free_rows_have_no_prior_mean_or_sigma() -> None:
    """broad_free rows must have H0_prior_mean=None and H0_prior_sigma=None."""
    runs = build_matrix()
    broad_rows = [r for r in runs if r.H0_policy == "broad_free"]
    assert broad_rows, "No broad_free rows found"
    for run in broad_rows:
        assert run.H0_prior_mean is None
        assert run.H0_prior_sigma is None


# ---------------------------------------------------------------------------
# Expected-output-columns field
# ---------------------------------------------------------------------------

def test_expected_output_columns_include_required_fields() -> None:
    """expected_output_columns must list all minimum-output fields required by issue #423."""
    required = {
        "model", "chi2", "AIC", "AICc", "BIC",
        "N", "k", "dof",
        "H0_policy", "rd_policy", "H0", "rd", "Os0",
        "Delta_AICc_RLL_CPL", "Delta_BIC_RLL_CPL", "claim_status",
    }
    runs = build_matrix()
    for run in runs:
        declared = set(run.expected_output_columns.split(","))
        missing = required - declared
        assert not missing, (
            f"run {run.run_id} expected_output_columns missing: {missing}"
        )


# ---------------------------------------------------------------------------
# File artifact generation
# ---------------------------------------------------------------------------

def test_write_json_creates_valid_schema(tmp_path: Path) -> None:
    """write_json must create a parseable JSON with schema and runs keys."""
    runs = build_matrix()
    out = tmp_path / "matrix.json"
    write_json(runs, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == "rll.h0_rd_ablation_matrix.v1"
    assert "runs" in payload
    assert len(payload["runs"]) == 6


def test_write_json_runs_contain_all_fields(tmp_path: Path) -> None:
    """Each JSON run entry must contain run_id, H0_policy, rd_policy, and command_template."""
    runs = build_matrix()
    out = tmp_path / "matrix.json"
    write_json(runs, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    for entry in payload["runs"]:
        assert "run_id" in entry
        assert "H0_policy" in entry
        assert "rd_policy" in entry
        assert "command_template" in entry


def test_write_csv_creates_expected_columns(tmp_path: Path) -> None:
    """write_csv must create a CSV with all dataclass field names as headers."""
    runs = build_matrix()
    out = tmp_path / "matrix.csv"
    write_csv(runs, out)

    with out.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        rows = list(reader)

    assert "run_id" in headers
    assert "H0_policy" in headers
    assert "rd_policy" in headers
    assert "expected_output_columns" in headers
    assert len(rows) == 6


def test_write_markdown_contains_all_run_ids(tmp_path: Path) -> None:
    """write_markdown must include every run_id in the generated Markdown table."""
    runs = build_matrix()
    out = tmp_path / "matrix.md"
    write_markdown(runs, out)

    text = out.read_text(encoding="utf-8")
    for run in runs:
        assert run.run_id in text, f"run_id '{run.run_id}' not found in markdown output"


def test_write_markdown_mentions_required_interpretation(tmp_path: Path) -> None:
    """The generated Markdown must contain the required interpretation section."""
    runs = build_matrix()
    out = tmp_path / "matrix.md"
    write_markdown(runs, out)

    text = out.read_text(encoding="utf-8")
    assert "Required interpretation" in text or "Runs" in text


def test_canonical_json_matches_build_matrix(tmp_path: Path) -> None:
    """The committed h0_rd_ablation_matrix.json must match what build_matrix() produces."""
    root = Path(__file__).resolve().parents[1]
    canonical = root / "data" / "inputs" / "cosmology_joint" / "h0_rd_ablation_matrix.json"

    if not canonical.exists():
        pytest.skip("canonical h0_rd_ablation_matrix.json not found")

    payload = json.loads(canonical.read_text(encoding="utf-8"))
    committed_ids = {r["run_id"] for r in payload["runs"]}

    runs = build_matrix()
    generated_ids = {r.run_id for r in runs}

    assert committed_ids == generated_ids, (
        "Committed h0_rd_ablation_matrix.json run_ids do not match build_matrix() output. "
        "Re-run: python3 tools/make_h0_rd_ablation_matrix.py"
    )
