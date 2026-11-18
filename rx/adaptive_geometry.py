"""Fail-closed adaptive geometry diagnostics for RLL.

This module derives geometry features from already-defined observables/states.
It does not add a cosmological parameter, modify a likelihood, or select a
physical mechanism. Standard-library only.
"""
from __future__ import annotations
import math

EPS = 1e-15


def _norm3(v):
    return math.hypot(*(float(x) for x in v))


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
    if not (math.isfinite(ratio) and ratio > 0.0 and
            math.isfinite(product) and product > 0.0):
        raise ValueError("BAO ratio/product cannot be represented as finite positive floats")
    # Use separate input logarithms to avoid needless loss of precision.
    log_x, log_y = math.log(x), math.log(y)
    log_scale = 0.5 * (log_x + log_y)
    anisotropy = log_x - log_y
    try:
        x_reconstructed = math.exp(log_scale + 0.5 * anisotropy)
        y_reconstructed = math.exp(log_scale - 0.5 * anisotropy)
    except OverflowError as exc:
        raise ValueError("BAO reconstruction exceeds finite range") from exc
    q = min(ratio, 1.0 / ratio)
    ecc = math.sqrt(max(0.0, 1.0 - q * q))
    rho = math.hypot(x, y)
    phi = math.atan2(x, y)
    a_tri = 0.5 * product
    a_ellipse = math.pi * product
    # Fail closed rather than silently exporting infinite/zeroed geometry proxies.
    phi_identity = phi - math.atan(ratio)
    area_identity = a_ellipse - 2.0 * math.pi * a_tri
    radial_identity = rho * rho - product * (ratio + 1.0 / ratio)
    derived = (x_reconstructed, y_reconstructed, q, ecc, rho, phi,
               a_tri, a_ellipse, phi_identity, area_identity, radial_identity)
    if not all(math.isfinite(v) for v in derived) or not (
            x_reconstructed > 0.0 and y_reconstructed > 0.0 and q > 0.0):
        raise ValueError("BAO derived geometry cannot be represented as finite floats")
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
            "phi_equals_atan_F_AP": phi_identity,
            "ellipse_area_minus_2pi_triangle_area": area_identity,
            "rho2_minus_product_times_ratio_plus_inverse": radial_identity,
        },
        "claim_allowed": False,
    }



def _scaled_covariance_2d(sigma_xx, sigma_xy, sigma_yy, positive_definite=False):
    """Scale-independent PSD/PD gate for a 2D symmetric covariance.

    Validity must not depend on a fixed absolute epsilon with physical units.
    This routine does not infer geometry or change an observational likelihood.
    """
    sxx, sxy, syy = (float(sigma_xx), float(sigma_xy), float(sigma_yy))
    if not all(math.isfinite(v) for v in (sxx, sxy, syy)):
        raise ValueError("covariance values must be finite")
    scale = max(abs(sxx), abs(sxy), abs(syy))
    if scale == 0.0:
        if positive_definite:
            raise ValueError("covariance must be positive definite")
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    a, b, c = sxx / scale, sxy / scale, syy / scale
    det = a * c - b * b
    if a < 0.0 or c < 0.0 or det < 0.0:
        raise ValueError("covariance must be positive semidefinite")
    if positive_definite and (a <= 0.0 or c <= 0.0 or det <= 0.0):
        raise ValueError("covariance must be positive definite")
    return scale, a, b, c, det


