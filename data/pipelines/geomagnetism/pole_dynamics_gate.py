"""Bounded geomagnetic pole-dynamics and secular-variation research adapter.

This module turns recent geomagnetic literature into deterministic, falsifiable
operators without promoting numerical coincidence into physical identity.

Implemented boundaries
----------------------
* A magnetic dip pole is treated locally as a zero of the horizontal field
  h=(B_theta, B_phi). Its motion can be obtained by implicit differentiation.
* Source/lobe sensitivity is a local derivative, not a statement that a chosen
  decomposition is uniquely physical.
* Frozen-flux residuals test an advection-only approximation; non-zero residual
  may include diffusion, model error, unresolved sources, or discretization.
* Wave-number/phase-speed conversion is a kinematic identity only.
* The RAFAELIA sqrt(3)/2 ratio is exposed only as a fixed, pre-registered
  comparison gate. It is never fitted to data in this module.
* No RLL cosmological claim is created by a geomagnetic fit.

claim_allowed = False
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from typing import Iterable, Sequence

TAU = 2.0 * math.pi
SQRT3_OVER_2 = math.sqrt(3.0) / 2.0
PHI_GOLDEN = (1.0 + math.sqrt(5.0)) / 2.0

Vector2 = tuple[float, float]
Matrix2 = tuple[tuple[float, float], tuple[float, float]]
Hessian2 = tuple[tuple[float, float], tuple[float, float]]


def _finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _positive(value: float, name: str) -> None:
    _finite(value, name)
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def solve_2x2(matrix: Matrix2, rhs: Vector2, det_tolerance: float = 1.0e-14) -> Vector2:
    """Solve a 2x2 linear system, failing closed near singularity."""
    (a, b), (c, d) = matrix
    e, f = rhs
    for name, value in (
        ("a", a), ("b", b), ("c", c), ("d", d), ("e", e), ("f", f)
    ):
        _finite(value, name)
    _positive(det_tolerance, "det_tolerance")
    det = a * d - b * c
    if abs(det) <= det_tolerance:
        raise ValueError("local horizontal-field Jacobian is singular or ill-conditioned")
    return ((e * d - b * f) / det, (a * f - e * c) / det)


def implicit_zero_velocity(horizontal_jacobian: Matrix2, horizontal_time_derivative: Vector2) -> Vector2:
    r"""Velocity of a moving zero h(p(t),t)=0.

    J_h p_dot + h_t = 0, therefore p_dot = -J_h^{-1} h_t.

    Coordinates must be a locally regular chart with consistent units.
    """
    return solve_2x2(
        horizontal_jacobian,
        (-horizontal_time_derivative[0], -horizontal_time_derivative[1]),
    )


def implicit_zero_acceleration(
    horizontal_jacobian: Matrix2,
    horizontal_second_time_derivative: Vector2,
    horizontal_space_time_derivatives: tuple[Vector2, Vector2],
    horizontal_spatial_hessians: tuple[Hessian2, Hessian2],
    zero_velocity: Vector2,
) -> Vector2:
    r"""Second derivative of a moving zero.

    For each component h_i,
      J_h p_ddot = -(h_tt + 2 h_xt p_dot + p_dot^T H_i p_dot).

    This is a local kinematic identity; it does not identify the physical cause
    of the field evolution.
    """
    vx, vy = zero_velocity
    rhs: list[float] = []
    for component in range(2):
        ftt = horizontal_second_time_derivative[component]
        fxt = horizontal_space_time_derivatives[component]
        hessian = horizontal_spatial_hessians[component]
        cross = 2.0 * (fxt[0] * vx + fxt[1] * vy)
        quadratic = (
            hessian[0][0] * vx * vx
            + (hessian[0][1] + hessian[1][0]) * vx * vy
            + hessian[1][1] * vy * vy
        )
        rhs.append(-(ftt + cross + quadratic))
    return solve_2x2(horizontal_jacobian, (rhs[0], rhs[1]))


def source_amplitude_sensitivity(horizontal_jacobian: Matrix2, source_horizontal_field: Vector2) -> Vector2:
    r"""Sensitivity of the zero position to one additive source amplitude.

    If h(p, alpha)=h_rest(p)+alpha*h_source(p)=0, then
      dp/dalpha = -J_h^{-1} h_source.

    This is suitable for bounded Canada/Siberia lobe experiments only when the
    source decomposition itself is explicitly provided and source-traced.
    """
    return solve_2x2(
        horizontal_jacobian,
        (-source_horizontal_field[0], -source_horizontal_field[1]),
    )


def frozen_flux_residual(
    radial_field_time_derivative: float,
    horizontal_flow_dot_grad_radial_field: float,
    radial_field: float,
    horizontal_flow_divergence: float,
) -> float:
    r"""Residual of dB_r/dt + div_H(u_H B_r)=0.

    The caller supplies metric-correct horizontal derivatives. Expanded:
      residual = B_r,t + u_H.grad_H(B_r) + B_r div_H(u_H).
    """
    values = (
        radial_field_time_derivative,
        horizontal_flow_dot_grad_radial_field,
        radial_field,
        horizontal_flow_divergence,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("frozen-flux inputs must be finite")
    return (
        radial_field_time_derivative
        + horizontal_flow_dot_grad_radial_field
        + radial_field * horizontal_flow_divergence
    )


def phase_passage_period_years(
    radius_km: float,
    azimuthal_wavenumber: int,
    phase_speed_km_per_year: float,
) -> float:
    r"""Convert azimuthal mode number and phase speed to crest-passage period.

    lambda_m = 2*pi*R/m
    T_m      = lambda_m/v = 2*pi*R/(m*v)
    """
    _positive(radius_km, "radius_km")
    _positive(phase_speed_km_per_year, "phase_speed_km_per_year")
    if not isinstance(azimuthal_wavenumber, int) or azimuthal_wavenumber < 1:
        raise ValueError("azimuthal_wavenumber must be an integer >= 1")
    return TAU * radius_km / (azimuthal_wavenumber * phase_speed_km_per_year)


def fit_zero_mean_sinusoid(
    times_year: Sequence[float],
    values: Sequence[float],
    period_year: float,
) -> dict[str, float]:
    r"""Linear least-squares fit y=A sin(wt)+B cos(wt) for fixed period.

    Mirrors the bounded two-column sinusoidal inversion used in recent IGRF-14
    flow-acceleration forecasting literature. It deliberately has no offset.
    """
    _positive(period_year, "period_year")
    if len(times_year) != len(values) or len(values) < 3:
        raise ValueError("times and values must have equal length >= 3")
    if not all(math.isfinite(x) for x in times_year) or not all(math.isfinite(y) for y in values):
        raise ValueError("times and values must be finite")

    omega = TAU / period_year
    ss = cc = sc = sy = cy = 0.0
    for t, y in zip(times_year, values):
        s = math.sin(omega * t)
        c = math.cos(omega * t)
        ss += s * s
        cc += c * c
        sc += s * c
        sy += s * y
        cy += c * y

    amplitude_sin, amplitude_cos = solve_2x2(((ss, sc), (sc, cc)), (sy, cy))
    residuals = []
    for t, y in zip(times_year, values):
        pred = amplitude_sin * math.sin(omega * t) + amplitude_cos * math.cos(omega * t)
        residuals.append(y - pred)
    mse = sum(r * r for r in residuals) / len(residuals)
    return {
        "period_year": period_year,
        "amplitude_sin": amplitude_sin,
        "amplitude_cos": amplitude_cos,
        "amplitude": math.hypot(amplitude_sin, amplitude_cos),
        "phase_rad": math.atan2(amplitude_cos, amplitude_sin),
        "mse": mse,
        "rmse": math.sqrt(mse),
    }


def scan_zero_mean_sinusoid_periods(
    times_year: Sequence[float],
    values: Sequence[float],
    period_min_year: float = 1.0,
    period_max_year: float = 20.0,
    period_step_year: float = 0.1,
) -> dict[str, object]:
    """Deterministically scan a predeclared period range and return minimum MSE."""
    _positive(period_min_year, "period_min_year")
    _positive(period_max_year, "period_max_year")
    _positive(period_step_year, "period_step_year")
    if period_max_year < period_min_year:
        raise ValueError("period_max_year must be >= period_min_year")

    count = int(round((period_max_year - period_min_year) / period_step_year))
    fits = [
        fit_zero_mean_sinusoid(times_year, values, period_min_year + i * period_step_year)
        for i in range(count + 1)
    ]
    best = min(fits, key=lambda item: (float(item["mse"]), float(item["period_year"])))
    return {
        "best": best,
        "period_min_year": period_min_year,
        "period_max_year": period_max_year,
        "period_step_year": period_step_year,
        "candidate_count": len(fits),
    }


def fixed_ratio_log_rms(values: Iterable[float], fixed_ratio: float = SQRT3_OVER_2) -> float:
    r"""Pre-registered fixed-ratio gate; no ratio is fitted.

    For positive x_n, return RMS[log(x_{n+1}/x_n)-log(q)]. A perfect geometric
    sequence with ratio q gives zero. Use only for a scalar observable defined
    before looking at the result (e.g. predeclared step length or curvature
    radius series); otherwise the test is post-hoc and invalid.
    """
    _positive(fixed_ratio, "fixed_ratio")
    seq = list(values)
    if len(seq) < 2:
        raise ValueError("at least two values are required")
    if not all(math.isfinite(x) and x > 0.0 for x in seq):
        raise ValueError("ratio-test values must be positive and finite")
    target = math.log(fixed_ratio)
    residuals = [math.log(b / a) - target for a, b in zip(seq, seq[1:])]
    return math.sqrt(sum(r * r for r in residuals) / len(residuals))


def great_circle_distance_km(
    lat1_deg: float,
    lon1_deg: float,
    lat2_deg: float,
    lon2_deg: float,
    radius_km: float = 6371.0088,
) -> float:
    _positive(radius_km, "radius_km")
    for name, value in (
        ("lat1_deg", lat1_deg), ("lon1_deg", lon1_deg),
        ("lat2_deg", lat2_deg), ("lon2_deg", lon2_deg),
    ):
        _finite(value, name)
    phi1, phi2 = math.radians(lat1_deg), math.radians(lat2_deg)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2_deg - lon1_deg)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    a = min(1.0, max(0.0, a))
    return 2.0 * radius_km * math.asin(math.sqrt(a))


def initial_bearing_rad(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float) -> float:
    phi1, phi2 = math.radians(lat1_deg), math.radians(lat2_deg)
    dlambda = math.radians(lon2_deg - lon1_deg)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    if abs(x) < 1.0e-15 and abs(y) < 1.0e-15:
        raise ValueError("bearing undefined for coincident or antipodal-degenerate points")
    return math.atan2(y, x)


def wrapped_angle_rad(angle: float) -> float:
    _finite(angle, "angle")
    return math.atan2(math.sin(angle), math.cos(angle))


def three_point_turning_angle_rad(
    prev_lat_deg: float,
    prev_lon_deg: float,
    lat_deg: float,
    lon_deg: float,
    next_lat_deg: float,
    next_lon_deg: float,
) -> float:
    """Signed change in forward bearing at the middle point."""
    bearing_in = initial_bearing_rad(prev_lat_deg, prev_lon_deg, lat_deg, lon_deg)
    bearing_out = initial_bearing_rad(lat_deg, lon_deg, next_lat_deg, next_lon_deg)
    return wrapped_angle_rad(bearing_out - bearing_in)


@dataclass(frozen=True)
class BaselineResult:
    phase_period_year: float
    phase_wavelength_km: float
    phase_angular_speed_rad_per_year: float
    implicit_velocity: Vector2
    implicit_acceleration: Vector2
    canada_sensitivity_example: Vector2
    siberia_sensitivity_example: Vector2
    frozen_flux_residual: float
    recovered_sinusoid_period_year: float
    sqrt3_ratio_rms: float
    claim_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["cross_paper_consistency"] = {
            "CHAOS8_reported_example": "m=13, eastward phase speed about 200 km/yr at CMB equator after 2012",
            "derived_crest_passage_period_year": self.phase_period_year,
            "Madsen_2026_reported_distribution": "Swarm toroidal flow-acceleration periods peak around 8-9 years",
            "interpretation": "numerical consistency only; not proof that both analyses isolate the same physical mode",
        }
        payload["boundaries"] = {
            "magnetic_pole_equals_material_object": False,
            "canada_siberia_decomposition_uniquely_identified_here": False,
            "frozen_flux_exact_physics": False,
            "sqrt3_over_2_detected_in_geomagnetic_data": False,
            "phi_detected_in_geomagnetic_data": False,
            "RLL_cosmology_supported_by_geomagnetism": False,
            "claim_allowed": False,
        }
        return payload


def baseline() -> dict[str, object]:
    # Cross-paper kinematic derivation: CHAOS-8 example m=13, v~200 km/yr.
    r_cmb_km = 3485.0
    m = 13
    phase_speed = 200.0
    period = phase_passage_period_years(r_cmb_km, m, phase_speed)
    wavelength = TAU * r_cmb_km / m
    angular_speed = phase_speed / r_cmb_km

    # Synthetic analytic moving zero h=(x-3t, y-0.4 t^2), evaluated at t=2.
    jacobian: Matrix2 = ((1.0, 0.0), (0.0, 1.0))
    velocity = implicit_zero_velocity(jacobian, (-3.0, -1.6))
    acceleration = implicit_zero_acceleration(
        jacobian,
        (0.0, -0.8),
        ((0.0, 0.0), (0.0, 0.0)),
        (((0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0))),
        velocity,
    )

    # Synthetic lobe sensitivities only; real source fields remain dataset-gated.
    canada_sensitivity = source_amplitude_sensitivity(jacobian, (2.0, -1.0))
    siberia_sensitivity = source_amplitude_sensitivity(jacobian, (-0.5, 1.5))

    # Exact synthetic frozen-flux closure.
    ff_residual = frozen_flux_residual(
        radial_field_time_derivative=-7.0,
        horizontal_flow_dot_grad_radial_field=3.0,
        radial_field=2.0,
        horizontal_flow_divergence=2.0,
    )

    # Synthetic recovery of an 8.4-year zero-mean acceleration signal.
    synthetic_times = [0.25 * i for i in range(49)]
    true_period = 8.4
    synthetic_values = [
        1.7 * math.sin(TAU * t / true_period) - 0.4 * math.cos(TAU * t / true_period)
        for t in synthetic_times
    ]
    sinusoid_scan = scan_zero_mean_sinusoid_periods(synthetic_times, synthetic_values)

    ratio_values = [1.0 * (SQRT3_OVER_2 ** i) for i in range(8)]
    ratio_rms = fixed_ratio_log_rms(ratio_values)

    result = BaselineResult(
        phase_period_year=period,
        phase_wavelength_km=wavelength,
        phase_angular_speed_rad_per_year=angular_speed,
        implicit_velocity=velocity,
        implicit_acceleration=acceleration,
        canada_sensitivity_example=canada_sensitivity,
        siberia_sensitivity_example=siberia_sensitivity,
        frozen_flux_residual=ff_residual,
        recovered_sinusoid_period_year=float(sinusoid_scan["best"]["period_year"]),
        sqrt3_ratio_rms=ratio_rms,
    )
    return {
        "schema": "rll.geomagnetism.pole_dynamics.baseline.v1",
        "epistemic_state": "SYNTHETIC_AND_LITERATURE_DERIVED_ONLY",
        "result": result.to_dict(),
        "real_data_gates": {
            "WMM2025_coefficients_bound": "TOKEN_VAZIO",
            "IGRF14_coefficients_bound": "TOKEN_VAZIO",
            "CHAOS8_coefficients_bound": "TOKEN_VAZIO",
            "north_dip_pole_time_series_checksum_verified": "TOKEN_VAZIO",
            "canada_siberia_lobe_decomposition_bound": "TOKEN_VAZIO",
            "real_sqrt3_ratio_test": "TOKEN_VAZIO",
            "real_phi_test": "TOKEN_VAZIO",
            "claim_allowed": False,
        },
        "F_ok": [
            "implicit zero velocity and acceleration operators implemented",
            "source-amplitude sensitivity operator implemented",
            "frozen-flux residual implemented",
            "azimuthal wavenumber/speed to passage-period identity implemented",
            "zero-mean sinusoid scan implemented",
            "pre-registered sqrt(3)/2 comparison gate implemented without fitting q",
        ],
        "F_gap": [
            "no official coefficient dataset is committed or checksum-bound by this baseline",
            "no real Canada/Siberia lobe source decomposition has been evaluated",
            "no RAFAELIA constant has been detected in geomagnetic observations",
        ],
        "F_next": "bind one official WMM2025/IGRF-14/CHAOS-8 coefficient source with checksum and evaluate the pole path and fixed pre-registered diagnostics without post-hoc tuning",
    }


if __name__ == "__main__":
    print(json.dumps(baseline(), indent=2, sort_keys=True))
