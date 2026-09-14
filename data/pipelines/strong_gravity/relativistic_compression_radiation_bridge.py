"""Bounded relativistic compression, radiation-pressure and microphysics bridge.

This module separates collective compression from microscopic thresholds. It is not
a GRMHD solver, a quantum kinetic solver, or evidence for RLL cosmology.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from typing import Mapping

C_M_S = 299_792_458.0
G_M3_KG_S2 = 6.67430e-11
MU0_N_A2 = 1.25663706212e-6
HBAR_J_S = 1.054571817e-34
ELECTRON_MASS_KG = 9.1093837015e-31
PI = math.pi

REFERENCE_THRESHOLDS_EV = {
    "hydrogen_ionization_reference": 13.6,
    "electron_positron_rest_pair_reference": 1.022e6,
    "hadronic_resolution_reference": 1.0e8,
}


@dataclass(frozen=True)
class CompressionRadiationState:
    pressure_pa: float
    expansion_scalar_s_inv: float
    electron_density_m3: float
    magnetic_field_t: float
    luminosity_w: float
    radius_m: float
    opacity_m2_kg: float
    central_mass_kg: float
    photon_coupling: float = 1.0

    def validate(self) -> None:
        if self.pressure_pa < 0:
            raise ValueError("pressure_pa must be non-negative")
        if self.electron_density_m3 <= 0:
            raise ValueError("electron_density_m3 must be positive")
        if self.radius_m <= 0 or self.opacity_m2_kg <= 0 or self.central_mass_kg <= 0:
            raise ValueError("radius, opacity and central mass must be positive")
        if self.luminosity_w < 0:
            raise ValueError("luminosity_w must be non-negative")
        if not 0.0 <= self.photon_coupling <= 2.0:
            raise ValueError("photon_coupling must be in [0, 2]")


@dataclass(frozen=True)
class CompressionRadiationResult:
    compression_work_w_m3: float
    magnetic_pressure_pa: float
    radiation_flux_w_m2: float
    radiation_pressure_pa: float
    photon_thrust_n: float
    radiative_acceleration_m_s2: float
    gravity_acceleration_m_s2: float
    eddington_luminosity_w: float
    eddington_ratio: float
    acceleration_ratio: float
    electron_degeneracy_pressure_pa: float
    field_energy_equivalent_mass_density_kg_m3: float
    reached_reference_thresholds: tuple[str, ...]
    claim_allowed: bool = False

    def to_dict(self) -> dict:
        out = asdict(self)
        out["claim_boundary"] = (
            "Scalar diagnostics only. No GRMHD, quantum-kinetic, nuclear, "
            "subnuclear, laboratory, astrophysical or cosmological validation."
        )
        return out


def compression_work_w_m3(pressure_pa: float, expansion_scalar_s_inv: float) -> float:
    if pressure_pa < 0:
        raise ValueError("pressure_pa must be non-negative")
    return -pressure_pa * expansion_scalar_s_inv


def magnetic_pressure_pa(magnetic_field_t: float) -> float:
    return magnetic_field_t * magnetic_field_t / (2.0 * MU0_N_A2)


def radiation_flux_w_m2(luminosity_w: float, radius_m: float) -> float:
    if luminosity_w < 0 or radius_m <= 0:
        raise ValueError("luminosity must be non-negative and radius positive")
    return luminosity_w / (4.0 * PI * radius_m * radius_m)


def radiation_pressure_pa(flux_w_m2: float, coupling: float = 1.0) -> float:
    if flux_w_m2 < 0 or not 0.0 <= coupling <= 2.0:
        raise ValueError("invalid flux or coupling")
    return coupling * flux_w_m2 / C_M_S


def photon_thrust_n(power_w: float, coupling: float = 1.0) -> float:
    if power_w < 0 or not 0.0 <= coupling <= 2.0:
        raise ValueError("invalid power or coupling")
    return coupling * power_w / C_M_S


def radiative_acceleration_m_s2(flux_w_m2: float, opacity_m2_kg: float) -> float:
    if flux_w_m2 < 0 or opacity_m2_kg <= 0:
        raise ValueError("invalid flux or opacity")
    return opacity_m2_kg * flux_w_m2 / C_M_S


def gravity_acceleration_m_s2(central_mass_kg: float, radius_m: float) -> float:
    if central_mass_kg <= 0 or radius_m <= 0:
        raise ValueError("mass and radius must be positive")
    return G_M3_KG_S2 * central_mass_kg / (radius_m * radius_m)


def eddington_luminosity_w(central_mass_kg: float, opacity_m2_kg: float) -> float:
    if central_mass_kg <= 0 or opacity_m2_kg <= 0:
        raise ValueError("mass and opacity must be positive")
    return 4.0 * PI * G_M3_KG_S2 * central_mass_kg * C_M_S / opacity_m2_kg


def electron_degeneracy_pressure_pa(electron_density_m3: float) -> float:
    """Non-relativistic zero-temperature electron degeneracy reference."""
    if electron_density_m3 <= 0:
        raise ValueError("electron_density_m3 must be positive")
    return (
        HBAR_J_S**2
        / (5.0 * ELECTRON_MASS_KG)
        * (3.0 * PI**2) ** (2.0 / 3.0)
        * electron_density_m3 ** (5.0 / 3.0)
    )


def field_energy_equivalent_mass_density_kg_m3(
    magnetic_field_t: float, radiation_energy_density_j_m3: float
) -> float:
    if radiation_energy_density_j_m3 < 0:
        raise ValueError("radiation energy density must be non-negative")
    magnetic_energy_density = magnetic_pressure_pa(magnetic_field_t)
    return (magnetic_energy_density + radiation_energy_density_j_m3) / (C_M_S**2)


def reached_reference_thresholds(
    available_energy_ev: float,
    thresholds_ev: Mapping[str, float] = REFERENCE_THRESHOLDS_EV,
) -> tuple[str, ...]:
    """Return reached references; process cross sections remain outside this model."""
    if available_energy_ev < 0:
        raise ValueError("available_energy_ev must be non-negative")
    for name, threshold in thresholds_ev.items():
        if threshold <= 0:
            raise ValueError(f"threshold {name} must be positive")
    return tuple(
        name
        for name, threshold in sorted(thresholds_ev.items(), key=lambda item: item[1])
        if available_energy_ev >= threshold
    )


def evaluate(
    state: CompressionRadiationState, available_energy_ev: float
) -> CompressionRadiationResult:
    state.validate()
    flux = radiation_flux_w_m2(state.luminosity_w, state.radius_m)
    a_rad = radiative_acceleration_m_s2(flux, state.opacity_m2_kg)
    a_grav = gravity_acceleration_m_s2(state.central_mass_kg, state.radius_m)
    l_edd = eddington_luminosity_w(state.central_mass_kg, state.opacity_m2_kg)
    radiation_energy_density = flux / C_M_S
    return CompressionRadiationResult(
        compression_work_w_m3=compression_work_w_m3(
            state.pressure_pa, state.expansion_scalar_s_inv
        ),
        magnetic_pressure_pa=magnetic_pressure_pa(state.magnetic_field_t),
        radiation_flux_w_m2=flux,
        radiation_pressure_pa=radiation_pressure_pa(flux, state.photon_coupling),
        photon_thrust_n=photon_thrust_n(state.luminosity_w, state.photon_coupling),
        radiative_acceleration_m_s2=a_rad,
        gravity_acceleration_m_s2=a_grav,
        eddington_luminosity_w=l_edd,
        eddington_ratio=state.luminosity_w / l_edd,
        acceleration_ratio=a_rad / a_grav,
        electron_degeneracy_pressure_pa=electron_degeneracy_pressure_pa(
            state.electron_density_m3
        ),
        field_energy_equivalent_mass_density_kg_m3=(
            field_energy_equivalent_mass_density_kg_m3(
                state.magnetic_field_t, radiation_energy_density
            )
        ),
        reached_reference_thresholds=reached_reference_thresholds(
            available_energy_ev
        ),
    )


def baseline() -> dict:
    solar_mass_kg = 1.98847e30
    state = CompressionRadiationState(
        pressure_pa=1.0e12,
        expansion_scalar_s_inv=-2.0,
        electron_density_m3=1.0e35,
        magnetic_field_t=10.0,
        luminosity_w=1.0e31,
        radius_m=1.0e7,
        opacity_m2_kg=0.04,
        central_mass_kg=10.0 * solar_mass_kg,
        photon_coupling=1.0,
    )
    result = evaluate(state, available_energy_ev=2.0e6)
    return {
        "schema": "rll.relativistic_compression_radiation.baseline.v1",
        "input": asdict(state),
        "available_energy_ev": 2.0e6,
        "result": result.to_dict(),
        "boundaries": {
            "particles_touch_classically": False,
            "wavefunctions_and_scattering_interact": True,
            "compression_automatically_creates_subparticles": False,
            "spin_hydrodynamics_solved": False,
            "grmhd_solved": False,
            "einstein_backreaction_solved": False,
            "nuclear_network_solved": False,
            "claim_allowed": False,
        },
    }


if __name__ == "__main__":
    print(json.dumps(baseline(), indent=2, sort_keys=True))
