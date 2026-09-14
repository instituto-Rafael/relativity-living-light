from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

model_comparison_fixture = {
    "n_obs": 10,
    "k_rll": 5,
    "k_lcdm": 2,
    "chi2_rll": 12.0,
    "chi2_lcdm": 13.0,
    "AIC_rll": 22.0,
    "AIC_lcdm": 17.0,
    "BIC_rll": 24.0,
    "BIC_lcdm": 18.0,
    "delta_chi2_rll_minus_lcdm": -1.0,
    "delta_aic_rll_minus_lcdm": 5.0,
    "delta_bic_rll_minus_lcdm": 6.0,
    "interpretation_label": "lcdm_preferred",
    "claim_boundary": "No superiority claim unless real-data metrics pass predefined thresholds.",
    "models": {
        "rll": {"chi2": 12.0, "aic": 22.0, "bic": 24.0},
        "lcdm": {"chi2": 13.0, "aic": 17.0, "bic": 18.0},
    },
}


def test_build_real_validation_report_generates_outputs(tmp_path: Path) -> None:
    input_json = tmp_path / "model_comparison.json"
    input_json.write_text(json.dumps(model_comparison_fixture), encoding="utf-8")

    out_json = tmp_path / "real_validation_report.json"
    out_table = tmp_path / "model_comparison_table.md"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_real_validation_report.py",
            "--input-json",
            str(input_json),
            "--out-json",
            str(out_json),
            "--out-table",
            str(out_table),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["rll"]["chi2"] == 12.0
    assert payload["lcdm"]["n_params"] == 2
    assert payload["claim_boundary"] == "No superiority claim unless real-data metrics pass predefined thresholds."
    assert "| RLL |" in out_table.read_text(encoding="utf-8")


def test_report_includes_evidence_scan_token_vazio_when_no_scan(tmp_path: Path) -> None:
    """When no evidence scan JSON exists the report embeds TOKEN_VAZIO claim_status."""
    input_json = tmp_path / "model_comparison.json"
    input_json.write_text(json.dumps(model_comparison_fixture), encoding="utf-8")

    out_json = tmp_path / "real_validation_report.json"
    out_table = tmp_path / "model_comparison_table.md"
    missing_scan = tmp_path / "nonexistent_scan.json"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_real_validation_report.py",
            "--input-json",
            str(input_json),
            "--out-json",
            str(out_json),
            "--out-table",
            str(out_table),
            "--evidence-scan-json",
            str(missing_scan),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert "evidence_scan" in payload
    assert payload["evidence_scan"]["claim_status"] == "TOKEN_VAZIO"
    table = out_table.read_text(encoding="utf-8")
    assert "## Evidence Scan" in table
    assert "claim_status:" in table


def test_report_wires_evidence_scan_when_available(tmp_path: Path) -> None:
    """When a scan JSON is provided the report embeds its claim_status and key deltas."""
    input_json = tmp_path / "model_comparison.json"
    input_json.write_text(json.dumps(model_comparison_fixture), encoding="utf-8")

    scan_json = tmp_path / "rll_model_evidence_scan.json"
    scan_json.write_text(
        json.dumps(
            {
                "claim_status": "CLAIM_BLOCKED",
                "claim_summary": "CPL preferred; H0 at boundary.",
                "best_by_AICc": "CPL_w0waCDM_joint_real",
                "best_by_BIC": "CPL_w0waCDM_joint_real",
                "H0_all_equal": True,
                "blocking_reasons": ["H0_all_equal"],
                "warnings": ["Os0_collapsed_to_zero"],
                "model_scans": [
                    {
                        "model": "RLL",
                        "delta_AICc_CPL": 33.0,
                        "delta_BIC_CPL": 35.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    out_json = tmp_path / "real_validation_report.json"
    out_table = tmp_path / "model_comparison_table.md"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_real_validation_report.py",
            "--input-json",
            str(input_json),
            "--out-json",
            str(out_json),
            "--out-table",
            str(out_table),
            "--evidence-scan-json",
            str(scan_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    ev = payload["evidence_scan"]
    assert ev["claim_status"] == "CLAIM_BLOCKED"
    assert ev["best_by_AICc"] == "CPL_w0waCDM_joint_real"
    assert ev["H0_all_equal"] is True
    assert ev["delta_AICc_rll_minus_cpl"] == 33.0
    table = out_table.read_text(encoding="utf-8")
    assert "CLAIM_BLOCKED" in table
    assert "## Evidence Scan" in table
