#!/usr/bin/env python3
"""CI-verifiable scientific skills for RLL.

Stdlib-only deterministic diagnostics. This module deliberately separates:
- VERIFIED_METHOD: deterministic numerical checks pass;
- EVIDENCED_ON_REPOSITORY_DATA: a repository data/result file was actually read;
- TOKEN_VAZIO: required evidence is absent, so no conclusion is fabricated.

It does not claim discovery, proof of a Millennium Problem, or physical validation of RLL.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Iterable

SCHEMA = "rll.ci_scientific_skills.v1"
CLAIM_BOUNDARY = (
    "Numerical method checks and repository-data diagnostics only; "
    "no physical superiority, discovery, or theorem-proof claim."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def robust_anomaly_scores(values: Iterable[float]) -> list[float]:
    """Return median/MAD robust z scores with NumPy-compatible fallback semantics."""
    x = [float(value) for value in values]
    if len(x) < 3:
        raise ValueError("anomaly scoring requires at least three scalar observations")
    if not all(math.isfinite(value) for value in x):
        raise ValueError("anomaly scoring received non-finite values")

    median = float(statistics.median(x))
    absolute = [abs(value - median) for value in x]
    mad = float(statistics.median(absolute))
    if mad == 0.0:
        std = float(statistics.pstdev(x))
        if std == 0.0:
            return [0.0 for _ in x]
        mean = float(statistics.fmean(x))
        return [(value - mean) / std for value in x]
    return [0.6744897501960817 * (value - median) / mad for value in x]


def _read_csv_records(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV without header: {path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"CSV without rows: {path}")
    return [str(name) for name in reader.fieldnames], rows


def _numeric_columns(fieldnames: list[str], rows: list[dict[str, str]]) -> tuple[list[str], dict[str, list[float]]]:
    columns: list[str] = []
    parsed: dict[str, list[float]] = {}
    for name in fieldnames:
        values: list[float] = []
        valid = True
        for row in rows:
            raw = row.get(name)
            if raw is None or str(raw).strip() == "":
                continue
            try:
                value = float(raw)
            except (TypeError, ValueError):
                valid = False
                break
            if not math.isfinite(value):
                valid = False
                break
            values.append(value)
        if valid and values:
            columns.append(name)
            parsed[name] = values
    return columns, parsed


def choose_numeric_column(fieldnames: list[str], rows: list[dict[str, str]]) -> tuple[str, list[float]]:
    preferred = [
        "value",
        "H",
        "H_obs",
        "measurement",
        "observable_value",
        "DV_over_rs",
        "chi2",
    ]
    numeric, parsed = _numeric_columns(fieldnames, rows)
    for name in preferred:
        if name in numeric:
            return name, parsed[name]
    if not numeric:
        raise ValueError("no numeric column available for anomaly diagnostics")
    return numeric[0], parsed[numeric[0]]


def anomaly_diagnostic(csv_path: Path, threshold: float = 3.5) -> dict:
    fieldnames, rows = _read_csv_records(csv_path)
    column, values = choose_numeric_column(fieldnames, rows)
    scores = robust_anomaly_scores(values)
    indices = [index for index, score in enumerate(scores) if abs(score) >= threshold]
    return {
        "status": "EVIDENCED_ON_REPOSITORY_DATA",
        "method": "median_absolute_deviation_robust_z",
        "input": str(csv_path),
        "input_sha256": sha256_file(csv_path),
        "column": column,
        "n": len(values),
        "threshold_abs_z": float(threshold),
        "anomaly_count": len(indices),
        "anomaly_indices": indices,
        "max_abs_score": max(abs(score) for score in scores),
        "claim": "Rows are diagnostic outliers under this estimator, not discoveries.",
    }


def _rfft_coefficients(signal: list[float]) -> list[complex]:
    """Dependency-free real DFT with the same 1/N coefficient normalization used previously."""
    n = len(signal)
    result: list[complex] = []
    for k in range(n // 2 + 1):
        angle = -2.0 * math.pi * k / n
        wr = math.cos(angle)
        wi = math.sin(angle)
        pr = 1.0
        pi = 0.0
        sr = 0.0
        si = 0.0
        for value in signal:
            sr += value * pr
            si += value * pi
            pr, pi = pr * wr - pi * wi, pr * wi + pi * wr
        result.append(complex(sr / n, si / n))
    return result


def fourier_torus_diagnostic(samples: int = 2048, max_mode: int = 32) -> dict:
    """Deterministic T^1 Fourier recovery test, the auditable base for T^d work."""
    if samples < 8 * max_mode:
        raise ValueError("samples must be at least eight times max_mode")
    theta = [index / samples for index in range(samples)]
    signal = [
        1.25
        + 0.70 * math.cos(2.0 * math.pi * 3.0 * value)
        - 0.40 * math.sin(2.0 * math.pi * 5.0 * value)
        for value in theta
    ]
    coeff = _rfft_coefficients(signal)
    upper = min(max_mode, len(coeff) - 1)
    reconstructed: list[float] = []
    for value in theta:
        estimate = coeff[0].real
        for k in range(1, upper + 1):
            phase = complex(
                math.cos(2.0 * math.pi * k * value),
                math.sin(2.0 * math.pi * k * value),
            )
            estimate += 2.0 * (coeff[k] * phase).real
        reconstructed.append(estimate)

    rmse = math.sqrt(
        sum((observed - predicted) ** 2 for observed, predicted in zip(signal, reconstructed))
        / samples
    )
    tail_energy = sum(abs(value) ** 2 for value in coeff[6:])
    pass_condition = rmse < 1e-12 and tail_energy < 1e-24
    return {
        "status": "VERIFIED_METHOD" if pass_condition else "CONTRADICTION",
        "space": "T^1",
        "extension_boundary": "T^7 requires explicit multidimensional data and tests.",
        "samples": samples,
        "max_mode": max_mode,
        "rmse": rmse,
        "tail_energy_after_mode_5": tail_energy,
        "expected_nonzero_modes": [0, 3, 5],
        "claim": "Deterministic Fourier implementation check; not a new convergence theorem.",
    }


def bayes_proxy_diagnostic(comparison_csv: Path) -> dict:
    """Read BIC results and report a Laplace/BIC log-Bayes proxy.

    log(B_10) ~= -0.5 * (BIC_1 - BIC_0). This is explicitly not nested sampling.
    """
    fieldnames, rows = _read_csv_records(comparison_csv)
    missing = sorted({"model", "BIC"} - set(fieldnames))
    if missing:
        raise ValueError(f"comparison file missing columns: {missing}")

    finite_rows = []
    for row in rows:
        raw = row.get("BIC")
        if raw is None or str(raw).strip() == "":
            continue
        try:
            bic = float(raw)
        except ValueError:
            continue
        if math.isfinite(bic):
            finite_rows.append((bic, str(row.get("model", ""))))
    if len(finite_rows) < 2:
        raise ValueError("comparison file requires two finite BIC values")
    finite_rows.sort(key=lambda item: item[0])
    preferred_bic, preferred_model = finite_rows[0]
    alternative_bic, alternative_model = finite_rows[1]
    delta_bic = alternative_bic - preferred_bic
    return {
        "status": "EVIDENCED_ON_REPOSITORY_DATA",
        "method": "BIC_Laplace_proxy",
        "input": str(comparison_csv),
        "input_sha256": sha256_file(comparison_csv),
        "preferred_by_bic": preferred_model,
        "alternative": alternative_model,
        "delta_bic_alternative_minus_preferred": delta_bic,
        "log_bayes_proxy_preferred_vs_alternative": 0.5 * delta_bic,
        "claim": "Approximation from BIC; not a nested-sampling evidence calculation.",
    }


def token_vazio(skill: str, expected: list[str]) -> dict:
    return {
        "status": "TOKEN_VAZIO",
        "skill": skill,
        "expected_inputs": expected,
        "claim": "No conclusion produced because required repository evidence is absent.",
    }


def first_existing(paths: Iterable[Path]) -> Path | None:
    return next((path for path in paths if path.is_file()), None)


def run(root: Path, output: Path, strict: bool = False) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    anomaly_candidates = [
        root / "data/real/cosmology_observational_seed_2026.csv",
        root / "data/real/cosmology/cosmology_observational_seed_2026.csv",
    ]
    comparison_candidates = [
        root / "results/structure_d/model_comparison_real.csv",
        root / "data/results/model_comparison.csv",
    ]

    anomaly_path = first_existing(anomaly_candidates)
    comparison_path = first_existing(comparison_candidates)

    payload = {
        "schema": SCHEMA,
        "claim_boundary": CLAIM_BOUNDARY,
        "skills": {
            "C1_anomaly_diagnostic": (
                anomaly_diagnostic(anomaly_path)
                if anomaly_path
                else token_vazio("C1_anomaly_diagnostic", [str(p) for p in anomaly_candidates])
            ),
            "B4_fourier_torus": fourier_torus_diagnostic(),
            "D1_bayes_proxy": (
                bayes_proxy_diagnostic(comparison_path)
                if comparison_path
                else token_vazio("D1_bayes_proxy", [str(p) for p in comparison_candidates])
            ),
        },
    }

    payload["overall_status"] = (
        "CONTRADICTION"
        if any(item["status"] == "CONTRADICTION" for item in payload["skills"].values())
        else "TOKEN_VAZIO"
        if any(item["status"] == "TOKEN_VAZIO" for item in payload["skills"].values())
        else "VERIFIED_METHODS_AND_REPOSITORY_DIAGNOSTICS"
    )
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if strict and payload["overall_status"] in {"TOKEN_VAZIO", "CONTRADICTION"}:
        raise SystemExit(2)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/ci-scientific-skills/report.json"),
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    payload = run(args.root.resolve(), args.output, strict=args.strict)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
