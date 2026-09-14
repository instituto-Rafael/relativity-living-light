"""Bounded toroidal geometry and sine-reference research adapter.

The module provides deterministic geometry, phase and closure diagnostics. It is
not a plasma-confinement solver, GRMHD solver, feedback controller, or proof that
a physical source is toroidal or universally stabilized by a sine wave.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math

TAU = 2.0 * math.pi
Vector3 = tuple[float, float, float]


def _positive_finite(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")


def wrapped_phase_error_rad(reference_phase_rad: float, observed_phase_rad: float) -> float:
    if not math.isfinite(reference_phase_rad) or not math.isfinite(observed_phase_rad):
        raise ValueError("phases must be finite")
    return math.atan2(
        math.sin(observed_phase_rad - reference_phase_rad),
        math.cos(observed_phase_rad - reference_phase_rad),
    )


def torus_point_m(major_radius_m: float, minor_radius_m: float, theta_rad: float, phi_rad: float) -> Vector3:
    _positive_finite(major_radius_m, "major_radius_m")
    _positive_finite(minor_radius_m, "minor_radius_m")
    if minor_radius_m >= major_radius_m:
        raise ValueError("minor_radius_m must be less than major_radius_m")
    if not math.isfinite(theta_rad) or not math.isfinite(phi_rad):
        raise ValueError("angles must be finite")
    ring_radius = major_radius_m + minor_radius_m * math.cos(theta_rad)
    return (
        ring_radius * math.cos(phi_rad),
        ring_radius * math.sin(phi_rad),
        minor_radius_m * math.sin(theta_rad),
    )


def torus_surface_residual_m(point_m: Vector3, major_radius_m: float, minor_radius_m: float) -> float:
    x, y, z = point_m
    if not all(math.isfinite(v) for v in point_m):
        raise ValueError("point components must be finite")
    _positive_finite(major_radius_m, "major_radius_m")
    _positive_finite(minor_radius_m, "minor_radius_m")
    radial = math.hypot(x, y)
    tube_radius = math.hypot(radial - major_radius_m, z)
    return tube_radius - minor_radius_m


def distance_m(a: Vector3, b: Vector3) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def rms(values: list[float]) -> float:
    if not values:
        raise ValueError("values must be non-empty")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("values must be finite")
    return math.sqrt(sum(value * value for value in values) / len(values))


@dataclass(frozen=True)
class ToroidalSineReferenceState:
    major_radius_m: float
    minor_radius_m: float
    inner_frequency_hz: float
    outer_frequency_hz: float
    reference_frequency_hz: float
    amplitude: float
    amplitude_unit: str
    duration_s: float
    sample_count: int
    theta0_rad: float = 0.0
    phi0_rad: float = 0.0
    reference_phase_rad: float = 0.0
    observed_phase_offset_rad: float = 0.0

    def validate(self) -> None:
        for name in (
            "major_radius_m",
            "minor_radius_m",
            "inner_frequency_hz",
            "outer_frequency_hz",
            "reference_frequency_hz",
            "amplitude",
            "duration_s",
        ):
            _positive_finite(float(getattr(self, name)), name)
        if self.minor_radius_m >= self.major_radius_m:
            raise ValueError("minor_radius_m must be less than major_radius_m")
        if not isinstance(self.sample_count, int) or self.sample_count < 3:
            raise ValueError("sample_count must be an integer >= 3")
        if not isinstance(self.amplitude_unit, str) or not self.amplitude_unit.strip():
            raise ValueError("amplitude_unit must be a non-empty string")
        for name in ("theta0_rad", "phi0_rad", "reference_phase_rad", "observed_phase_offset_rad"):
            if not math.isfinite(float(getattr(self, name))):
                raise ValueError(f"{name} must be finite")


@dataclass(frozen=True)
class ToroidalSineReferenceResult:
    phase_error_rad: float
    phase_lock_score: float
    signal_rms_error: float
    signal_normalized_rms_error: float
    closure_residual_m: float
    closure_residual_normalized: float
    maximum_surface_residual_m: float
    geometric_path_metric_dimensionless: float
    sample_count: int
    cycle_closed_within_tolerance: bool
    reference_only: bool = True
    claim_allowed: bool = False

    def to_dict(self) -> dict:
        out = asdict(self)
        out["claim_boundary"] = (
            "Synthetic toroidal geometry and sine-reference diagnostics only. "
            "No universal stabilization, plasma confinement, GRMHD source fit, "
            "laboratory validation, or cosmological modification."
        )
        return out


def evaluate(state: ToroidalSineReferenceState, closure_tolerance_m: float = 1.0e-9) -> ToroidalSineReferenceResult:
    state.validate()
    if not math.isfinite(closure_tolerance_m) or closure_tolerance_m < 0:
        raise ValueError("closure_tolerance_m must be non-negative and finite")

    points: list[Vector3] = []
    errors: list[float] = []
    maximum_surface_residual = 0.0
    path_metric = 0.0
    previous: Vector3 | None = None

    for index in range(state.sample_count):
        t = state.duration_s * index / (state.sample_count - 1)
        theta = state.theta0_rad + TAU * state.inner_frequency_hz * t
        phi = state.phi0_rad + TAU * state.outer_frequency_hz * t
        point = torus_point_m(state.major_radius_m, state.minor_radius_m, theta, phi)
        points.append(point)
        maximum_surface_residual = max(
            maximum_surface_residual,
            abs(torus_surface_residual_m(point, state.major_radius_m, state.minor_radius_m)),
        )
        if previous is not None:
            step = distance_m(previous, point)
            path_metric += (step / state.major_radius_m) ** 2
        previous = point

        reference_phase = TAU * state.reference_frequency_hz * t + state.reference_phase_rad
        observed_phase = reference_phase + state.observed_phase_offset_rad
        reference_value = state.amplitude * math.sin(reference_phase)
        observed_value = state.amplitude * math.sin(observed_phase)
        errors.append(observed_value - reference_value)

    phase_error = wrapped_phase_error_rad(
        state.reference_phase_rad,
        state.reference_phase_rad + state.observed_phase_offset_rad,
    )
    closure = distance_m(points[0], points[-1])
    signal_rms = rms(errors)
    return ToroidalSineReferenceResult(
        phase_error_rad=phase_error,
        phase_lock_score=0.5 * (1.0 + math.cos(phase_error)),
        signal_rms_error=signal_rms,
        signal_normalized_rms_error=signal_rms / state.amplitude,
        closure_residual_m=closure,
        closure_residual_normalized=closure / state.major_radius_m,
        maximum_surface_residual_m=maximum_surface_residual,
        geometric_path_metric_dimensionless=path_metric,
        sample_count=state.sample_count,
        cycle_closed_within_tolerance=closure <= closure_tolerance_m,
    )


def baseline() -> dict:
    state = ToroidalSineReferenceState(
        major_radius_m=3.0,
        minor_radius_m=1.0,
        inner_frequency_hz=2.0,
        outer_frequency_hz=1.0,
        reference_frequency_hz=1.0,
        amplitude=1.0,
        amplitude_unit="normalized",
        duration_s=1.0,
        sample_count=1001,
        observed_phase_offset_rad=math.pi / 6.0,
    )
    result = evaluate(state)
    return {
        "schema": "rll.strong_gravity.toroidal_sine_reference.baseline.v1",
        "input": asdict(state),
        "result": result.to_dict(),
        "boundaries": {
            "toroidal_geometry_is_operational_model": True,
            "pure_sine_is_universal_stabilizer": False,
            "tokamak_result_equals_black_hole_accretion": False,
            "plasma_confinement_solved": False,
            "grmhd_source_fit": False,
            "cosmological_background_modified": False,
            "claim_allowed": False,
        },
    }


if __name__ == "__main__":
    print(json.dumps(baseline(), indent=2, sort_keys=True))
