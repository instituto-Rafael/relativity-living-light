"""Bounded magnetorotational, MAD and relativistic-jet bridge.

This module connects the session's rotating-dipole, electroaerodynamic-deflection
and black-hole-plasma discussion through explicit diagnostics. It is not a GRMHD,
force-free, PIC, radiative-transfer or cosmological solver.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from typing import Iterable

C_M_S = 299_792_458.0
G_M3_KG_S2 = 6.67430e-11
MU0_N_A2 = 1.25663706212e-6
PI = math.pi
SOLAR_MASS_KG = 1.98847e30
Vector3 = tuple[float, float, float]


def _vector3(values: Iterable[float], name: str) -> Vector3:
    data = tuple(float(value) for value in values)
    if len(data) != 3 or not all(math.isfinite(value) for value in data):
        raise ValueError(f"{name} must contain three finite components")
    return data[0], data[1], data[2]


def vector_add(a: Vector3, b: Vector3) -> Vector3:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def vector_scale(scale: float, vector: Vector3) -> Vector3:
    if not math.isfinite(scale):
        raise ValueError("scale must be finite")
    return scale * vector[0], scale * vector[1], scale * vector[2]


def cross(a: Vector3, b: Vector3) -> Vector3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def magnitude(vector: Vector3) -> float:
    return math.sqrt(sum(component * component for component in vector))


@dataclass(frozen=True)
class DipoleRotorState:
    volume_m3: float
    density_kg_m3: float
    magnetization_a_m: float
    characteristic_radius_m: float
    inertia_coefficient: float
    spin_angular_frequency_rad_s: float
    field_angular_frequency_rad_s: float
    magnetic_field_t: float

    def validate(self) -> None:
        positive = {
            "volume_m3": self.volume_m3,
            "density_kg_m3": self.density_kg_m3,
            "characteristic_radius_m": self.characteristic_radius_m,
            "inertia_coefficient": self.inertia_coefficient,
            "spin_angular_frequency_rad_s": self.spin_angular_frequency_rad_s,
            "field_angular_frequency_rad_s": self.field_angular_frequency_rad_s,
        }
        for name, value in positive.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite")
        if not math.isfinite(self.magnetization_a_m) or self.magnetization_a_m < 0:
            raise ValueError("magnetization_a_m must be non-negative and finite")
        if not math.isfinite(self.magnetic_field_t):
            raise ValueError("magnetic_field_t must be finite")

    @property
    def mass_kg(self) -> float:
        return self.density_kg_m3 * self.volume_m3

    @property
    def magnetic_moment_a_m2(self) -> float:
        return self.magnetization_a_m * self.volume_m3

    @property
    def moment_of_inertia_kg_m2(self) -> float:
        return self.inertia_coefficient * self.mass_kg * self.characteristic_radius_m**2


@dataclass(frozen=True)
class KerrPlasmaState:
    central_mass_kg: float
    spin_dimensionless: float
    magnetic_field_t: float
    mass_density_kg_m3: float
    specific_enthalpy_dimensionless: float
    radial_speed_m_s: float
    thermal_pressure_pa: float
    magnetic_flux_wb: float
    field_angular_frequency_rad_s: float
    bz_kappa: float = 0.05

    def validate(self) -> None:
        if not math.isfinite(self.central_mass_kg) or self.central_mass_kg <= 0:
            raise ValueError("central_mass_kg must be positive and finite")
        if not math.isfinite(self.spin_dimensionless) or abs(self.spin_dimensionless) >= 1:
            raise ValueError("spin_dimensionless must satisfy |a_*| < 1")
        if not math.isfinite(self.magnetic_field_t):
            raise ValueError("magnetic_field_t must be finite")
        if not math.isfinite(self.mass_density_kg_m3) or self.mass_density_kg_m3 <= 0:
            raise ValueError("mass_density_kg_m3 must be positive and finite")
        if not math.isfinite(self.specific_enthalpy_dimensionless) or self.specific_enthalpy_dimensionless < 1:
            raise ValueError("specific_enthalpy_dimensionless must be >= 1")
        if not math.isfinite(self.radial_speed_m_s) or not 0 <= self.radial_speed_m_s < C_M_S:
            raise ValueError("radial_speed_m_s must be in [0, c)")
        if not math.isfinite(self.thermal_pressure_pa) or self.thermal_pressure_pa < 0:
            raise ValueError("thermal_pressure_pa must be non-negative and finite")
        if not math.isfinite(self.magnetic_flux_wb) or self.magnetic_flux_wb < 0:
            raise ValueError("magnetic_flux_wb must be non-negative and finite")
        if not math.isfinite(self.field_angular_frequency_rad_s) or self.field_angular_frequency_rad_s <= 0:
            raise ValueError("field_angular_frequency_rad_s must be positive")
        if not math.isfinite(self.bz_kappa) or self.bz_kappa < 0:
            raise ValueError("bz_kappa must be non-negative")


@dataclass(frozen=True)
class MagnetorotationalJetResult:
    dipole_mass_kg: float
    dipole_magnetic_moment_a_m2: float
    dipole_moment_of_inertia_kg_m2: float
    rotational_lock_parameter: float
    rotational_regime: str
    electromagnetic_force_density_n_m3: Vector3
    electromagnetic_force_density_magnitude_n_m3: float
    poynting_flux_w_m2: Vector3
    poynting_flux_magnitude_w_m2: float
    gravitational_radius_m: float
    horizon_angular_frequency_rad_s: float
    light_cylinder_radius_m: float
    magnetic_pressure_pa: float
    ram_pressure_pa: float
    arrest_parameter: float
    arrest_regime: str
    magnetization_sigma: float
    conversion_regime: str
    blandford_znajek_power_proxy_w: float
    claim_allowed: bool = False

    def to_dict(self) -> dict:
        out = asdict(self)
        out["claim_boundary"] = (
            "Diagnostics and scaling proxies only. No GRMHD, force-free, PIC, "
            "radiative-transfer, observational or RLL cosmology validation."
        )
        return out


def electric_force_density_n_m3(charge_density_c_m3: float, electric_field_v_m: Vector3) -> Vector3:
    if not math.isfinite(charge_density_c_m3):
        raise ValueError("charge_density_c_m3 must be finite")
    return vector_scale(charge_density_c_m3, _vector3(electric_field_v_m, "electric_field_v_m"))


def electromagnetic_force_density_n_m3(
    charge_density_c_m3: float,
    electric_field_v_m: Vector3,
    current_density_a_m2: Vector3,
    magnetic_field_t: Vector3,
) -> Vector3:
    electric = electric_force_density_n_m3(charge_density_c_m3, electric_field_v_m)
    current = _vector3(current_density_a_m2, "current_density_a_m2")
    magnetic = _vector3(magnetic_field_t, "magnetic_field_t")
    return vector_add(electric, cross(current, magnetic))


def poynting_flux_w_m2(electric_field_v_m: Vector3, magnetic_field_t: Vector3) -> Vector3:
    electric = _vector3(electric_field_v_m, "electric_field_v_m")
    magnetic = _vector3(magnetic_field_t, "magnetic_field_t")
    return vector_scale(1.0 / MU0_N_A2, cross(electric, magnetic))


def rotational_lock_parameter(state: DipoleRotorState) -> float:
    state.validate()
    denominator = (
        state.moment_of_inertia_kg_m2
        * state.spin_angular_frequency_rad_s
        * state.field_angular_frequency_rad_s
    )
    return abs(state.magnetic_moment_a_m2 * state.magnetic_field_t) / denominator


def rotational_regime(parameter: float) -> str:
    if parameter < 0 or not math.isfinite(parameter):
        raise ValueError("parameter must be non-negative and finite")
    if parameter < 0.1:
        return "angular_inertia_dominated"
    if parameter <= 10.0:
        return "phase_lock_transition"
    return "field_torque_dominated"


def similar_body_scaling(reference_volume_m3: float, target_volume_m3: float) -> dict:
    if reference_volume_m3 <= 0 or target_volume_m3 <= 0:
        raise ValueError("volumes must be positive")
    ratio = target_volume_m3 / reference_volume_m3
    return {
        "volume_ratio": ratio,
        "magnetic_moment_ratio": ratio,
        "moment_of_inertia_ratio": ratio ** (5.0 / 3.0),
        "angular_response_ratio": ratio ** (-2.0 / 3.0),
    }


def gravitational_radius_m(central_mass_kg: float) -> float:
    if central_mass_kg <= 0:
        raise ValueError("central_mass_kg must be positive")
    return G_M3_KG_S2 * central_mass_kg / C_M_S**2


def horizon_angular_frequency_rad_s(central_mass_kg: float, spin_dimensionless: float) -> float:
    if central_mass_kg <= 0 or abs(spin_dimensionless) >= 1:
        raise ValueError("invalid mass or Kerr spin")
    if spin_dimensionless == 0:
        return 0.0
    denominator = 2.0 * G_M3_KG_S2 * central_mass_kg * (
        1.0 + math.sqrt(1.0 - spin_dimensionless**2)
    )
    return spin_dimensionless * C_M_S**3 / denominator


def light_cylinder_radius_m(field_angular_frequency_rad_s: float) -> float:
    if field_angular_frequency_rad_s <= 0:
        raise ValueError("field angular frequency must be positive")
    return C_M_S / field_angular_frequency_rad_s


def magnetic_pressure_pa(magnetic_field_t: float) -> float:
    if not math.isfinite(magnetic_field_t):
        raise ValueError("magnetic_field_t must be finite")
    return magnetic_field_t**2 / (2.0 * MU0_N_A2)


def ram_pressure_pa(mass_density_kg_m3: float, radial_speed_m_s: float) -> float:
    if mass_density_kg_m3 <= 0 or not 0 <= radial_speed_m_s < C_M_S:
        raise ValueError("invalid density or radial speed")
    return mass_density_kg_m3 * radial_speed_m_s**2


def arrest_parameter(
    magnetic_field_t: float,
    mass_density_kg_m3: float,
    radial_speed_m_s: float,
    thermal_pressure_pa: float,
) -> float:
    if thermal_pressure_pa < 0:
        raise ValueError("thermal_pressure_pa must be non-negative")
    denominator = ram_pressure_pa(mass_density_kg_m3, radial_speed_m_s) + thermal_pressure_pa
    if denominator <= 0:
        raise ValueError("ram plus thermal pressure must be positive")
    return magnetic_pressure_pa(magnetic_field_t) / denominator


def arrest_regime(parameter: float) -> str:
    if parameter < 0 or not math.isfinite(parameter):
        raise ValueError("parameter must be non-negative and finite")
    if parameter < 0.1:
        return "magnetically_subdominant"
    if parameter < 1.0:
        return "magnetic_transition"
    return "mad_candidate"


def magnetization_sigma(
    magnetic_field_t: float,
    mass_density_kg_m3: float,
    specific_enthalpy_dimensionless: float,
) -> float:
    if mass_density_kg_m3 <= 0 or specific_enthalpy_dimensionless < 1:
        raise ValueError("invalid density or specific enthalpy")
    return magnetic_field_t**2 / (
        MU0_N_A2 * mass_density_kg_m3 * specific_enthalpy_dimensionless * C_M_S**2
    )


def conversion_regime(sigma: float) -> str:
    if sigma < 0 or not math.isfinite(sigma):
        raise ValueError("sigma must be non-negative and finite")
    if sigma < 0.1:
        return "matter_energy_dominated"
    if sigma < 1.0:
        return "mixed_conversion"
    return "poynting_dominated_candidate"


def blandford_znajek_power_proxy_w(
    magnetic_flux_wb: float,
    horizon_angular_frequency_rad_s_value: float,
    kappa: float,
) -> float:
    if magnetic_flux_wb < 0 or kappa < 0:
        raise ValueError("magnetic flux and kappa must be non-negative")
    return (
        kappa
        * magnetic_flux_wb**2
        * horizon_angular_frequency_rad_s_value**2
        / (MU0_N_A2 * C_M_S)
    )


def evaluate(
    rotor: DipoleRotorState,
    plasma: KerrPlasmaState,
    charge_density_c_m3: float,
    electric_field_v_m: Vector3,
    current_density_a_m2: Vector3,
    magnetic_field_vector_t: Vector3,
) -> MagnetorotationalJetResult:
    rotor.validate()
    plasma.validate()
    force = electromagnetic_force_density_n_m3(
        charge_density_c_m3,
        electric_field_v_m,
        current_density_a_m2,
        magnetic_field_vector_t,
    )
    poynting = poynting_flux_w_m2(electric_field_v_m, magnetic_field_vector_t)
    lock = rotational_lock_parameter(rotor)
    omega_h = horizon_angular_frequency_rad_s(plasma.central_mass_kg, plasma.spin_dimensionless)
    arrest = arrest_parameter(
        plasma.magnetic_field_t,
        plasma.mass_density_kg_m3,
        plasma.radial_speed_m_s,
        plasma.thermal_pressure_pa,
    )
    sigma = magnetization_sigma(
        plasma.magnetic_field_t,
        plasma.mass_density_kg_m3,
        plasma.specific_enthalpy_dimensionless,
    )
    return MagnetorotationalJetResult(
        dipole_mass_kg=rotor.mass_kg,
        dipole_magnetic_moment_a_m2=rotor.magnetic_moment_a_m2,
        dipole_moment_of_inertia_kg_m2=rotor.moment_of_inertia_kg_m2,
        rotational_lock_parameter=lock,
        rotational_regime=rotational_regime(lock),
        electromagnetic_force_density_n_m3=force,
        electromagnetic_force_density_magnitude_n_m3=magnitude(force),
        poynting_flux_w_m2=poynting,
        poynting_flux_magnitude_w_m2=magnitude(poynting),
        gravitational_radius_m=gravitational_radius_m(plasma.central_mass_kg),
        horizon_angular_frequency_rad_s=omega_h,
        light_cylinder_radius_m=light_cylinder_radius_m(plasma.field_angular_frequency_rad_s),
        magnetic_pressure_pa=magnetic_pressure_pa(plasma.magnetic_field_t),
        ram_pressure_pa=ram_pressure_pa(plasma.mass_density_kg_m3, plasma.radial_speed_m_s),
        arrest_parameter=arrest,
        arrest_regime=arrest_regime(arrest),
        magnetization_sigma=sigma,
        conversion_regime=conversion_regime(sigma),
        blandford_znajek_power_proxy_w=blandford_znajek_power_proxy_w(
            plasma.magnetic_flux_wb, omega_h, plasma.bz_kappa
        ),
    )


def baseline() -> dict:
    rotor = DipoleRotorState(
        volume_m3=1.0,
        density_kg_m3=7_500.0,
        magnetization_a_m=1.19e6,
        characteristic_radius_m=0.5,
        inertia_coefficient=0.4,
        spin_angular_frequency_rad_s=1_000.0,
        field_angular_frequency_rad_s=500.0,
        magnetic_field_t=1.5,
    )
    central_mass = 10.0 * SOLAR_MASS_KG
    rg = gravitational_radius_m(central_mass)
    plasma_b = 1.0e4
    plasma = KerrPlasmaState(
        central_mass_kg=central_mass,
        spin_dimensionless=0.9,
        magnetic_field_t=plasma_b,
        mass_density_kg_m3=1.0e-4,
        specific_enthalpy_dimensionless=2.0,
        radial_speed_m_s=0.1 * C_M_S,
        thermal_pressure_pa=1.0e11,
        magnetic_flux_wb=plasma_b * PI * rg**2,
        field_angular_frequency_rad_s=500.0,
        bz_kappa=0.05,
    )
    result = evaluate(
        rotor=rotor,
        plasma=plasma,
        charge_density_c_m3=1.0e-6,
        electric_field_v_m=(1.0e6, 0.0, 0.0),
        current_density_a_m2=(0.0, 1.0e6, 0.0),
        magnetic_field_vector_t=(0.0, 0.0, plasma_b),
    )
    return {
        "schema": "rll.strong_gravity.magnetorotational_jet_bridge.baseline.v1",
        "rotor_input": asdict(rotor),
        "plasma_input": asdict(plasma),
        "force_input": {
            "charge_density_c_m3": 1.0e-6,
            "electric_field_v_m": [1.0e6, 0.0, 0.0],
            "current_density_a_m2": [0.0, 1.0e6, 0.0],
            "magnetic_field_vector_t": [0.0, 0.0, plasma_b],
        },
        "similar_body_scaling_1_to_10_m3": similar_body_scaling(1.0, 10.0),
        "result": result.to_dict(),
        "boundaries": {
            "n55_literal_black_hole_material": False,
            "rotating_dipole_parable_preserved": True,
            "electroaerodynamic_equals_grmhd": False,
            "mad_confirmed_for_source": False,
            "relativistic_jet_confirmed_for_source": False,
            "cosmological_background_modified": False,
            "claim_allowed": False,
        },
    }


if __name__ == "__main__":
    print(json.dumps(baseline(), indent=2, sort_keys=True))
