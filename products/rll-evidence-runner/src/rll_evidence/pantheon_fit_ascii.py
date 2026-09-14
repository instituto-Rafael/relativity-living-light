from __future__ import annotations

"""Numerically bounded adapter for the official ASCII Pantheon+ covariance.

The official STAT+SYS text matrix carries decimal-serialization roundoff with
max|C-C^T|=3e-8. This module accepts only a narrowly bounded asymmetry, records
it, and applies C <- (C+C.T)/2 before the existing no-jitter Cholesky path.
"""

from pathlib import Path
from typing import Any, Sequence

import numpy as np

from . import pantheon_fit as _core

COVARIANCE_SYMMETRY_ATOL = 5.0e-8
COVARIANCE_SYMMETRY_POLICY = (
    "Accept raw ASCII roundoff only when max|C-C^T| <= 5e-8, then apply "
    "C <- (C+C.T)/2 deterministically before Cholesky; no jitter is applied."
)

LCDM = _core.LCDM
RLL = _core.RLL
e2 = _core.e2
distance_modulus = _core.distance_modulus
profiled_likelihood = _core.profiled_likelihood
fit_model = _core.fit_model

_ORIGINAL_PREPARE_DATA = _core.prepare_data
_ORIGINAL_BUILD_RESULT = _core.build_result
_LAST_DIAGNOSTICS: dict[str, Any] = {}


def _diagnostics(covariance: np.ndarray) -> dict[str, Any]:
    matrix = np.asarray(covariance, dtype=float)
    max_asymmetry = float(np.max(np.abs(matrix - matrix.T)))
    return {
        "max_asymmetry_raw": max_asymmetry,
        "absolute_tolerance": COVARIANCE_SYMMETRY_ATOL,
        "within_tolerance": max_asymmetry <= COVARIANCE_SYMMETRY_ATOL,
        "symmetrization": "C <- (C + C.T) / 2",
        "symmetrized": max_asymmetry > 0.0,
        "policy": COVARIANCE_SYMMETRY_POLICY,
    }


def _validate_and_symmetrize(
    covariance: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    matrix = np.asarray(covariance, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"covariance must be square, got shape={matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("covariance contains non-finite values")
    if np.any(np.diag(matrix) <= 0.0):
        raise ValueError("covariance diagonal must be strictly positive")
    diagnostics = _diagnostics(matrix)
    if not diagnostics["within_tolerance"]:
        raise ValueError(
            "covariance is not symmetric within canonical tolerance: "
            f"max asymmetry={diagnostics['max_asymmetry_raw']}, "
            f"atol={COVARIANCE_SYMMETRY_ATOL}"
        )
    return 0.5 * (matrix + matrix.T), diagnostics


def load_covariance(path: Path, expected_n: int) -> np.ndarray:
    tokens = np.fromfile(path, dtype=float, sep=" ")
    if tokens.size < 1:
        raise ValueError("empty covariance file")
    dimension = int(tokens[0])
    values = tokens[1:]
    if dimension != expected_n:
        raise ValueError(f"covariance dimension={dimension}, catalog rows={expected_n}")
    expected_values = dimension * dimension
    if values.size != expected_values:
        raise ValueError(f"covariance values={values.size}, expected={expected_values}")
    matrix = values.reshape((dimension, dimension))
    _, diagnostics = _validate_and_symmetrize(matrix)
    _LAST_DIAGNOSTICS.clear()
    _LAST_DIAGNOSTICS["source_full_matrix"] = diagnostics
    return matrix


def prepare_data(
    z_hd: Sequence[float],
    z_hel: Sequence[float],
    m_b_corr: Sequence[float],
    ceph_dist: Sequence[float],
    is_calibrator: Sequence[bool],
    covariance: np.ndarray,
    *,
    integration_points: int = 4096,
):
    normalized, diagnostics = _validate_and_symmetrize(covariance)
    _LAST_DIAGNOSTICS["selected_matrix"] = diagnostics
    data = _ORIGINAL_PREPARE_DATA(
        z_hd,
        z_hel,
        m_b_corr,
        ceph_dist,
        is_calibrator,
        normalized,
        integration_points=integration_points,
    )
    data.covariance_diagnostics = dict(_LAST_DIAGNOSTICS)
    return data


def build_result(
    catalog_path: Path,
    covariance_path: Path,
    output_path: Path,
    *,
    seeds: Sequence[int],
    maxiter: int = 250,
    ftol: float = 1.0e-10,
    integration_points: int = 4096,
    z_min: float = 0.01,
) -> dict[str, Any]:
    payload = _ORIGINAL_BUILD_RESULT(
        catalog_path,
        covariance_path,
        output_path,
        seeds=seeds,
        maxiter=maxiter,
        ftol=ftol,
        integration_points=integration_points,
        z_min=z_min,
    )
    payload["inputs"]["covariance"]["diagnostics"] = dict(_LAST_DIAGNOSTICS)
    payload["method"]["covariance_symmetry_policy"] = COVARIANCE_SYMMETRY_POLICY
    payload["method"]["linear_algebra"] = (
        "bounded deterministic symmetrization followed by Cholesky; "
        "no diagonal approximation; no jitter"
    )
    payload["F_ok"].append(
        "ASCII roundoff asymmetry is measured, bounded, recorded, and "
        "symmetrized deterministically before Cholesky."
    )
    _core._atomic_json(output_path, payload)
    return payload


# The original build pipeline resolves these names from its module globals.
_core.load_covariance = load_covariance
_core.prepare_data = prepare_data
_core.build_result = build_result


def main(argv: Sequence[str] | None = None) -> int:
    return _core.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
