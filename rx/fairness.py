"""Rx fairness/statistics primitives for RLL.

Project-owned stdlib-only implementations of small statistical and governance
mechanics historically coupled to NumPy in the legacy fairness module.

The underlying mathematical methods are standard. This module is an
implementation replacement surface, not a claim of authorship over AIC/BIC,
covariance mathematics, S8, or cosmological growth theory.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.util import find_spec

from .cosmology import transition_f


@dataclass(frozen=True)
class CovarianceReadiness:
    ready: bool
    claim_allowed: bool
    mode: str
    reason: str
    n: int


def aic(chi2, k):
    return float(float(chi2) + 2.0 * int(k))


def bic(chi2, k, n_obs):
    n = int(n_obs)
    if n <= 0:
        raise ValueError("n_obs must be positive for BIC")
    return float(float(chi2) + int(k) * math.log(n))


def aicc(chi2, k, n_obs):
    k_int = int(k)
    n = int(n_obs)
    if n <= k_int + 1:
        raise ValueError("AICc undefined when n_obs <= k + 1")
    return float(
        aic(chi2, k_int)
        + (2.0 * k_int * (k_int + 1)) / (n - k_int - 1)
    )


def s8_parameter(sigma8, om):
    om_value = float(om)
    if om_value < 0.0:
        return float("nan")
    return float(float(sigma8) * math.sqrt(om_value / 0.3))


def _w_eff_scalar(z, zt, wt):
    z_value = float(z)
    width = max(float(wt), 1.0e-12)
    zp1 = 1.0 + z_value
    fz = transition_f(z_value, float(zt), width)
    fprime = -(fz * (1.0 - fz)) / width
    matter_like = zp1**3
    density_shape = fz + (1.0 - fz) * matter_like
    if density_shape == 0.0:
        return float("nan")
    density_prime = (
        fprime * (1.0 - matter_like)
        + 3.0 * (1.0 - fz) * zp1**2
    )
    return float(-1.0 + zp1 * density_prime / (3.0 * density_shape))


def w_eff_rll_density(z, zt, wt):
    """Density-consistent effective equation of state for the RLL sector.

    A scalar input returns a float. Lists/tuples return the same container kind.
    Vectorization stays explicit instead of restoring a hidden third-party API.
    """

    if isinstance(z, tuple):
        return tuple(_w_eff_scalar(item, zt, wt) for item in z)
    if isinstance(z, list):
        return [_w_eff_scalar(item, zt, wt) for item in z]
    return _w_eff_scalar(z, zt, wt)


def _jacobi_eigenvalues_symmetric(matrix, *, tolerance=1.0e-14, max_sweeps=80):
    """Approximate eigenvalues of a small real symmetric matrix."""

    n = len(matrix)
    if n == 0:
        return []
    a = [[float(value) for value in row] for row in matrix]
    if n == 1:
        return [a[0][0]]

    for _ in range(max(1, int(max_sweeps))):
        p = 0
        q = 1
        largest = abs(a[p][q])
        for i in range(n):
            for j in range(i + 1, n):
                candidate = abs(a[i][j])
                if candidate > largest:
                    p, q, largest = i, j, candidate

        if largest <= tolerance:
            break

        app = a[p][p]
        aqq = a[q][q]
        apq = a[p][q]
        phi = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c = math.cos(phi)
        s = math.sin(phi)

        for k in range(n):
            if k in (p, q):
                continue
            akp = a[k][p]
            akq = a[k][q]
            new_kp = c * akp - s * akq
            new_kq = s * akp + c * akq
            a[k][p] = a[p][k] = new_kp
            a[k][q] = a[q][k] = new_kq

        a[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        a[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        a[p][q] = a[q][p] = 0.0

    return [a[i][i] for i in range(n)]


def covariance_readiness(covariance, *, mode):
    """Validate covariance and preserve the provenance-aware claim gate."""

    mode_text = str(mode)
    try:
        cov = [[float(value) for value in row] for row in covariance]
    except (TypeError, ValueError):
        return CovarianceReadiness(
            False, False, mode_text, "covariance is not a numeric matrix", 0
        )

    n = len(cov)
    if n == 0 or any(len(row) != n for row in cov):
        return CovarianceReadiness(
            False, False, mode_text, "covariance is not square", 0
        )
    if any(not math.isfinite(value) for row in cov for value in row):
        return CovarianceReadiness(
            False, False, mode_text, "covariance contains non-finite values", n
        )
    for i in range(n):
        for j in range(i + 1, n):
            if abs(cov[i][j] - cov[j][i]) > 1.0e-10:
                return CovarianceReadiness(
                    False, False, mode_text, "covariance is not symmetric", n
                )
    if any(cov[i][i] <= 0.0 for i in range(n)):
        return CovarianceReadiness(
            False,
            False,
            mode_text,
            "covariance diagonal is not strictly positive",
            n,
        )

    eigenvalues = _jacobi_eigenvalues_symmetric(cov)
    if min(eigenvalues) < -1.0e-10:
        return CovarianceReadiness(
            False,
            False,
            mode_text,
            "covariance is not positive semidefinite",
            n,
        )
    if mode_text != "official_full":
        return CovarianceReadiness(
            True,
            False,
            mode_text,
            "valid covariance, but not an official full covariance",
            n,
        )
    return CovarianceReadiness(
        True, True, mode_text, "official full covariance is valid", n
    )


def growth_backend_benchmark_status(*, require_external=False):
    """Report CLASS/CAMB import availability without treating it as validation."""

    backends = {
        "classy": find_spec("classy") is not None,
        "camb": find_spec("camb") is not None,
    }
    available = [name for name, present in backends.items() if present]
    status = "available" if available else "skipped_missing_backend"
    claim_allowed = bool(available) and bool(require_external)
    result = {
        "status": status,
        "available_backends": available,
        "checked_backends": sorted(backends),
        "claim_allowed": claim_allowed,
        "reason": (
            "External CLASS/CAMB backend is importable; a numerical benchmark "
            "must still be run before strong growth claims."
            if available
            else "CLASS/CAMB is not installed; local D+/fσ8 remains an "
            "internal approximation."
        ),
    }
    if claim_allowed:
        result.update(
            {
                "source": available,
                "metric": "fsigma8_residuals",
                "baseline": ["LCDM_growth", "CPL_growth"],
                "uncertainty_or_covariance_status": (
                    "external_backend_benchmark_required"
                ),
                "claim_boundary": (
                    "Backend availability permits a benchmark run; it does not "
                    "by itself validate any cosmological model."
                ),
            }
        )
    return result


def load_parameter_origin_registry(registry):
    """Validate the minimal parameter-origin registry contract."""

    if not isinstance(registry, Mapping):
        raise ValueError("parameter registry must be an object")
    required_top = {"schema", "parameters"}
    missing_top = required_top.difference(registry)
    if missing_top:
        raise ValueError(
            "parameter registry missing keys: %s" % sorted(missing_top)
        )
    params = registry["parameters"]
    if not isinstance(params, list) or not params:
        raise ValueError(
            "parameter registry requires a non-empty parameters list"
        )
    required_param = {
        "name",
        "model",
        "origin",
        "role",
        "status",
        "reference_keys",
    }
    for idx, item in enumerate(params):
        if not isinstance(item, Mapping):
            raise ValueError("parameter entry %d is not an object" % idx)
        missing = required_param.difference(item)
        if missing:
            raise ValueError(
                "parameter entry %d missing keys: %s" % (idx, sorted(missing))
            )
    return dict(registry)
