from __future__ import annotations

"""Three-model Pantheon+ full-covariance adapter: LCDM x CPL x RLL.

This module deliberately reuses the already audited Pantheon+ ASCII-covariance
pipeline.  It does not replace or rewrite the historical LCDM/RLL result.  CPL
is added as a fairness control under the same catalog selection, covariance,
profiled absolute-magnitude nuisance, seeds, optimizer and integration grid.
"""

import argparse
from pathlib import Path
from typing import Any, Sequence

import numpy as np

# Importing the ASCII adapter first installs the bounded covariance-roundoff
# policy into the shared core (full matrix, deterministic symmetrization, no
# jitter).  We then add only the missing CPL background model.
from . import pantheon_fit_ascii as _ascii
from . import pantheon_fit as _core

SCHEMA = "rll_pantheon_full_covariance_three_model_fit_v1"
LCDM = _core.LCDM
RLL = _core.RLL
CPL = "CPL_pantheon_full"

CPL_SPEC: dict[str, Any] = {
    "parameter_names": ("H0", "Omega_m", "w0", "wa"),
    "bounds": ((60.0, 80.0), (0.10, 0.60), (-2.0, -0.3), (-3.0, 3.0)),
    "canonical_start": (70.0, 0.30, -1.0, 0.0),
    "k_including_profiled_M_B": 5,
}

# The shared fitter dispatches parameter metadata through MODEL_SPECS.
_core.MODEL_SPECS.setdefault(CPL, CPL_SPEC)
_ORIGINAL_E2 = _core.e2


def e2(model: str, z: np.ndarray, parameters: Sequence[float]) -> np.ndarray:
    """Dimensionless E(z)^2 including a flat CPL/w0wa control model."""

    if model != CPL:
        return _ORIGINAL_E2(model, z, parameters)

    _, omega_m, w0, wa = map(float, parameters)
    z_array = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_array
    omega_de = 1.0 - omega_m - _core.OMEGA_R0
    if omega_de <= 0.0 or np.any(zp1 <= 0.0):
        return np.full_like(z_array, np.nan)
    dark_energy = zp1 ** (3.0 * (1.0 + w0 + wa)) * np.exp(
        -3.0 * wa * z_array / zp1
    )
    value = omega_m * zp1**3 + _core.OMEGA_R0 * zp1**4 + omega_de * dark_energy
    return np.asarray(value, dtype=float)


# Core distance_modulus/profiled_likelihood/fit_model resolve `e2` from their
# module globals at call time.  Patch only that dispatch point so every other
# audited numerical path is inherited unchanged.
_core.e2 = e2

prepare_data = _ascii.prepare_data
distance_modulus = _core.distance_modulus
profiled_likelihood = _core.profiled_likelihood
fit_model = _core.fit_model


def _delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, float]:
    return {
        metric: float(candidate[metric] - baseline[metric])
        for metric in ("chi2", "AIC", "AICc", "BIC")
    }


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
    """Execute LCDM, CPL and RLL on one identical Pantheon+ likelihood."""

    # Preserve all audited input/covariance diagnostics by first producing the
    # canonical two-model payload through the existing ASCII adapter.
    payload = _ascii.build_result(
        catalog_path,
        covariance_path,
        output_path,
        seeds=seeds,
        maxiter=maxiter,
        ftol=ftol,
        integration_points=integration_points,
        z_min=z_min,
    )

    data, _original_rows = _core.load_data(
        catalog_path,
        covariance_path,
        integration_points=integration_points,
        z_min=z_min,
    )
    cpl = _core.fit_model(data, CPL, seeds, maxiter=maxiter, ftol=ftol)

    lcdm_row = dict(payload["models"][LCDM]["best"])
    rll_row = dict(payload["models"][RLL]["best"])
    cpl_row = dict(cpl["best"])

    payload["schema"] = SCHEMA
    payload["rows"] = [lcdm_row, cpl_row, rll_row]
    payload["models"] = {
        LCDM: payload["models"][LCDM],
        CPL: cpl,
        RLL: payload["models"][RLL],
    }
    payload["comparison"] = {
        "baseline": LCDM,
        "controls": [CPL, RLL],
        "cpl_minus_baseline": _delta(cpl_row, lcdm_row),
        "rll_minus_baseline": _delta(rll_row, lcdm_row),
        # Compatibility alias for consumers that historically interpreted RLL
        # as the single candidate.
        "candidate_minus_baseline": _delta(rll_row, lcdm_row),
    }
    statuses = [payload["models"][name]["status"] for name in (LCDM, CPL, RLL)]
    payload["status"] = (
        "PASS_LIMITED" if all(status == "PASS" for status in statuses)
        else "TOKEN_VAZIO_CONVERGENCE"
    )
    payload["scientific_boundary"] = (
        "A common full-covariance Pantheon+SH0ES LCDM/CPL/RLL fit is a fair "
        "single-likelihood comparison; it is not Bayesian evidence, independent "
        "replication, DES-Dovekie calibration validation, or model confirmation."
    )
    payload["method"]["model_fairness"] = (
        "LCDM, CPL and RLL share catalog selection, full STAT+SYS covariance, "
        "profiled M_B nuisance, H0/Omega_m common bounds, seeds, optimizer, "
        "integration grid and flat-closure radiation convention."
    )
    payload["F_ok"].append(
        "CPL is evaluated as a mandatory modern control under the same full-covariance likelihood as LCDM and RLL."
    )
    payload["F_gap"].extend(
        [
            "DES-Dovekie calibration/covariance ablation remains TOKEN_VAZIO.",
            "AIC/AICc/BIC remain information criteria and do not replace real nested-sampling evidence.",
        ]
    )
    payload["F_next"] = [
        "Materialize the DES-Dovekie calibration variant with equivalent provenance and nuisance policy.",
        "Use this identical three-model likelihood as one component of real nested-sampling evidence.",
        "Independently reproduce hashes and fitted metrics before scientific promotion.",
    ]
    _core._atomic_json(output_path, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Full-covariance Pantheon+SH0ES LCDM/CPL/RLL fairness fit"
    )
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--covariance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="11,23,37,53,71")
    parser.add_argument("--maxiter", type=int, default=250)
    parser.add_argument("--ftol", type=float, default=1.0e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    parser.add_argument("--z-min", type=float, default=0.01)
    args = parser.parse_args(argv)
    try:
        seeds = _core.parse_seeds(args.seeds)
        if args.maxiter < 1 or args.integration_points < 64:
            raise ValueError("maxiter must be >=1 and integration-points must be >=64")
        result = build_result(
            args.catalog,
            args.covariance,
            args.output,
            seeds=seeds,
            maxiter=args.maxiter,
            ftol=args.ftol,
            integration_points=args.integration_points,
            z_min=args.z_min,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(
        f"{result['status']} rows={len(result['rows'])} "
        f"dBIC_CPL={result['comparison']['cpl_minus_baseline']['BIC']:.8g} "
        f"dBIC_RLL={result['comparison']['rll_minus_baseline']['BIC']:.8g}"
    )
    return 0 if result["status"] == "PASS_LIMITED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
