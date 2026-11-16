"""Strong-gravity photonic transport diagnostics for RLL.

This module is deliberately small, dependency-free and epistemically bounded.
It supplies exact algebraic/ODE identities and dimensionless diagnostics that
can be compared with GRMHD/GRRMHD/GRPIC + relativistic radiative-transfer
baselines.  It does not define a new interaction and does not promote the
"upside-down hammer" analogy to a law of nature.

Conventions
-----------
* SI for dimensional helpers unless explicitly stated.
* theta = div(u) has units 1/s in the local frame used by the caller.
* pressures share one unit system.
* frequency gains are positive multiplicative ratios.
* TOKEN_VAZIO is preserved whenever a physical closure must come from an
  external EOS, opacity, nuclear network or calibrated transport model.
"""
from __future__ import annotations

import math
from typing import Iterable

H_PLANCK = 6.62607015e-34
E_CHARGE = 1.602176634e-19
EPSILON_0 = 8.8541878128e-12
M_E = 9.1093837139e-31


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def convergent_compression_number(expansion_scalar: float, flow_time_s: float) -> float:
    """C_down=max(0,-Theta)*tau_flow, an adimensional convergence measure."""
    theta = _finite("expansion_scalar", expansion_scalar)
    tau = _finite("flow_time_s", flow_time_s)
    if tau < 0:
        raise ValueError("flow_time_s must be non-negative")
    return max(0.0, -theta) * tau


def ram_pressure_ratio(
    ram_pressure: float,
    thermal_pressure: float,
    magnetic_pressure: float,
    radiation_pressure: float,
) -> float:
    """R_ram=p_ram/(p_th+p_B+p_rad)."""
    vals = [
        _finite("ram_pressure", ram_pressure),
        _finite("thermal_pressure", thermal_pressure),
        _finite("magnetic_pressure", magnetic_pressure),
        _finite("radiation_pressure", radiation_pressure),
    ]
    if any(value < 0 for value in vals):
        raise ValueError("pressures must be non-negative")
    denominator = sum(vals[1:])
    if denominator <= 0:
        raise ValueError("supporting pressure sum must be positive")
    return vals[0] / denominator


def upside_down_hammer_number(
    expansion_scalar: float,
    flow_time_s: float,
    fast_mach: float,
    ram_pressure: float,
    thermal_pressure: float,
    magnetic_pressure: float,
    radiation_pressure: float,
) -> float:
    """Dimensionless hypothesis diagnostic H_down=C_down*M_f*R_ram.

    This is a diagnostic for falsification, not a universal shock law.  It is
    useful only if it adds predictive information beyond the underlying
    compression, Mach number and pressure-ratio baselines.
    """
    mach = _finite("fast_mach", fast_mach)
    if mach < 0:
        raise ValueError("fast_mach must be non-negative")
    return (
        convergent_compression_number(expansion_scalar, flow_time_s)
        * mach
        * ram_pressure_ratio(
            ram_pressure,
            thermal_pressure,
            magnetic_pressure,
            radiation_pressure,
        )
    )


def damkohler_number(flow_time_s: float, process_time_s: float) -> float:
    """Da=tau_flow/tau_process."""
    flow = _finite("flow_time_s", flow_time_s)
    process = _finite("process_time_s", process_time_s)
    if flow < 0 or process <= 0:
        raise ValueError("flow time must be >=0 and process time >0")
    return flow / process


def first_order_completion(flow_time_s: float, process_time_s: float) -> float:
    """For dX/dt=(1-X)/tau: X(tau_flow)=1-exp(-Da)."""
    return -math.expm1(-damkohler_number(flow_time_s, process_time_s))


def compose_frequency_gains(gains: Iterable[float]) -> float:
    """Sequential deterministic frequency gains multiply, never add."""
    total = 1.0
    seen = False
    for raw in gains:
        gain = _finite("gain", raw)
        if gain <= 0:
            raise ValueError("all frequency gains must be positive")
        total *= gain
        seen = True
    return total if seen else 1.0


def log_hardening(gains: Iterable[float]) -> float:
    """H_nu=ln(nu_out/nu_in)=sum_j ln(g_j)."""
    total = 0.0
    for raw in gains:
        gain = _finite("gain", raw)
        if gain <= 0:
            raise ValueError("all frequency gains must be positive")
        total += math.log(gain)
    return total


