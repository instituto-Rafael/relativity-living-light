from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = ROOT / "tools" / "scan_rll_model_evidence.py"
_spec = importlib.util.spec_from_file_location("scan_rll_model_evidence_restored", SCANNER_PATH)
assert _spec and _spec.loader
scanner = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("scan_rll_model_evidence_restored", scanner)
_spec.loader.exec_module(scanner)


def write_csv(path: Path, rows: list[dict[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_registry(path: Path) -> Path:
    path.write_text(json.dumps({"schema": "rll.parameter_origin_registry.v2"}), encoding="utf-8")
    return path


def rows(h0=(67.0, 67.5, 68.0, 67.2)) -> list[dict[str, str]]:
    return [
        {"model": "LCDM_joint", "chi2": "100", "AIC": "106", "AICc": "106.5", "BIC": "112", "N": "64", "k": "3", "dof": "61", "H0": str(h0[0]), "Om": "0.31", "Os0": "", "zt": "", "wt": ""},
        {"model": "wCDM_joint", "chi2": "99", "AIC": "107", "AICc": "107.5", "BIC": "115", "N": "64", "k": "4", "dof": "60", "H0": str(h0[1]), "Om": "0.31", "Os0": "", "zt": "", "wt": ""},
        {"model": "CPL_w0waCDM_joint", "chi2": "90", "AIC": "100", "AICc": "101", "BIC": "110", "N": "64", "k": "5", "dof": "59", "H0": str(h0[2]), "Om": "0.30", "Os0": "", "zt": "", "wt": ""},
        {"model": "RLL_joint", "chi2": "95", "AIC": "107", "AICc": "108", "BIC": "118", "N": "64", "k": "6", "dof": "58", "H0": str(h0[3]), "Om": "0.31", "Os0": "0.05", "zt": "1.2", "wt": "0.4"},
    ]


def run(tmp_path: Path, data: list[dict[str, str]]):
    return scanner.scan(write_csv(tmp_path / "rows.csv", data), write_registry(tmp_path / "registry.json"))


def test_h0_all_equal_warning_references_ablation_matrix(tmp_path: Path) -> None:
    result = run(tmp_path, rows((60.0, 60.0, 60.0, 60.0)))
    assert result.H0_all_equal is True
    assert any("h0_rd_ablation_matrix" in warning for warning in result.warnings)


def test_h0_not_all_equal_emits_no_equal_warning(tmp_path: Path) -> None:
    result = run(tmp_path, rows())
    assert result.H0_all_equal is False
    assert not any("H0_all_equal" in warning or "H0 is identical" in warning for warning in result.warnings)


def test_missing_rll_blocks_claim(tmp_path: Path) -> None:
    result = run(tmp_path, [row for row in rows() if "RLL" not in row["model"]])
    assert result.claim_status == "CLAIM_BLOCKED"
    assert any("RLL" in reason for reason in result.blocking_reasons)


def test_missing_cpl_blocks_claim(tmp_path: Path) -> None:
    result = run(tmp_path, [row for row in rows() if "CPL" not in row["model"]])
    assert result.claim_status == "CLAIM_BLOCKED"
    assert any("CPL" in reason or "baseline" in reason.lower() for reason in result.blocking_reasons)


def test_dof_mismatch_is_local_flag_and_claim_blocker(tmp_path: Path) -> None:
    data = rows()
    data[2]["dof"] = "55"
    result = run(tmp_path, data)
    assert result.claim_status == "CLAIM_BLOCKED"
    flagged = [row for row in result.model_scans if row.dof_consistent is False]
    assert flagged
    assert any("N-k-dof" in flag for row in flagged for flag in row.local_flags)
    assert any("inconsistent N-k-dof" in reason for reason in result.blocking_reasons)


def test_best_models_are_selected_by_minimum_aicc_and_bic(tmp_path: Path) -> None:
    result = run(tmp_path, rows())
    assert result.best_by_AICc == "CPL_w0waCDM_joint"
    assert result.best_by_BIC == "CPL_w0waCDM_joint"


def test_models_present_records_all_four_required_classes(tmp_path: Path) -> None:
    result = run(tmp_path, rows())
    assert set(result.models_present) == {"LCDM", "wCDM", "CPL", "RLL"}
    assert result.missing_required_model_classes == []