def covariance_ellipse_2d(sigma_xx, sigma_xy, sigma_yy):
    """Principal-axis diagnostics for a symmetric 2x2 covariance matrix."""
    scale, a, b, c, det_normalized = _scaled_covariance_2d(
        sigma_xx, sigma_xy, sigma_yy)
    if scale == 0.0:
        lmax = lmin = 0.0
    else:
        lmax_normalized = 0.5 * (a + c) + math.hypot(0.5 * (a - c), b)
        lmin_normalized = det_normalized / lmax_normalized if lmax_normalized else 0.0
        lmax = scale * lmax_normalized
        lmin = scale * lmin_normalized
    major, minor = math.sqrt(lmax), math.sqrt(lmin)
    q = minor / major if major else 0.0
    ecc = math.sqrt(max(0.0, 1.0 - q * q))
    angle = 0.5 * math.atan2(2.0 * b, a - c)
    cond = math.inf if lmin == 0.0 else lmax / lmin
    area = math.pi * major * minor
    det = (scale * scale) * det_normalized
    if not all(math.isfinite(v) for v in (lmax, lmin, major, minor, area, det)):
        raise ValueError("covariance diagnostics exceed finite range; rescale inputs")
    return {
        "lambda_major": lmax,
        "lambda_minor": lmin,
        "axis_major_1sigma": major,
        "axis_minor_1sigma": minor,
        "axis_ratio_q": q,
        "eccentricity": ecc,
        "orientation_rad": angle,
        "area_1sigma": area,
        "determinant": det,
        "condition_number": cond,
        "claim_allowed": False,
    }


def mahalanobis2_2d(dx, dy, sigma_xx, sigma_xy, sigma_yy):
    """Squared Mahalanobis residual for a positive-definite 2x2 covariance."""
    dx, dy = float(dx), float(dy)
    if not math.isfinite(dx) or not math.isfinite(dy):
        raise ValueError("residual values must be finite")
    scale, a, b, c, det = _scaled_covariance_2d(
        sigma_xx, sigma_xy, sigma_yy, positive_definite=True)
    divisor = math.sqrt(scale)
    x, y = dx / divisor, dy / divisor
    result = (c * x * x - 2.0 * b * x * y + a * y * y) / det
    if not math.isfinite(result) or result < 0.0:
        raise ValueError("Mahalanobis residual is not finite and nonnegative")
    return result


def local_curve_invariants_3d(velocity, acceleration, jerk=None):
    """Euclidean/local-orthonormal curve diagnostics.

    Allowed directly for G0/G1. For G2/G3, inputs must first be expressed in
    a declared local orthonormal frame or replaced by a metric-specific adapter.
    """
    v = tuple(map(float, velocity))
    a = tuple(map(float, acceleration))
    if len(v) != 3 or len(a) != 3:
        raise ValueError("velocity and acceleration must be 3-vectors")
    if not all(math.isfinite(x) for x in (*v, *a)):
        raise ValueError("velocity and acceleration must be finite")
    speed = _norm3(v)
    if not math.isfinite(speed):
        raise ValueError("speed must remain finite; rescale input units")
    if speed <= EPS:
        return {"state": "TOKEN_VAZIO_ZERO_SPEED", "speed": speed, "curvature": None, "torsion": None, "claim_allowed": False}
    cross_va = _cross3(v, a)
    cross_norm = _norm3(cross_va)
    if not math.isfinite(cross_norm):
        raise ValueError("cross-product magnitude not finite; rescale inputs")
    try:
        curvature = cross_norm / (speed ** 3)
        tangential_accel = _dot3(v, a) / speed
        normal_accel = cross_norm / speed
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("curve diagnostics not representable; rescale inputs") from exc
    if not all(math.isfinite(x) for x in
               (curvature, tangential_accel, normal_accel)):
        raise ValueError("curve diagnostics not finite; rescale inputs")
    torsion = None
    torsion_state = "TOKEN_VAZIO_JERK_NOT_SUPPLIED"
    if jerk is not None:
        j = tuple(map(float, jerk))
        if len(j) != 3:
            raise ValueError("jerk must be a 3-vector")
        if not all(math.isfinite(x) for x in j):
            raise ValueError("jerk must be finite")
        denom = cross_norm * cross_norm
        if not math.isfinite(denom):
            raise ValueError("torsion denominator overflow; rescale inputs")
        if denom <= EPS:
            torsion_state = "TOKEN_VAZIO_ZERO_CURVATURE"
        else:
            torsion = _dot3(cross_va, j) / denom
            if not math.isfinite(torsion):
                raise ValueError("torsion is not finite; rescale inputs")
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