def spiral_radial_wavelength(radial_wavenumber: float) -> float:
    """Local wavelength lambda_r=2*pi/|k_r|."""
    k_r = _finite("radial_wavenumber", radial_wavenumber)
    if k_r == 0:
        raise ValueError("radial_wavenumber must be non-zero")
    return 2.0 * math.pi / abs(k_r)


def logistic_transition(chi: float, midpoint: float, width: float) -> float:
    """f=1/(1+exp((chi-midpoint)/width)); phenomenological only."""
    x = _finite("chi", chi)
    x0 = _finite("midpoint", midpoint)
    w = _finite("width", width)
    if w == 0:
        raise ValueError("width must be non-zero")
    z = (x - x0) / w
    if z >= 0:
        ez = math.exp(-z)
        return ez / (1.0 + ez)
    ez = math.exp(z)
    return 1.0 / (1.0 + ez)


def logistic_midpoint_slope(width: float) -> float:
    """Exact derivative f'(chi_t)=-1/(4w)."""
    w = _finite("width", width)
    if w == 0:
        raise ValueError("width must be non-zero")
    return -1.0 / (4.0 * w)


def invariant_transfer_constant_coeff(
    invariant_intensity_0: float,
    invariant_emissivity: float,
    invariant_absorption: float,
    affine_length: float,
) -> float:
    """Exact constant-coefficient solution of dI/dlambda=E-A*I."""
    i0 = _finite("invariant_intensity_0", invariant_intensity_0)
    emissivity = _finite("invariant_emissivity", invariant_emissivity)
    absorption = _finite("invariant_absorption", invariant_absorption)
    length = _finite("affine_length", affine_length)
    if i0 < 0 or emissivity < 0 or absorption < 0 or length < 0:
        raise ValueError("transfer inputs must be non-negative")
    if absorption == 0:
        return i0 + emissivity * length
    attenuation = math.exp(-absorption * length)
    return i0 * attenuation + (emissivity / absorption) * (1.0 - attenuation)


def adiabatic_radiation_energy_density(u0: float, volume0: float, volume1: float) -> float:
    """For isotropic adiabatic radiation p=u/3: u*V^(4/3)=const."""
    u = _finite("u0", u0)
    v0 = _finite("volume0", volume0)
    v1 = _finite("volume1", volume1)
    if u < 0 or v0 <= 0 or v1 <= 0:
        raise ValueError("u0 must be >=0 and volumes >0")
    return u * (v0 / v1) ** (4.0 / 3.0)


def adiabatic_radiation_temperature(t0: float, volume0: float, volume1: float) -> float:
    """If additionally u=a*T^4: T*V^(1/3)=const."""
    t = _finite("t0", t0)
    v0 = _finite("volume0", volume0)
    v1 = _finite("volume1", volume1)
    if t < 0 or v0 <= 0 or v1 <= 0:
        raise ValueError("t0 must be >=0 and volumes >0")
    return t * (v0 / v1) ** (1.0 / 3.0)


def photon_energy_ev(frequency_hz: float) -> float:
    frequency = _finite("frequency_hz", frequency_hz)
    if frequency <= 0:
        raise ValueError("frequency_hz must be positive")
    return H_PLANCK * frequency / E_CHARGE


def electron_plasma_angular_frequency(electron_density_m3: float) -> float:
    density = _finite("electron_density_m3", electron_density_m3)
    if density < 0:
        raise ValueError("electron_density_m3 must be non-negative")
    return math.sqrt(density * E_CHARGE**2 / (EPSILON_0 * M_E))


def electron_cyclotron_angular_frequency(magnetic_field_t: float) -> float:
    field = _finite("magnetic_field_t", magnetic_field_t)
    return abs(E_CHARGE * field / M_E)


def epistemic_contract() -> dict[str, object]:
    return {
        "claim_allowed": False,
        "status": "IMPLEMENTED_UNTESTED_UNTIL_CI",
        "baseline_models": [
            "ideal_GRMHD",
            "resistive_GRMHD",
            "two_temperature_GRRMHD",
            "GRPIC",
            "general_relativistic_radiative_transfer",
        ],
        "exclusive_RLL_observable": "TOKEN_VAZIO",
        "calibrated_transport_solution": "TOKEN_VAZIO",
        "falsifier": (
            "reject added diagnostics if they provide no out-of-sample predictive "
            "gain beyond standard compression, Mach, GRMHD/GRPIC and GRRT baselines"
        ),
    }
