#!/usr/bin/env python3
"""CI-verifiable scientific skills for RLL.

This module deliberately separates three claim levels:
- VERIFIED_METHOD: deterministic numerical checks pass;
- EVIDENCED_ON_REPOSITORY_DATA: a repository data/result file was actually read;
- TOKEN_VAZIO: required evidence is absent, so no conclusion is fabricated.

It does not claim discovery, proof of a Millennium Problem, or physical validation of RLL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

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


def robust_anomaly_scores(values: Iterable[float]) -> np.ndarray:
    """Return median/MAD robust z scores.

    CRC values are identifiers/integrity checks, not physical observables.  Anomaly
    detection therefore operates on explicit numeric columns and records the column.
    """
    x = np.asarray(list(values), dtype=float)
    if x.ndim != 1 or x.size < 3:
        raise ValueError("anomaly scoring requires at least three scalar observations")
    if not np.all(np.isfinite(x)):
        raise ValueError("anomaly scoring received non-finite values")
    median = float(np.median(x))
    mad = float(np.median(np.abs(x - median)))
    if mad == 0.0:
        std = float(np.std(x))
        if std == 0.0:
            return np.zeros_like(x)
        return (x - float(np.mean(x))) / std
    return 0.6744897501960817 * (x - median) / mad


def choose_numeric_column(frame: pd.DataFrame) -> str:
    preferred = [
        "value",
        "H",
        "H_obs",
        "measurement",
        "observable_value",
        "DV_over_rs",
        "chi2",
    ]
    numeric = list(frame.select_dtypes(include=[np.number]).columns)
    for name in preferred:
        if name in numeric:
            return name
    if not numeric:
        raise ValueError("no numeric column available for anomaly diagnostics")
    return numeric[0]


def anomaly_diagnostic(csv_path: Path, threshold: float = 3.5) -> dict:
    frame = pd.read_csv(csv_path)
    column = choose_numeric_column(frame)
    values = frame[column].to_numpy(dtype=float)
    scores = robust_anomaly_scores(values)
    indices = np.flatnonzero(np.abs(scores) >= threshold).astype(int).tolist()
    return {
        "status": "EVIDENCED_ON_REPOSITORY_DATA",
        "method": "median_absolute_deviation_robust_z",
        "input": str(csv_path),
        "input_sha256": sha256_file(csv_path),
        "column": column,
        "n": int(values.size),
        "threshold_abs_z": float(threshold),
        "anomaly_count": len(indices),
        "anomaly_indices": indices,
        "max_abs_score": float(np.max(np.abs(scores))),
        "claim": "Rows are diagnostic outliers under this estimator, not discoveries.",
    }


def fourier_torus_diagnostic(samples: int = 2048, max_mode: int = 32) -> dict:
    """Deterministic T^1 Fourier recovery test, the auditable base for T^d work."""
    if samples < 8 * max_mode:
        raise ValueError("samples must be at least eight times max_mode")
    theta = np.arange(samples, dtype=float) / samples
    signal = 1.25 + 0.70 * np.cos(2 * np.pi * 3 * theta) - 0.40 * np.sin(
        2 * np.pi * 5 * theta
    )
    coeff = np.fft.rfft(signal) / samples
    reconstructed = np.full(samples, coeff[0].real)
    upper = min(max_mode, coeff.size - 1)
    for k in range(1, upper + 1):
        reconstructed += 2.0 * np.real(coeff[k] * np.exp(2j * np.pi * k * theta))
    rmse = float(np.sqrt(np.mean((signal - reconstructed) ** 2)))
    tail_energy = float(np.sum(np.abs(coeff[6:]) ** 2))
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

    log(B_10) ~= -0.5 * (BIC_1 - BIC_0).  This is explicitly not nested sampling.
    """
    frame = pd.read_csv(comparison_csv)
    required = {"model", "BIC"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"comparison file missing columns: {missing}")
    if frame.shape[0] < 2:
        raise ValueError("comparison file requires at least two model rows")
    rows = frame.dropna(subset=["BIC"]).sort_values("BIC").reset_index(drop=True)
    if rows.shape[0] < 2:
        raise ValueError("comparison file requires two finite BIC values")
    preferred = rows.iloc[0]
    alternative = rows.iloc[1]
    delta_bic = float(alternative["BIC"] - preferred["BIC"])
    log_bayes_proxy_preferred_vs_alternative = 0.5 * delta_bic
    return {
        "status": "EVIDENCED_ON_REPOSITORY_DATA",
        "method": "BIC_Laplace_proxy",
        "input": str(comparison_csv),
        "input_sha256": sha256_file(comparison_csv),
        "preferred_by_bic": str(preferred["model"]),
        "alternative": str(alternative["model"]),
        "delta_bic_alternative_minus_preferred": delta_bic,
        "log_bayes_proxy_preferred_vs_alternative": log_bayes_proxy_preferred_vs_alternative,
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
