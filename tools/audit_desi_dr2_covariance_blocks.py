#!/usr/bin/env python3
"""Audit repository-declared DESI DR2 BAO covariance blocks.

This tool materializes the block-diagonal covariance represented by the
repository's primary-point and covariance-summary CSV files. It verifies every
2x2 block, demonstrates that off-diagonal terms affect a deterministic
one-sigma diagnostic, and emits an auditable artifact. It does not run a
cosmological fit or claim that a full official joint covariance was ingested.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAIM_BOUNDARY = (
    "Repository-declared DESI DR2 covariance blocks and deterministic diagnostics "
    "only; no synthetic diagnostic is a physical fit, no full joint covariance is "
    "claimed, and no model superiority claim is allowed."
)


class CovarianceAuditError(RuntimeError):
    """Raised when covariance inputs or block invariants are inconsistent."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise CovarianceAuditError(f"required CSV not found: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise CovarianceAuditError(f"CSV has no data rows: {path}")
    return rows


def _float(row: dict[str, str], key: str, context: str) -> float:
    try:
        value = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise CovarianceAuditError(f"{context}: invalid numeric field {key!r}") from exc
    if not math.isfinite(value):
        raise CovarianceAuditError(f"{context}: non-finite field {key!r}")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _close(a: float, b: float, *, atol: float = 1e-9) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=atol)


def _invert_2x2(var_a: float, covariance: float, var_b: float) -> tuple[float, float, float, float]:
    determinant = var_a * var_b - covariance * covariance
    if determinant <= 0.0:
        raise CovarianceAuditError(
            f"covariance block is not positive definite: determinant={determinant}"
        )
    return (
        var_b / determinant,
        -covariance / determinant,
        -covariance / determinant,
        var_a / determinant,
    )


def _quadratic_2x2(residual_a: float, residual_b: float, inverse: tuple[float, float, float, float]) -> float:
    i00, i01, i10, i11 = inverse
    return (
        residual_a * (i00 * residual_a + i01 * residual_b)
        + residual_b * (i10 * residual_a + i11 * residual_b)
    )


