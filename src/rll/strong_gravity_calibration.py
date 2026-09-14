"""Strong-gravity heuristic calibration primitives for RLL.

The module converts the session's analogies (compression, electrolysis,
fatigue, radiation and collective gravity) into explicit, unit-aware
operators and epistemic gates. It is dependency-free for CPython/Termux.

It does not claim a new interaction or replace GRMHD/GRPIC. Numerical sweeps
are reference calculations or synthetic smoke tests unless an observational
manifest says otherwise.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import math
from typing import Any, Iterable

G = 6.67430e-11
C = 299_792_458.0
K_E = 8.9875517923e9
E_CHARGE = 1.602176634e-19
M_E = 9.1093837139e-31
M_P = 1.67262192595e-27
M_SUN = 1.98847e30
H_PLANCK = 6.62607015e-34
EV_J = E_CHARGE
R_GAS = 8.31446261815324
MOLAR_MASS_WATER = 0.01801528


class Regime(str, Enum):
    INFALL_DOMINANT = "infall_dominant"
    TRANSITIONAL = "transitional"
    EXPANSION_OUTFLOW = "expansion_or_outflow"
    SELF_GRAVITY_INSTABILITY = "self_gravity_instability_candidate"
    BACKREACTION_RELEVANT = "disk_backreaction_relevant"
    SELF_GRAVITY_SUBDOMINANT = "self_gravity_subdominant"
    TOKEN_VAZIO = "TOKEN_VAZIO"


@dataclass(frozen=True)
class CascadeState:
    """Minimal recurrent state X=(rho, x_e, J, u)."""

    density: float
    ionization_fraction: float
    current_density: float
    internal_energy_density: float

    def validate(self) -> None:
        if self.density < 0:
            raise ValueError("density must be non-negative")
        if not 0.0 <= self.ionization_fraction <= 1.0:
            raise ValueError("ionization_fraction must be in [0, 1]")
        if self.internal_energy_density < 0:
            raise ValueError("internal_energy_density must be non-negative")


@dataclass(frozen=True)
class CascadeRates:
    """Rates used by one explicit-Euler calibration step.

    All values must share a caller-declared unit system. The implementation
    preserves signs instead of silently converting conventions.
    """

    expansion_scalar: float
    pressure: float
    photoionization_rate: float
    impact_ionization_rate: float
    field_ionization_rate: float
    tidal_ionization_rate: float
    recombination_rate: float
    current_drive: float
    current_relaxation_time: float
    gravity_heating: float
    electromagnetic_heating: float
    radiation_heating: float
    cooling: float
    outflow_loss: float

    def validate(self) -> None:
        non_negative = {
            "pressure": self.pressure,
            "photoionization_rate": self.photoionization_rate,
            "impact_ionization_rate": self.impact_ionization_rate,
            "field_ionization_rate": self.field_ionization_rate,
            "tidal_ionization_rate": self.tidal_ionization_rate,
            "recombination_rate": self.recombination_rate,
            "current_relaxation_time": self.current_relaxation_time,
            "gravity_heating": self.gravity_heating,
            "electromagnetic_heating": self.electromagnetic_heating,
            "radiation_heating": self.radiation_heating,
            "cooling": self.cooling,
            "outflow_loss": self.outflow_loss,
        }
        for name, value in non_negative.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.current_relaxation_time == 0:
            raise ValueError("current_relaxation_time must be positive")


def gravitational_radius(mass_kg: float) -> float:
    if mass_kg <= 0:
        raise ValueError("mass_kg must be positive")
    return G * mass_kg / C**2


def keplerian_angular_frequency(mass_kg: float, radius_m: float) -> float:
    if mass_kg <= 0 or radius_m <= 0:
        raise ValueError("mass and radius must be positive")
    return math.sqrt(G * mass_kg / radius_m**3)


def orbital_period(mass_kg: float, radius_m: float) -> float:
    return 2.0 * math.pi / keplerian_angular_frequency(mass_kg, radius_m)


def disk_mass_ratio(disk_mass_kg: float, central_mass_kg: float) -> float:
    if disk_mass_kg < 0 or central_mass_kg <= 0:
        raise ValueError("invalid masses")
    return disk_mass_kg / central_mass_kg


def ring_surface_density(disk_mass_kg: float, radius_m: float) -> float:
    """Reference mean surface density M_d/(pi r^2), not a disk profile."""
    if disk_mass_kg < 0 or radius_m <= 0:
        raise ValueError("invalid ring inputs")
    return disk_mass_kg / (math.pi * radius_m**2)


def toomre_q(sound_speed: float, epicyclic_frequency: float, surface_density: float) -> float:
    if sound_speed < 0 or epicyclic_frequency < 0 or surface_density <= 0:
        raise ValueError("invalid Toomre inputs")
    return sound_speed * epicyclic_frequency / (math.pi * G * surface_density)


def classify_self_gravity(toomre_value: float, mass_ratio: float) -> Regime:
    if toomre_value <= 0 or mass_ratio < 0:
        raise ValueError("invalid self-gravity diagnostics")
    if toomre_value <= 1.0:
        return Regime.SELF_GRAVITY_INSTABILITY
    if mass_ratio >= 0.1:
        return Regime.BACKREACTION_RELEVANT
    return Regime.SELF_GRAVITY_SUBDOMINANT


def compressive_heating_rate(pressure: float, expansion_scalar: float) -> float:
    """Return -p*Theta; positive for compression when Theta<0."""
    if pressure < 0:
        raise ValueError("pressure must be non-negative")
    return -pressure * expansion_scalar


def gravitothermal_ratio(
    thermal_pressure: float,
    magnetic_pressure: float,
    radiation_pressure: float,
    density: float,
    potential_depth: float,
) -> float:
    """R_GT=(P_th+P_B+P_rad)/(rho*|Phi_eff|)."""
    values = (thermal_pressure, magnetic_pressure, radiation_pressure, density)
    if any(value < 0 for value in values) or potential_depth == 0:
        raise ValueError("invalid gravitothermal inputs")
    denominator = density * abs(potential_depth)
    if denominator == 0:
        raise ValueError("density*potential_depth must be non-zero")
    return (thermal_pressure + magnetic_pressure + radiation_pressure) / denominator


def classify_gravitothermal(ratio: float, tolerance: float = 0.1) -> Regime:
    if ratio < 0 or tolerance < 0:
        raise ValueError("invalid classification input")
    if ratio < 1.0 - tolerance:
        return Regime.INFALL_DOMINANT
    if ratio <= 1.0 + tolerance:
        return Regime.TRANSITIONAL
    return Regime.EXPANSION_OUTFLOW


def magnetoelectric_transduction(
    electrical_power_density: float,
    compressive_power_density: float,
    epsilon: float = 1e-30,
) -> float:
    if electrical_power_density < 0 or compressive_power_density < 0 or epsilon <= 0:
        raise ValueError("invalid transduction inputs")
    return electrical_power_density / (compressive_power_density + epsilon)


def oscillator_quality_factor(angular_frequency: float, damping_rate: float) -> float:
    if angular_frequency < 0 or damping_rate <= 0:
        raise ValueError("invalid oscillator inputs")
    return angular_frequency / (2.0 * damping_rate)


def tidal_acceleration_difference(mass_kg: float, radius_m: float, length_m: float) -> float:
    if mass_kg <= 0 or radius_m <= 0 or length_m < 0:
        raise ValueError("invalid tidal inputs")
    return 2.0 * G * mass_kg * length_m / radius_m**3


def photon_energy_ev(frequency_hz: float) -> float:
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive")
    return H_PLANCK * frequency_hz / EV_J


def classify_photon_channel(energy_ev: float) -> str:
    """Heuristic interaction class, not a material-specific cross section."""
    if energy_ev < 1e-3:
        return "collective_or_rotational_heating"
    if energy_ev < 1.0:
        return "vibrational_or_electronic_heating"
    if energy_ev < 10.0:
        return "molecular_dissociation_possible"
    if energy_ev < 1.0e5:
        return "photoionization_and_secondary_electrons"
    if energy_ev < 1.022e6:
        return "high_energy_compton_nuclear_thresholds_possible"
    return "pair_production_possible_if_momentum_balance_allows"


def coulomb_to_gravity_force_ratio(
    charge_1_c: float,
    charge_2_c: float,
    mass_1_kg: float,
    mass_2_kg: float,
) -> float:
    if mass_1_kg <= 0 or mass_2_kg <= 0:
        raise ValueError("masses must be positive")
    return K_E * abs(charge_1_c * charge_2_c) / (G * mass_1_kg * mass_2_kg)


def ideal_gas_volume_m3(
    mass_kg: float,
    molar_mass_kg_per_mol: float,
    temperature_k: float,
    pressure_pa: float,
) -> float:
    if mass_kg < 0 or molar_mass_kg_per_mol <= 0 or temperature_k <= 0 or pressure_pa <= 0:
        raise ValueError("invalid ideal-gas inputs")
    moles = mass_kg / molar_mass_kg_per_mol
    return moles * R_GAS * temperature_k / pressure_pa


def advance_cascade_state(state: CascadeState, rates: CascadeRates, dt: float) -> CascadeState:
    """Advance X_(t+1)=F(X_t) for calibration/smoke tests.

    This is a transparent explicit recurrence, not a trained neural network.
    """
    state.validate()
    rates.validate()
    if dt <= 0:
        raise ValueError("dt must be positive")

    density_dot = -state.density * rates.expansion_scalar
    ionization_dot = (
        rates.photoionization_rate
        + rates.impact_ionization_rate
        + rates.field_ionization_rate
        + rates.tidal_ionization_rate
        - rates.recombination_rate * state.ionization_fraction
    )
    current_dot = (rates.current_drive - state.current_density) / rates.current_relaxation_time
    q_comp = compressive_heating_rate(rates.pressure, rates.expansion_scalar)
    energy_dot = (
        q_comp
        + rates.gravity_heating
        + rates.electromagnetic_heating
        + rates.radiation_heating
        - rates.cooling
        - rates.outflow_loss
    )

    return CascadeState(
        density=max(0.0, state.density + dt * density_dot),
        ionization_fraction=min(1.0, max(0.0, state.ionization_fraction + dt * ionization_dot)),
        current_density=state.current_density + dt * current_dot,
        internal_energy_density=max(0.0, state.internal_energy_density + dt * energy_dot),
    )


def iterate_cascade(
    initial: CascadeState,
    rates: CascadeRates,
    dt: float,
    steps: int,
) -> list[CascadeState]:
    if steps < 0:
        raise ValueError("steps must be non-negative")
    states = [initial]
    current = initial
    for _ in range(steps):
        current = advance_cascade_state(current, rates, dt)
        states.append(current)
    return states


def reference_black_hole_sweep(
    central_mass_solar: float,
    radius_rg: float = 20.0,
    sound_speed_fraction_c: float = 0.05,
    mass_ratios: Iterable[float] = (1e-3, 1e-2, 1e-1, 2.5e-1),
) -> dict[str, Any]:
    """Deterministic scale sweep using a mean-ring surface density.

    This is a reference calculation, not a GRMHD solution.
    """
    if central_mass_solar <= 0 or radius_rg <= 0 or sound_speed_fraction_c < 0:
        raise ValueError("invalid sweep configuration")
    mass = central_mass_solar * M_SUN
    radius = radius_rg * gravitational_radius(mass)
    omega = keplerian_angular_frequency(mass, radius)
    sound_speed = sound_speed_fraction_c * C
    rows = []
    for ratio in mass_ratios:
        if ratio <= 0:
            raise ValueError("mass ratios must be positive")
        disk_mass = ratio * mass
        sigma = ring_surface_density(disk_mass, radius)
        q_t = toomre_q(sound_speed, omega, sigma)
        rows.append(
            {
                "disk_mass_ratio": ratio,
                "toomre_q_reference": q_t,
                "self_gravity_regime": classify_self_gravity(q_t, ratio).value,
                "surface_density_kg_m2": sigma,
            }
        )
    return {
        "central_mass_solar": central_mass_solar,
        "radius_rg": radius_rg,
        "radius_m": radius,
        "sound_speed_fraction_c": sound_speed_fraction_c,
        "orbital_angular_frequency_rad_s": omega,
        "orbital_period_s": orbital_period(mass, radius),
        "rows": rows,
        "claim_allowed": False,
        "model_scope": "Newtonian reference ring; not a relativistic disk solution",
    }


def calibration_payload() -> dict[str, Any]:
    """Produce the deterministic numerical payload committed with the session."""
    frequencies = {
        "microwave_2_45_GHz": 2.45e9,
        "infrared_30_THz": 3.0e13,
        "ultraviolet_3_PHz": 3.0e15,
        "xray_10_keV_approx": 2.417989e18,
        "gamma_1_MeV_approx": 2.417989e20,
    }
    photon_rows = []
    for name, frequency in frequencies.items():
        energy = photon_energy_ev(frequency)
        photon_rows.append(
            {
                "name": name,
                "frequency_hz": frequency,
                "energy_ev": energy,
                "channel": classify_photon_channel(energy),
            }
        )

    steam_volume = ideal_gas_volume_m3(
        mass_kg=1.0,
        molar_mass_kg_per_mol=MOLAR_MASS_WATER,
        temperature_k=373.15,
        pressure_pa=101_325.0,
    )
    force_ratio = coulomb_to_gravity_force_ratio(-E_CHARGE, E_CHARGE, M_E, M_P)

    initial = CascadeState(1.0, 0.05, 0.0, 1.0)
    rates = CascadeRates(
        expansion_scalar=-0.2,
        pressure=1.0,
        photoionization_rate=0.08,
        impact_ionization_rate=0.12,
        field_ionization_rate=0.05,
        tidal_ionization_rate=0.0,
        recombination_rate=0.10,
        current_drive=2.0,
        current_relaxation_time=2.0,
        gravity_heating=0.05,
        electromagnetic_heating=0.10,
        radiation_heating=0.08,
        cooling=0.07,
        outflow_loss=0.03,
    )
    states = iterate_cascade(initial, rates, dt=0.1, steps=20)

    return {
        "schema_version": "1.0.0",
        "generated_at": "2026-07-17",
        "claim_allowed": False,
        "raw_data_policy": "immutable",
        "water_reference": {
            "input_liquid_water_litre_approx": 1.0,
            "ideal_gas_steam_volume_m3_at_373_15K_1atm": steam_volume,
            "expansion_ratio_to_1_litre": steam_volume / 0.001,
            "scope": "ideal-gas reference; saturated-steam tables differ slightly",
        },
        "force_scale_reference": {
            "electron_proton_coulomb_to_gravity_ratio": force_ratio,
            "interpretation": "local atomic coupling is electromagnetic; collective mass still gravitates",
        },
        "photon_energy_ladder": photon_rows,
        "stellar_black_hole_sweep": reference_black_hole_sweep(10.0),
        "supermassive_black_hole_sweep": reference_black_hole_sweep(4.3e6),
        "recurrent_state_smoke_test": {
            "scope": "synthetic dimensionless algorithm test; not observational calibration",
            "initial": asdict(states[0]),
            "final": asdict(states[-1]),
            "steps": 20,
            "dt": 0.1,
        },
        "TOKEN_VAZIO": [
            "physical ionization rates for a specified source",
            "GRMHD/GRPIC fields and covariances",
            "observational target and loss function",
            "RNN training corpus if a neural network is intended",
        ],
    }
