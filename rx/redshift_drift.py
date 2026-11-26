"""Bounded FLRW redshift-drift diagnostic (not a likelihood or detection).

Loeb (1998), arXiv:astro-ph/9802122, eq. 3; Alves et al. (2019),
doi:10.1093/mnras/stz1934. Observer proper time, comoving sources,
first-order time increment; peculiar acceleration and calibration excluded.
Uses the existing producer H(z); does not change the cosmological model.
"""
from __future__ import annotations

import math

from . import cosmology

MPC_KM = 3.0856775814913673e19
JULIAN_YEAR_S = 365.25 * 86400.0
MAX_Z = 10.0
MAX_YEARS = 100.0


def _finite(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name}: boolean is not a physical scalar")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name}: invalid scalar") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name}: nonfinite scalar")
    return result


def _bounded(value, lo, hi, name):
    result = _finite(value, name)
    if not lo <= result <= hi:
        raise ValueError(f"{name}: outside diagnostic domain [{lo}, {hi}]")
    return result


def _validated_vector(model, vector):
    if model not in cosmology.BOUNDS:
        raise ValueError("unknown model")
    try:
        raw = tuple(vector)
    except TypeError as exc:
        raise ValueError("invalid parameter vector") from exc
    names = cosmology.PARAM_NAMES[model]
    if len(raw) != len(names):
        raise ValueError("parameter vector length mismatch")
    values = tuple(_bounded(v, lo, hi, name)
                   for v, (lo, hi), name in zip(raw, cosmology.BOUNDS[model], names))
    if cosmology.omega_lambda(model, values) <= 0.0:
        raise ValueError("nonpositive dark-energy density")
    return values


def drift_rate_per_second(model, z, vector):
    """dz/dt_obs in s^-1, for 0 <= z <= 10 and producer prior bounds."""
    z = _bounded(z, 0.0, MAX_Z, "z")
    values = _validated_vector(model, vector)
    h0 = values[0]
    hz = cosmology.hubble(model, z, values)
    if not math.isfinite(hz) or hz <= 0.0:
        raise ValueError("invalid producer H(z)")
    if z == 0.0:
        if not math.isclose(hz, h0, rel_tol=1e-14, abs_tol=0.0):
            raise ValueError("producer violates H(0)=H0")
        return 0.0
    # Split (1+z)*H0 to reduce avoidable rounding in the subtraction.
    return math.fsum((h0, h0 * z, -hz)) / MPC_KM


def velocity_drift_cm_s(model, z, vector, years):
    """First-order spectroscopic velocity shift in cm/s; 0 <= years <= 100."""
    z = _bounded(z, 0.0, MAX_Z, "z")
    years = _bounded(years, 0.0, MAX_YEARS, "observer years")
    rate = drift_rate_per_second(model, z, vector)
    return cosmology.C_KMS * 1e5 * rate * (years * JULIAN_YEAR_S) / (1.0 + z)
