"""Fail-closed adaptive geometry diagnostics for RLL.

This module derives geometry features from already-defined observables/states.
It does not add a cosmological parameter, modify a likelihood, or select a
physical mechanism. Standard-library only.
"""
from __future__ import annotations
import math

EPS = 1e-15


def _norm3(v):
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _cross3(a, b):
    ax, ay, az = map(float, a)
    bx, by, bz = map(float, b)
    return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)


def _dot3(a, b):
    return sum(float(x) * float(y) for x, y in zip(a, b))


def bao_observable_geometry(dm_over_rd, dh_over_rd):
    """Invertible diagnostic coordinates for positive BAO transverse/radial observables.

    x = D_M/r_d, y = D_H/r_d.
    Independent two-coordinate core:
      log_scale = 1/2 log(xy)
      anisotropy = log(x/y) = log(F_AP)
    All ellipse/triangle/polar proxies below are deterministic functions of x,y.
    """
    x = float(dm_over_rd)
    y = float(dh_over_rd)
    if not (math.isfinite(x) and math.isfinite(y) and x > 0.0 and y > 0.0):
        raise ValueError("DM/rd and DH/rd must be finite and positive")
    ratio = x / y
    product = x * y
    log_scale = 0.5 * math.log(product)
    anisotropy = math.log(ratio)
    x_reconstructed = math.exp(log_scale + 0.5 * anisotropy)
    y_reconstructed = math.exp(log_scale - 0.5 * anisotropy)
    q = min(ratio, 1.0 / ratio)
    ecc = math.sqrt(max(0.0, 1.0 - q * q))
    rho = math.hypot(x, y)
    phi = math.atan2(x, y)
    a_tri = 0.5 * product
    a_ellipse = math.pi * product
    return {
        "DM_over_rd": x,
        "DH_over_rd": y,
        "F_AP": ratio,
        "product_scale": product,
        "log_scale": log_scale,
        "anisotropy_log_ratio": anisotropy,
        "rho": rho,
        "phi_rad": phi,
        "axis_ratio_q": q,
        "ellipse_eccentricity_proxy": ecc,
        "right_triangle_area_proxy": a_tri,
        "ellipse_area_proxy": a_ellipse,
        "reconstruction": {"DM_over_rd": x_reconstructed, "DH_over_rd": y_reconstructed},
        "redundancy_identities": {
            "phi_equals_atan_F_AP": phi - math.atan(ratio),
            "ellipse_area_minus_2pi_triangle_area": a_ellipse - 2.0 * math.pi * a_tri,
            "rho2_minus_product_times_ratio_plus_inverse": rho * rho - product * (ratio + 1.0 / ratio),
        },
        "claim_allowed": False,
    }


def covariance_ellipse_2d(sigma_xx, sigma_xy, sigma_yy):
    """Principal-axis diagnostics for a symmetric 2x2 covariance matrix."""
    sxx = float(sigma_xx)
    sxy = float(sigma_xy)
    syy = float(sigma_yy)
    if not all(math.isfinite(v) for v in (sxx, sxy, syy)):
        raise ValueError("covariance values must be finite")
    det = sxx * syy - sxy * sxy
    if sxx < -EPS or syy < -EPS or det < -EPS:
        raise ValueError("covariance must be positive semidefinite")
    trace = sxx + syy
    disc = math.sqrt(max(0.0, ((sxx - syy) * 0.5) ** 2 + sxy * sxy))
    lmax = max(0.0, 0.5 * trace + disc)
    lmin = max(0.0, 0.5 * trace - disc)
    major = math.sqrt(lmax)
    minor = math.sqrt(lmin)
    q = 0.0 if major <= EPS else minor / major
    ecc = math.sqrt(max(0.0, 1.0 - q * q))
    angle = 0.5 * math.atan2(2.0 * sxy, sxx - syy)
    cond = math.inf if lmin <= EPS else lmax / lmin
    return {
        "lambda_major": lmax,
        "lambda_minor": lmin,
        "axis_major_1sigma": major,
        "axis_minor_1sigma": minor,
        "axis_ratio_q": q,
        "eccentricity": ecc,
        "orientation_rad": angle,
        "area_1sigma": math.pi * major * minor,
        "determinant": max(0.0, det),
        "condition_number": cond,
        "claim_allowed": False,
    }


def mahalanobis2_2d(dx, dy, sigma_xx, sigma_xy, sigma_yy):
    """Squared Mahalanobis residual for a nonsingular 2x2 covariance."""
    dx = float(dx)
    dy = float(dy)
    sxx = float(sigma_xx)
    sxy = float(sigma_xy)
    syy = float(sigma_yy)
    det = sxx * syy - sxy * sxy
    if not math.isfinite(det) or det <= EPS:
        raise ValueError("covariance must be positive definite")
    return (syy * dx * dx - 2.0 * sxy * dx * dy + sxx * dy * dy) / det


def local_curve_invariants_3d(velocity, acceleration, jerk=None):
    """Euclidean/local-orthonormal curve diagnostics.

    Allowed directly for G0/G1. For G2/G3, inputs must first be expressed in
    a declared local orthonormal frame or replaced by a metric-specific adapter.
    """
    v = tuple(map(float, velocity))
    a = tuple(map(float, acceleration))
    if len(v) != 3 or len(a) != 3:
        raise ValueError("velocity and acceleration must be 3-vectors")
    speed = _norm3(v)
    if speed <= EPS:
        return {"state": "TOKEN_VAZIO_ZERO_SPEED", "speed": speed, "curvature": None, "torsion": None, "claim_allowed": False}
    cross_va = _cross3(v, a)
    cross_norm = _norm3(cross_va)
    curvature = cross_norm / (speed ** 3)
    tangential_accel = _dot3(v, a) / speed
    normal_accel = cross_norm / speed
    torsion = None
    torsion_state = "TOKEN_VAZIO_JERK_NOT_SUPPLIED"
    if jerk is not None:
        j = tuple(map(float, jerk))
        if len(j) != 3:
            raise ValueError("jerk must be a 3-vector")
        denom = cross_norm * cross_norm
        if denom <= EPS:
            torsion_state = "TOKEN_VAZIO_ZERO_CURVATURE"
        else:
            torsion = _dot3(cross_va, j) / denom
            torsion_state = "DEFINED"
    return {
        "state": "DEFINED",
        "speed": speed,
        "curvature": curvature,
        "tangential_acceleration": tangential_accel,
        "normal_acceleration": normal_accel,
        "torsion": torsion,
        "torsion_state": torsion_state,
        "claim_allowed": False,
    }
