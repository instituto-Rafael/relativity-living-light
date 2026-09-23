"""Zero-third-party DHA spectral baseline with explicit angular semantics.

The legacy DESI DHA route names its scan variable omega while Astropy
LombScargle.power consumes ordinary frequency (cycles per x-unit). This module
removes that ambiguity: all public spectral scan inputs are angular frequency
in radians per x-unit.

This is an authored implementation surface for deterministic engineering
reproduction. It is not an Astropy Lomb-Scargle parity claim and does not
synthesize a false-alarm probability without a separately validated contract.
"""

from __future__ import annotations

import math

from .kernel import invert_matrix


TAU = 2.0 * math.pi


def angular_frequency_to_cycles(omega):
    return float(omega) / TAU


def cycles_to_angular_frequency(frequency):
    return TAU * float(frequency)


def linspace(start, stop, count):
    n = int(count)
    if n < 2:
        raise ValueError("count must be at least 2")
    lo = float(start)
    hi = float(stop)
    step = (hi - lo) / (n - 1)
    return [lo + step * i for i in range(n)]


def _validate_vectors(x, y, sigma):
    xs = [float(v) for v in x]
    ys = [float(v) for v in y]
    ss = [float(v) for v in sigma]
    if not xs or len(xs) != len(ys) or len(xs) != len(ss):
        raise ValueError("x/y/sigma must be non-empty and have equal lengths")
    if any(not math.isfinite(v) for v in xs + ys + ss):
        raise ValueError("x/y/sigma contain non-finite values")
    if any(v <= 0.0 for v in ss):
        raise ValueError("sigma must be strictly positive")
    return xs, ys, ss


def _weighted_constant_chi2(y, sigma):
    weights = [1.0 / (s * s) for s in sigma]
    sw = sum(weights)
    mean = sum(w * value for w, value in zip(weights, y)) / sw
    return sum(w * (value - mean) ** 2 for w, value in zip(weights, y))


def _weighted_sinusoid_fit_at_omega(x, y, sigma, omega):
    """Fit c0 + c*cos(omega*x) + s*sin(omega*x) by weighted least squares."""

    w0 = float(omega)
    if not math.isfinite(w0) or w0 <= 0.0:
        raise ValueError("omega must be finite and positive")

    normal = [[0.0] * 3 for _ in range(3)]
    rhs = [0.0, 0.0, 0.0]

    for xv, yv, sv in zip(x, y, sigma):
        weight = 1.0 / (sv * sv)
        row = [1.0, math.cos(w0 * xv), math.sin(w0 * xv)]
        for i in range(3):
            rhs[i] += weight * row[i] * yv
            for j in range(3):
                normal[i][j] += weight * row[i] * row[j]

    inverse = invert_matrix(normal, eps=1.0e-24)
    beta = [
        sum(inverse[i][j] * rhs[j] for j in range(3))
        for i in range(3)
    ]
    chi2 = 0.0
    for xv, yv, sv in zip(x, y, sigma):
        model = (
            beta[0]
            + beta[1] * math.cos(w0 * xv)
            + beta[2] * math.sin(w0 * xv)
        )
        chi2 += ((yv - model) / sv) ** 2

    cosine = beta[1]
    sine = beta[2]
    amplitude = math.hypot(cosine, sine)
    phase = math.atan2(-sine, cosine)
    return {
        "offset": beta[0],
        "cosine": cosine,
        "sine": sine,
        "amplitude": amplitude,
        "phase": phase,
        "omega": w0,
        "frequency_cycles": angular_frequency_to_cycles(w0),
        "chi2": chi2,
    }


def angular_gls_periodogram(x, y, sigma, omega_grid):
    """Weighted floating-mean sinusoid scan over angular frequencies."""

    xs, ys, ss = _validate_vectors(x, y, sigma)
    grid = [float(value) for value in omega_grid]
    if not grid or any(
        (not math.isfinite(value) or value <= 0.0)
        for value in grid
    ):
        raise ValueError(
            "omega_grid must contain finite positive angular frequencies"
        )

    chi2_null = _weighted_constant_chi2(ys, ss)
    if chi2_null <= 0.0:
        raise ValueError(
            "constant/null chi2 is zero; periodogram is undefined"
        )

    rows = []
    for omega in grid:
        fit = _weighted_sinusoid_fit_at_omega(xs, ys, ss, omega)
        power = 1.0 - fit["chi2"] / chi2_null
        fit["power"] = max(0.0, min(1.0, power))
        rows.append(fit)

    best = max(rows, key=lambda item: item["power"])
    return {
        "method": "rx_weighted_angular_gls_v1",
        "frequency_semantics": "angular_radians_per_x_unit",
        "omega_grid": grid,
        "power": [row["power"] for row in rows],
        "best_omega": best["omega"],
        "best_frequency_cycles": best["frequency_cycles"],
        "best_fit": best,
        "chi2_null": chi2_null,
        "false_alarm_probability": "TOKEN_VAZIO_NOT_IMPLEMENTED",
        "astropy_semantic_parity": "TOKEN_VAZIO_NOT_CLAIMED",
        "claim_allowed": False,
    }


def scan_angular_gls(
    x,
    y,
    sigma,
    *,
    omega_min,
    omega_max,
    n_grid=2000,
):
    return angular_gls_periodogram(
        x,
        y,
        sigma,
        linspace(omega_min, omega_max, n_grid),
    )