def build_audit(primary_path: Path, summary_path: Path, output: Path) -> dict[str, Any]:
    primary_path = primary_path.resolve()
    summary_path = summary_path.resolve()
    output.mkdir(parents=True, exist_ok=True)

    primary_rows = _read_csv(primary_path)
    summary_rows = _read_csv(summary_path)

    selected_rows = [
        row
        for row in primary_rows
        if str(row.get("primary_likelihood", "")).strip().lower() == "true"
    ]
    if len(selected_rows) != len(primary_rows):
        raise CovarianceAuditError(
            "all rows in the canonical primary-points input must declare primary_likelihood=true"
        )

    index_by_block: dict[str, list[int]] = {}
    for index, row in enumerate(selected_rows):
        block = str(row.get("covariance_block", "")).strip()
        if not block:
            raise CovarianceAuditError(f"primary row {index}: covariance_block is empty")
        sigma = _float(row, "sigma", f"primary row {index}")
        if sigma <= 0.0:
            raise CovarianceAuditError(f"primary row {index}: sigma must be positive")
        index_by_block.setdefault(block, []).append(index)

    summary_by_block: dict[str, dict[str, str]] = {}
    for row in summary_rows:
        block = str(row.get("covariance_block", "")).strip()
        if not block:
            raise CovarianceAuditError("summary row has empty covariance_block")
        if block in summary_by_block:
            raise CovarianceAuditError(f"duplicate summary block: {block}")
        summary_by_block[block] = row

    size = len(selected_rows)
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    block_reports: list[dict[str, Any]] = []
    paired_blocks = 0
    isotropic_blocks = 0

    for block, indices in sorted(index_by_block.items()):
        if len(indices) == 1:
            index = indices[0]
            sigma = _float(selected_rows[index], "sigma", f"primary block {block}")
            matrix[index][index] = sigma * sigma
            isotropic_blocks += 1
            block_reports.append(
                {
                    "covariance_block": block,
                    "kind": "isotropic_diagonal",
                    "indices": [index],
                    "determinant": sigma * sigma,
                    "positive_definite": True,
                    "diagnostic_chi2_diagonal": 1.0,
                    "diagnostic_chi2_full": 1.0,
                    "off_diagonal_effect": 0.0,
                }
            )
            continue

        if len(indices) != 2:
            raise CovarianceAuditError(
                f"block {block} maps to {len(indices)} primary rows; expected 1 or 2"
            )
        if block not in summary_by_block:
            raise CovarianceAuditError(f"paired block missing from covariance summary: {block}")

        index_a, index_b = indices
        row_a = selected_rows[index_a]
        row_b = selected_rows[index_b]
        summary = summary_by_block[block]
        observable_a = str(summary.get("observable_a", "")).strip()
        observable_b = str(summary.get("observable_b", "")).strip()
        primary_observables = {str(row_a.get("observable", "")), str(row_b.get("observable", ""))}
        if primary_observables != {observable_a, observable_b}:
            raise CovarianceAuditError(
                f"block {block}: summary observables do not match primary rows"
            )

        primary_by_observable = {
            str(row_a["observable"]): (index_a, row_a),
            str(row_b["observable"]): (index_b, row_b),
        }
        index_a, row_a = primary_by_observable[observable_a]
        index_b, row_b = primary_by_observable[observable_b]

        sigma_a = _float(row_a, "sigma", f"primary block {block}/{observable_a}")
        sigma_b = _float(row_b, "sigma", f"primary block {block}/{observable_b}")
        summary_sigma_a = _float(summary, "sigma_a", f"summary block {block}")
        summary_sigma_b = _float(summary, "sigma_b", f"summary block {block}")
        rho = _float(summary, "correlation_coefficient", f"summary block {block}")
        covariance = _float(summary, "covariance", f"summary block {block}")

        if not -1.0 < rho < 1.0:
            raise CovarianceAuditError(f"block {block}: correlation must lie inside (-1, 1)")
        if not _close(sigma_a, summary_sigma_a) or not _close(sigma_b, summary_sigma_b):
            raise CovarianceAuditError(f"block {block}: summary sigma differs from primary input")
        expected_covariance = rho * sigma_a * sigma_b
        if not _close(covariance, expected_covariance):
            raise CovarianceAuditError(
                f"block {block}: covariance={covariance} but rho*sigma_a*sigma_b={expected_covariance}"
            )

        var_a = sigma_a * sigma_a
        var_b = sigma_b * sigma_b
        inverse = _invert_2x2(var_a, covariance, var_b)
        determinant = var_a * var_b - covariance * covariance
        matrix[index_a][index_a] = var_a
        matrix[index_b][index_b] = var_b
        matrix[index_a][index_b] = covariance
        matrix[index_b][index_a] = covariance

        # Deliberately synthetic diagnostic: one sigma in the same direction.
        # It demonstrates operator use only and is never interpreted as a fit.
        chi2_diagonal = (sigma_a / sigma_a) ** 2 + (sigma_b / sigma_b) ** 2
        chi2_full = _quadratic_2x2(sigma_a, sigma_b, inverse)
        effect = chi2_full - chi2_diagonal
        if _close(effect, 0.0, atol=1e-12):
            raise CovarianceAuditError(
                f"block {block}: off-diagonal covariance had no diagnostic effect"
            )

        paired_blocks += 1
        block_reports.append(
            {
                "covariance_block": block,
                "kind": "anisotropic_2x2",
                "indices": [index_a, index_b],
                "observables": [observable_a, observable_b],
                "sigma_a": sigma_a,
                "sigma_b": sigma_b,
                "correlation_coefficient": rho,
                "covariance": covariance,
                "determinant": determinant,
                "positive_definite": True,
                "diagnostic_residual": [sigma_a, sigma_b],
                "diagnostic_chi2_diagonal": chi2_diagonal,
                "diagnostic_chi2_full": chi2_full,
                "off_diagonal_effect": effect,
            }
        )

    orphan_summary = sorted(set(summary_by_block) - set(index_by_block))
    if orphan_summary:
        raise CovarianceAuditError(
            f"covariance summary contains blocks absent from primary points: {orphan_summary}"
        )

    matrix_path = output / "DESI_DR2_BAO_BLOCK_COVARIANCE.csv"
    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["row"] + [f"obs_{index:02d}" for index in range(size)])
        for index, row in enumerate(matrix):
            writer.writerow([f"obs_{index:02d}"] + [f"{value:.15g}" for value in row])

    order_path = output / "OBSERVABLE_ORDER.csv"
    with order_path.open("w", encoding="utf-8", newline="") as handle:
        columns = [
            "index",
            "release",
            "tracer",
            "z_eff",
            "observable",
            "value",
            "sigma",
            "covariance_block",
            "source_table",
            "source_url",
        ]
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for index, row in enumerate(selected_rows):
            writer.writerow({"index": index, **{key: row.get(key, "") for key in columns[1:]}})

    report_payload = {
        "schema": "rll.desi_dr2_covariance_blocks.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_primary_points": str(primary_path),
        "input_covariance_summary": str(summary_path),
        "input_sha256": {
            "primary_points": _sha256_file(primary_path),
            "covariance_summary": _sha256_file(summary_path),
        },
        "observable_count": size,
        "paired_2x2_blocks": paired_blocks,
        "isotropic_diagonal_blocks": isotropic_blocks,
        "block_diagonal_matrix_materialized": True,
        "full_cross_block_covariance_materialized": False,
        "scientific_fit_executed": False,
        "diagnostic_residual_is_synthetic": True,
        "claim_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "blocks": block_reports,
    }
    _write_json(output / "COVARIANCE_AUDIT.json", report_payload)

    markdown = [
        "# DESI DR2 BAO Covariance Block Audit",
        "",
        f"- observables: `{size}`",
        f"- anisotropic 2x2 blocks: `{paired_blocks}`",
        f"- isotropic diagonal blocks: `{isotropic_blocks}`",
        "- full cross-block covariance: `TOKEN_VAZIO`",
        "- scientific fit executed: `false`",
        "- `claim_allowed=false`",
        "",
        "## Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## F_ok",
        "",
        "- repository-declared paired covariances reconstructed",
        "- sigma and rho consistency checked against primary points",
        "- every 2x2 block proved positive definite",
        "- deterministic diagnostic proved off-diagonal use",
        "- block-diagonal 13x13 matrix emitted with explicit observable order",
        "",
        "## F_gap",
        "",
        "- full official cross-block covariance matrix",
        "- model predictions for DV/DM/DH in one vector likelihood",
        "- fit-level comparison against the diagonal approximation",
        "- independent source verification and review",
        "",
        "## F_next",
        "",
        "Integrate this block matrix into an isolated DESI vector-likelihood adapter, keeping the existing cosmological fit unchanged until regression and source-verification gates pass.",
        "",
    ]
    (output / "REPORT.md").write_text("\n".join(markdown), encoding="utf-8")

    manifest = {
        "schema": "rll.desi_dr2_covariance_artifact_manifest.v1",
        "claim_allowed": False,
        "files": [],
    }
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name not in {"MANIFEST.json", "CHECKSUMS.sha256"}:
            manifest["files"].append(
                {
                    "path": path.name,
                    "sha256": _sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    _write_json(output / "MANIFEST.json", manifest)
    checksum_lines = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "CHECKSUMS.sha256":
            checksum_lines.append(f"{_sha256_file(path)}  {path.name}")
    (output / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )
    return report_payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--primary",
        default="data/real/cosmology/desi_dr2_bao_primary_points.csv",
    )
    parser.add_argument(
        "--summary",
        default="data/real/cosmology/desi_dr2_bao_covariance_summary.csv",
    )
    parser.add_argument("--output", default="artifacts/desi-dr2-covariance-blocks")
    args = parser.parse_args()
    try:
        payload = build_audit(Path(args.primary), Path(args.summary), Path(args.output))
    except CovarianceAuditError as exc:
        print(f"COVARIANCE_AUDIT_ERROR: {exc}")
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
