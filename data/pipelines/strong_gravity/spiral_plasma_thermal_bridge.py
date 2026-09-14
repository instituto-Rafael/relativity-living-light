"""Deterministic spiral/plasma/thermal bridge for RLL strong-gravity studies.

This module is a bounded physics model, not evidence for RLL cosmology.
All inputs are SI unless explicitly documented. The 144/288 kHz pair is treated
as an external AC drive and never as an atomic transition frequency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import cos, exp, log, pi, sqrt
from typing import Dict, Iterable, Tuple

ELEMENTARY_CHARGE_C = 1.602176634e-19
ELECTRON_MASS_KG = 9.1093837015e-31
BOLTZMANN_J_PER_K = 1.380649e-23
PLANCK_EV_S = 4.135667696e-15

FUNDAMENTAL_HZ = 144_000.0
SECOND_HARMONIC_HZ = 288_000.0
SPIRAL_RATIO = sqrt(3.0) / 2.0
SPIRAL_SECTOR_RAD = pi / 3.0


@dataclass(frozen=True)
class PlasmaState:
    electron_density_m3: float
    electron_temperature_k: float
    effective_collision_hz: float
    magnetic_field_t: float
    ionization_fraction: float

    def validate(self) -> None:
        if self.electron_density_m3 <= 0.0:
            raise ValueError("electron_density_m3 must be positive")
        if self.electron_temperature_k <= 0.0:
            raise ValueError("electron_temperature_k must be positive")
        if self.effective_collision_hz <= 0.0:
            raise ValueError("effective_collision_hz must be positive")
        if not 0.0 <= self.ionization_fraction <= 1.0:
            raise ValueError("ionization_fraction must be in [0, 1]")


@dataclass(frozen=True)
class DriveComponent:
    frequency_hz: float
    electric_field_v_m: float
    phase_rad: float = 0.0

    def validate(self) -> None:
        if self.frequency_hz <= 0.0:
            raise ValueError("frequency_hz must be positive")
        if self.electric_field_v_m < 0.0:
            raise ValueError("electric_field_v_m cannot be negative")


@dataclass(frozen=True)
class ThermalBudget:
    heat_capacity_j_m3_k: float
    compression_w_m3: float = 0.0
    gravity_w_m3: float = 0.0
    reconnection_w_m3: float = 0.0
    radiation_absorption_w_m3: float = 0.0
    nonlinear_mixing_w_m3: float = 0.0
    cooling_w_m3: float = 0.0
    outflow_w_m3: float = 0.0

    def validate(self) -> None:
        if self.heat_capacity_j_m3_k <= 0.0:
            raise ValueError("heat_capacity_j_m3_k must be positive")


@dataclass(frozen=True)
class ConductivityTensor:
    parallel_s_m: float
    pedersen_s_m: float
    hall_s_m: float
    magnetization_beta: float


@dataclass(frozen=True)
class BridgeResult:
    sigma_real_144_s_m: float
    sigma_real_288_s_m: float
    q_rf_144_w_m3: float
    q_rf_288_w_m3: float
    temperature_rate_k_s: float
    spiral_radius_m: float
    biermann_source_t_s: float
    conductivity_tensor: ConductivityTensor
    claim_allowed: bool = False

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["claim_boundary"] = (
            "Deterministic model output only; no laboratory, astrophysical, "
            "exoplanetary or cosmological claim is promoted."
        )
        return data


def angular_frequency(frequency_hz: float) -> float:
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    return 2.0 * pi * frequency_hz


def photon_energy_ev(frequency_hz: float) -> float:
    return PLANCK_EV_S * frequency_hz


def mev_to_hz(energy_mev: float) -> float:
    if energy_mev <= 0.0:
        raise ValueError("energy_mev must be positive")
    return (energy_mev * 1.0e-3) / PLANCK_EV_S


def spiral_radius(radius0_m: float, phi_rad: float) -> float:
    """Continuous form of r_n = r_0 (sqrt(3)/2)^n at 60-degree sectors."""
    if radius0_m <= 0.0:
        raise ValueError("radius0_m must be positive")
    exponent = log(SPIRAL_RATIO) * (phi_rad / SPIRAL_SECTOR_RAD)
    return radius0_m * exp(exponent)


def drude_conductivity_real_s_m(state: PlasmaState, frequency_hz: float) -> float:
    """Dissipative real conductivity for a collision-damped electron fluid."""
    state.validate()
    omega = angular_frequency(frequency_hz)
    nu = state.effective_collision_hz
    numerator = state.electron_density_m3 * ELEMENTARY_CHARGE_C**2 * nu
    denominator = ELECTRON_MASS_KG * (nu**2 + omega**2)
    return numerator / denominator


def conductivity_tensor(state: PlasmaState) -> ConductivityTensor:
    """Classical parallel, Pedersen and Hall conductivities."""
    state.validate()
    nu = state.effective_collision_hz
    omega_ce = ELEMENTARY_CHARGE_C * abs(state.magnetic_field_t) / ELECTRON_MASS_KG
    beta = omega_ce / nu
    sigma_parallel = (
        state.electron_density_m3 * ELEMENTARY_CHARGE_C**2
        / (ELECTRON_MASS_KG * nu)
    )
    denominator = 1.0 + beta**2
    return ConductivityTensor(
        parallel_s_m=sigma_parallel,
        pedersen_s_m=sigma_parallel / denominator,
        hall_s_m=sigma_parallel * beta / denominator,
        magnetization_beta=beta,
    )


def rf_heating_w_m3(state: PlasmaState, drive: DriveComponent) -> float:
    drive.validate()
    sigma_real = drude_conductivity_real_s_m(state, drive.frequency_hz)
    return 0.5 * sigma_real * drive.electric_field_v_m**2


def biermann_source_t_s(
    electron_density_m3: float,
    grad_density_m4: Tuple[float, float, float],
    grad_temperature_k_m: Tuple[float, float, float],
) -> float:
    """Magnitude of -(k_B/e)(grad n_e x grad T_e)/n_e in tesla/second."""
    if electron_density_m3 <= 0.0:
        raise ValueError("electron_density_m3 must be positive")
    ax, ay, az = grad_density_m4
    bx, by, bz = grad_temperature_k_m
    cross = (
        ay * bz - az * by,
        az * bx - ax * bz,
        ax * by - ay * bx,
    )
    magnitude = sqrt(sum(component * component for component in cross))
    return (BOLTZMANN_J_PER_K / ELEMENTARY_CHARGE_C) * magnitude / electron_density_m3


def temperature_rate_k_s(
    state: PlasmaState,
    drives: Iterable[DriveComponent],
    budget: ThermalBudget,
) -> float:
    state.validate()
    budget.validate()
    q_rf = sum(rf_heating_w_m3(state, drive) for drive in drives)
    q_net = (
        budget.compression_w_m3
        + budget.gravity_w_m3
        + budget.reconnection_w_m3
        + budget.radiation_absorption_w_m3
        + budget.nonlinear_mixing_w_m3
        + q_rf
        - budget.cooling_w_m3
        - budget.outflow_w_m3
    )
    return q_net / budget.heat_capacity_j_m3_k


def harmonic_drive_value(
    time_s: float,
    fundamental: DriveComponent,
    second_harmonic: DriveComponent,
) -> float:
    fundamental.validate()
    second_harmonic.validate()
    if abs(second_harmonic.frequency_hz - 2.0 * fundamental.frequency_hz) > 1.0e-9:
        raise ValueError("second_harmonic frequency must equal 2 * fundamental")
    return (
        fundamental.electric_field_v_m
        * cos(angular_frequency(fundamental.frequency_hz) * time_s + fundamental.phase_rad)
        + second_harmonic.electric_field_v_m
        * cos(
            angular_frequency(second_harmonic.frequency_hz) * time_s
            + second_harmonic.phase_rad
        )
    )


def evaluate_bridge(
    state: PlasmaState,
    fundamental: DriveComponent,
    second_harmonic: DriveComponent,
    budget: ThermalBudget,
    radius0_m: float,
    phi_rad: float,
    grad_density_m4: Tuple[float, float, float],
    grad_temperature_k_m: Tuple[float, float, float],
) -> BridgeResult:
    if abs(fundamental.frequency_hz - FUNDAMENTAL_HZ) > 1.0e-9:
        raise ValueError("fundamental must be 144 kHz for the canonical benchmark")
    if abs(second_harmonic.frequency_hz - SECOND_HARMONIC_HZ) > 1.0e-9:
        raise ValueError("second_harmonic must be 288 kHz for the canonical benchmark")
    tensor = conductivity_tensor(state)
    return BridgeResult(
        sigma_real_144_s_m=drude_conductivity_real_s_m(state, FUNDAMENTAL_HZ),
        sigma_real_288_s_m=drude_conductivity_real_s_m(state, SECOND_HARMONIC_HZ),
        q_rf_144_w_m3=rf_heating_w_m3(state, fundamental),
        q_rf_288_w_m3=rf_heating_w_m3(state, second_harmonic),
        temperature_rate_k_s=temperature_rate_k_s(
            state, (fundamental, second_harmonic), budget
        ),
        spiral_radius_m=spiral_radius(radius0_m, phi_rad),
        biermann_source_t_s=biermann_source_t_s(
            state.electron_density_m3,
            grad_density_m4,
            grad_temperature_k_m,
        ),
        conductivity_tensor=tensor,
    )
