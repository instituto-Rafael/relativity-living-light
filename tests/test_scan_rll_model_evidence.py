"""Tests for tools/scan_rll_model_evidence.py — calculable evidence scanner."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = ROOT / "tools" / "scan_rll_model_evidence.py"

# Load and register the module once at module level so that @dataclass __module__
# lookups resolve correctly. Registration in sys.modules before exec_module is
# required because Python's dataclass decorator looks up the class's module at
# class-definition time and would raise AttributeError if the module is absent.
_scanner_spec = importlib.util.spec_from_file_location("scan_rll_model_evidence", SCANNER_PATH)
assert _scanner_spec is not None and _scanner_spec.loader is not None
_scanner_module = importlib.util.module_from_spec(_scanner_spec)
sys.modules.setdefault("scan_rll_model_evidence", _scanner_module)
_scanner_spec.loader.exec_module(_scanner_module)  # type: ignore[union-attr]


def load_scanner():
    return _scanner_module


# Convenience alias so tests can call scan(...) directly (mirrors direct-import style).
scan = _scanner_module.scan


# ---------------------------------------------------------------------------
# Helpers (compact style — used by tests imported from main branch)
# ---------------------------------------------------------------------------

_COLS = [
    "model", "chi2", "AIC", "AICc", "BIC",
    "N", "k", "dof",
    "H0", "Om", "Os0", "zt", "wt",
]


def _make_csv(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "results.csv"
    fieldnames = list(rows[0].keys()) if rows else _COLS
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _make_registry(tmp_path: Path) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema": "rll.parameter_origin_registry.v2"}), encoding="utf-8")
    return path


def _base_rows(
    h0_lcdm: float = 67.0,
    h0_wcdm: float = 67.5,
    h0_cpl: float = 68.0,
    h0_rll: float = 67.0,
    os0_rll: float = 0.05,
) -> list[dict]:
    """Four-model result table with configurable H0 and Os0 values."""
    return [
        {"model": "LCDM_joint", "chi2": "100", "AIC": "106", "AICc": "106.5", "BIC": "112",
         "N": "64", "k": "3", "dof": "61", "H0": str(h0_lcdm), "Om": "0.31", "Os0": "", "zt": "", "wt": ""},
        {"model": "wCDM_joint", "chi2": "99", "AIC": "107", "AICc": "107.5", "BIC": "115",
         "N": "64", "k": "4", "dof": "60", "H0": str(h0_wcdm), "Om": "0.31", "Os0": "", "zt": "", "wt": ""},
        {"model": "CPL_w0waCDM_joint", "chi2": "90", "AIC": "100", "AICc": "101", "BIC": "110",
         "N": "64", "k": "5", "dof": "59", "H0": str(h0_cpl), "Om": "0.30", "Os0": "", "zt": "", "wt": ""},
        {"model": "RLL_joint", "chi2": "95", "AIC": "107", "AICc": "108", "BIC": "118",
         "N": "64", "k": "6", "dof": "58", "H0": str(h0_rll), "Om": "0.31", "Os0": str(os0_rll), "zt": "1.2", "wt": "0.4"},
    ]


# ---------------------------------------------------------------------------
# Helpers (verbose style — used by tests from PR #422)
# ---------------------------------------------------------------------------


def _write_minimal_csv(path: Path, rows: list[dict]) -> None:
    """Write a minimal CSV to *path* in the expected format."""
    if not rows:
        path.write_text("model\n", encoding="utf-8")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_minimal_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "rll.parameter_origin_registry.v1", "parameters": {}}
    path.write_text(json.dumps(payload), encoding="utf-8")


def _make_four_model_rows(
    rll_os0: float = 0.0,
    rll_aicc: float = 130.0,
    rll_bic: float = 140.0,
    cpl_aicc: float = 80.0,
    cpl_bic: float = 90.0,
    n: int = 64,
) -> list[dict]:
    """Return four model rows (LCDM, wCDM, CPL, RLL) with plausible values."""
    k_lcdm, k_wcdm, k_cpl, k_rll = 5, 6, 7, 8
    return [
        {
            "model": "LCDM_joint_real",
            "chi2": "100.0",
            "AIC": "110.0",
            "AICc": "111.0",
            "BIC": "120.0",
            "N": str(n),
            "k": str(k_lcdm),
            "dof": str(n - k_lcdm),
            "H0": "67.0",
            "Om": "0.315",
            "OL": "0.685",
            "Ob_h2": "0.022",
            "sigma8": "0.8",
            "w": "",
            "w0": "",
            "wa": "",
            "Os0": "",
            "zt": "",
            "wt": "",
        },
        {
            "model": "wCDM_joint_real",
            "chi2": "99.0",
            "AIC": "111.0",
            "AICc": "112.0",
            "BIC": "121.0",
            "N": str(n),
            "k": str(k_wcdm),
            "dof": str(n - k_wcdm),
            "H0": "67.0",
            "Om": "0.315",
            "OL": "0.685",
            "Ob_h2": "0.022",
            "sigma8": "0.8",
            "w": "-1.0",
            "w0": "",
            "wa": "",
            "Os0": "",
            "zt": "",
            "wt": "",
        },
        {
            "model": "CPL_w0waCDM_joint_real",
            "chi2": "70.0",
            "AIC": "84.0",
            "AICc": str(cpl_aicc),
            "BIC": str(cpl_bic),
            "N": str(n),
            "k": str(k_cpl),
            "dof": str(n - k_cpl),
            "H0": "67.0",
            "Om": "0.315",
            "OL": "0.685",
            "Ob_h2": "0.022",
            "sigma8": "0.8",
            "w": "",
            "w0": "-0.9",
            "wa": "-0.5",
            "Os0": "",
            "zt": "",
            "wt": "",
        },
        {
            "model": "RLL_joint_real",
            "chi2": "95.0",
            "AIC": "111.0",
            "AICc": str(rll_aicc),
            "BIC": str(rll_bic),
            "N": str(n),
            "k": str(k_rll),
            "dof": str(n - k_rll),
            "H0": "67.0",
            "Om": "0.315",
            "OL": "0.685",
            "Ob_h2": "0.022",
            "sigma8": "0.8",
            "w": "",
            "w0": "",
            "wa": "",
            "Os0": str(rll_os0),
            "zt": "1.16",
            "wt": "0.4",
        },
    ]


# ---------------------------------------------------------------------------
# Basic scan tests
# ---------------------------------------------------------------------------


def test_scanner_module_loads() -> None:
    scanner = load_scanner()
    assert hasattr(scanner, "scan")
    assert hasattr(scanner, "write_json")
    assert hasattr(scanner, "write_markdown")


def test_scan_real_csv_returns_expected_claim_status() -> None:
    """Scan the committed CSV and confirm the expected CLAIM_BLOCKED state."""
    scanner = load_scanner()
    csv_path = ROOT / "results" / "structure_d" / "joint_real_likelihood.csv"
    registry_path = ROOT / "data" / "inputs" / "cosmology_joint" / "parameter_origin_registry.json"
    if not csv_path.exists():
        pytest.skip("committed CSV not available")

    result = scanner.scan(csv_path, registry_path)

    assert result.claim_status == "CLAIM_BLOCKED"
    assert result.best_by_AICc == "CPL_w0waCDM_joint_real"
    assert result.best_by_BIC == "CPL_w0waCDM_joint_real"


def test_scan_claim_blocked_when_rll_worse_than_cpl(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    _write_minimal_csv(csv_path, _make_four_model_rows(rll_aicc=130.0, cpl_aicc=80.0))
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    assert result.claim_status == "CLAIM_BLOCKED"
    assert result.best_by_AICc is not None
    assert "CPL" in result.best_by_AICc


def test_scan_pass_limited_when_rll_not_worse_than_cpl(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    # RLL AICc/BIC better (lower) than CPL
    _write_minimal_csv(csv_path, _make_four_model_rows(rll_aicc=75.0, rll_bic=85.0, cpl_aicc=80.0, cpl_bic=90.0))
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    assert result.claim_status == "PASS_LIMITED"


def test_scan_claim_blocked_when_rll_os0_collapsed(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    _write_minimal_csv(csv_path, _make_four_model_rows(rll_os0=0.0, rll_aicc=130.0))
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    assert result.claim_status == "CLAIM_BLOCKED"
    rll_row = next((ms for ms in result.model_scans if ms.model == "RLL"), None)
    assert rll_row is not None
    assert any("Os0" in flag for flag in rll_row.local_flags)


def test_scan_populates_model_scans_for_all_models(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    _write_minimal_csv(csv_path, _make_four_model_rows())
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    model_classes = {ms.model for ms in result.model_scans}
    assert model_classes == {"LCDM", "wCDM", "CPL", "RLL"}


def test_scan_delta_aicc_cpl_is_positive_when_rll_worse(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    _write_minimal_csv(csv_path, _make_four_model_rows(rll_aicc=130.0, cpl_aicc=80.0))
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    rll_row = next((ms for ms in result.model_scans if ms.model == "RLL"), None)
    assert rll_row is not None
    assert rll_row.delta_AICc_CPL is not None
    assert rll_row.delta_AICc_CPL > 0


def test_scan_missing_required_model_classes_blocks_claim(tmp_path: Path) -> None:
    """When a required baseline (e.g. CPL) is absent, claim must be blocked."""
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    rows = [r for r in _make_four_model_rows() if "CPL" not in r["model"]]
    _write_minimal_csv(csv_path, rows)
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    assert result.claim_status == "CLAIM_BLOCKED"
    assert "CPL" in result.missing_required_model_classes


def test_scan_h0_all_equal_flag_when_identical(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    rows = _make_four_model_rows()
    # All H0 values are already 67.0 in the fixture rows
    _write_minimal_csv(csv_path, rows)
    _write_minimal_registry(registry_path)

    result = scanner.scan(csv_path, registry_path)

    assert result.H0_all_equal is True
    assert any("H0 is identical" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# write_json / write_markdown output structure tests
# ---------------------------------------------------------------------------


def test_write_json_produces_valid_json_with_required_keys(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    _write_minimal_csv(csv_path, _make_four_model_rows())
    _write_minimal_registry(registry_path)
    result = scanner.scan(csv_path, registry_path)

    json_out = tmp_path / "evidence_scan.json"
    scanner.write_json(result, json_out)

    payload = json.loads(json_out.read_text(encoding="utf-8"))
    for key in ("claim_status", "best_by_AICc", "best_by_BIC", "H0_all_equal", "blocking_reasons", "warnings", "model_scans"):
        assert key in payload, f"missing key: {key}"


def test_write_markdown_includes_evidence_scan_section(tmp_path: Path) -> None:
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    _write_minimal_csv(csv_path, _make_four_model_rows())
    _write_minimal_registry(registry_path)
    result = scanner.scan(csv_path, registry_path)

    md_out = tmp_path / "evidence_scan.md"
    scanner.write_markdown(result, md_out)

    text = md_out.read_text(encoding="utf-8")
    assert "## Summary" in text
    assert "claim_status:" in text
    assert "best_by_AICc:" in text
    assert "best_by_BIC:" in text
    assert "H0_all_equal:" in text
    assert "## Model table" in text


def test_write_markdown_shows_token_vazio_for_missing_rll(tmp_path: Path) -> None:
    """When RLL row is absent, markdown must include TOKEN_VAZIO in diagnostics."""
    scanner = load_scanner()
    csv_path = tmp_path / "test.csv"
    registry_path = tmp_path / "registry.json"
    rows = [r for r in _make_four_model_rows() if "RLL" not in r["model"]]
    _write_minimal_csv(csv_path, rows)
    _write_minimal_registry(registry_path)
    result = scanner.scan(csv_path, registry_path)

    md_out = tmp_path / "evidence_scan.md"
    scanner.write_markdown(result, md_out)

    text = md_out.read_text(encoding="utf-8")
    assert "TOKEN_VAZIO" in text


# ---------------------------------------------------------------------------
# H0_all_equal — additional assertions (from PR #423)
# ---------------------------------------------------------------------------


def test_h0_all_equal_warning_references_ablation_matrix(tmp_path: Path) -> None:
    """The H0_all_equal warning must reference the ablation matrix file."""
    rows = _base_rows(h0_lcdm=60.0, h0_wcdm=60.0, h0_cpl=60.0, h0_rll=60.0)
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    assert result.H0_all_equal is True
    assert any("h0_rd_ablation_matrix" in w for w in result.warnings), (
        "H0_all_equal warning must reference the h0_rd_ablation_matrix file"
    )


def test_h0_not_all_equal_no_warning(tmp_path: Path) -> None:
    """When H0 values differ across models, H0_all_equal=False and no H0 warning is emitted."""
    rows = _base_rows(h0_lcdm=67.0, h0_wcdm=67.5, h0_cpl=68.0, h0_rll=67.2)
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    assert result.H0_all_equal is False
    assert not any("H0_all_equal" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Claim blocking — absent models (from PR #423)
# ---------------------------------------------------------------------------


def test_claim_blocked_when_rll_absent(tmp_path: Path) -> None:
    """When no RLL row is present, claim_status is CLAIM_BLOCKED."""
    rows = [
        {"model": "LCDM_joint", "chi2": "100", "AIC": "106", "AICc": "107", "BIC": "112",
         "N": "64", "k": "3", "dof": "61", "H0": "67", "Om": "0.31", "Os0": "", "zt": "", "wt": ""},
        {"model": "CPL_w0waCDM_joint", "chi2": "90", "AIC": "100", "AICc": "101", "BIC": "110",
         "N": "64", "k": "5", "dof": "59", "H0": "68", "Om": "0.30", "Os0": "", "zt": "", "wt": ""},
    ]
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    assert result.claim_status == "CLAIM_BLOCKED"
    assert any("RLL" in r for r in result.blocking_reasons)


def test_claim_blocked_when_cpl_absent(tmp_path: Path) -> None:
    """When no CPL row is present, claim_status is CLAIM_BLOCKED (no baseline for comparison)."""
    rows = [
        {"model": "LCDM_joint", "chi2": "100", "AIC": "106", "AICc": "107", "BIC": "112",
         "N": "64", "k": "3", "dof": "61", "H0": "67", "Om": "0.31", "Os0": "", "zt": "", "wt": ""},
        {"model": "RLL_joint", "chi2": "89", "AIC": "101", "AICc": "100", "BIC": "109",
         "N": "64", "k": "6", "dof": "58", "H0": "67.2", "Om": "0.31", "Os0": "0.06", "zt": "1.2", "wt": "0.4"},
    ]
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    assert result.claim_status == "CLAIM_BLOCKED"
    assert any("CPL" in r or "baseline" in r.lower() for r in result.blocking_reasons)


# ---------------------------------------------------------------------------
# N-k-dof consistency (from PR #423)
# ---------------------------------------------------------------------------


def test_dof_mismatch_is_flagged_and_blocks_claim(tmp_path: Path) -> None:
    """A row where N-k != dof should receive a local flag and block the claim."""
    rows = _base_rows()
    rows[2]["dof"] = "55"  # CPL row: should be 59
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    assert result.claim_status == "CLAIM_BLOCKED"
    flagged = [ms for ms in result.model_scans if ms.dof_consistent is False]
    assert flagged, "Expected at least one row with dof_consistent=False"
    assert any("N-k-dof" in flag for ms in flagged for flag in ms.local_flags)


# ---------------------------------------------------------------------------
# Output structure — best-model names (from PR #423)
# ---------------------------------------------------------------------------


def test_scan_best_by_aicc_and_bic_are_correct(tmp_path: Path) -> None:
    """best_by_AICc and best_by_BIC identify the model with the lowest respective values."""
    rows = _base_rows()
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    # CPL has AICc=101 (lowest) and BIC=110 (lowest) in _base_rows
    assert result.best_by_AICc == "CPL_w0waCDM_joint"
    assert result.best_by_BIC == "CPL_w0waCDM_joint"


def test_scan_models_present_field(tmp_path: Path) -> None:
    """models_present lists all four model classes when all are in the CSV."""
    rows = _base_rows()
    result = scan(_make_csv(tmp_path, rows), _make_registry(tmp_path))

    assert set(result.models_present) == {"LCDM", "wCDM", "CPL", "RLL"}
