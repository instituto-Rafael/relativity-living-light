import csv
import json
import subprocess
from pathlib import Path

import pytest

from tools.audit_desi_dr2_covariance_blocks import (
    CovarianceAuditError,
    build_audit,
)


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _inputs(tmp_path: Path, *, wrong_covariance: bool = False) -> tuple[Path, Path]:
    primary = tmp_path / "primary.csv"
    summary = tmp_path / "summary.csv"
    primary_columns = [
        "release",
        "tracer",
        "z_eff",
        "observable",
        "value",
        "sigma",
        "covariance_block",
        "paired_observable",
        "correlation_coefficient",
        "primary_likelihood",
        "source_table",
        "source_url",
        "notes",
    ]
    _write_csv(
        primary,
        primary_columns,
        [
            {
                "release": "test",
                "tracer": "BGS",
                "z_eff": 0.3,
                "observable": "DV_over_rd",
                "value": 8.0,
                "sigma": 0.1,
                "covariance_block": "BGS_DV",
                "paired_observable": "",
                "correlation_coefficient": "",
                "primary_likelihood": "true",
                "source_table": "table",
                "source_url": "https://example.invalid",
                "notes": "isotropic",
            },
            {
                "release": "test",
                "tracer": "LRG",
                "z_eff": 0.5,
                "observable": "DM_over_rd",
                "value": 14.0,
                "sigma": 0.2,
                "covariance_block": "LRG_DM_DH",
                "paired_observable": "DH_over_rd",
                "correlation_coefficient": -0.5,
                "primary_likelihood": "true",
                "source_table": "table",
                "source_url": "https://example.invalid",
                "notes": "paired a",
            },
            {
                "release": "test",
                "tracer": "LRG",
                "z_eff": 0.5,
                "observable": "DH_over_rd",
                "value": 22.0,
                "sigma": 0.4,
                "covariance_block": "LRG_DM_DH",
                "paired_observable": "DM_over_rd",
                "correlation_coefficient": -0.5,
                "primary_likelihood": "true",
                "source_table": "table",
                "source_url": "https://example.invalid",
                "notes": "paired b",
            },
        ],
    )
    covariance = -0.04 if not wrong_covariance else -0.03
    _write_csv(
        summary,
        [
            "covariance_block",
            "tracer",
            "z_eff",
            "observable_a",
            "sigma_a",
            "observable_b",
            "sigma_b",
            "correlation_coefficient",
            "covariance",
        ],
        [
            {
                "covariance_block": "LRG_DM_DH",
                "tracer": "LRG",
                "z_eff": 0.5,
                "observable_a": "DM_over_rd",
                "sigma_a": 0.2,
                "observable_b": "DH_over_rd",
                "sigma_b": 0.4,
                "correlation_coefficient": -0.5,
                "covariance": covariance,
            }
        ],
    )
    return primary, summary


def test_builds_block_matrix_and_uses_off_diagonal(tmp_path: Path) -> None:
    primary, summary = _inputs(tmp_path)
    output = tmp_path / "artifact"

    payload = build_audit(primary, summary, output)

    assert payload["observable_count"] == 3
    assert payload["paired_2x2_blocks"] == 1
    assert payload["isotropic_diagonal_blocks"] == 1
    assert payload["block_diagonal_matrix_materialized"] is True
    assert payload["full_cross_block_covariance_materialized"] is False
    assert payload["scientific_fit_executed"] is False
    assert payload["claim_allowed"] is False

    paired = next(block for block in payload["blocks"] if block["kind"] == "anisotropic_2x2")
    assert paired["positive_definite"] is True
    assert paired["diagnostic_chi2_diagonal"] == pytest.approx(2.0)
    assert paired["diagnostic_chi2_full"] != pytest.approx(2.0)
    assert paired["off_diagonal_effect"] != pytest.approx(0.0)

    receipt = json.loads((output / "COVARIANCE_AUDIT.json").read_text(encoding="utf-8"))
    assert receipt["diagnostic_residual_is_synthetic"] is True
    subprocess.check_call(["sha256sum", "-c", "CHECKSUMS.sha256"], cwd=output)


def test_rejects_covariance_inconsistent_with_rho_and_sigmas(tmp_path: Path) -> None:
    primary, summary = _inputs(tmp_path, wrong_covariance=True)
    with pytest.raises(CovarianceAuditError, match="rho\\*sigma_a\\*sigma_b"):
        build_audit(primary, summary, tmp_path / "bad")
