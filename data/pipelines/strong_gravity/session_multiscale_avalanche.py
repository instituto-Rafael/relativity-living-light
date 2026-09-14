"""Finite multiscale session synthesis for the RLL strong-gravity branch."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import itertools, json, math
from typing import Sequence

FUNDAMENTAL_HZ = 144_000.0
SECOND_HARMONIC_HZ = 288_000.0
SPIRAL_SHRINK = math.sqrt(3.0) / 2.0
SPIRAL_DELTA_PHI_RAD = math.pi / 3.0
PLANCK_EV_S = 4.135667696e-15
MEV_TO_EV = 1.0e-3
LIGHT_MATTER_MODES_MEV = (3.2, 5.1)

@dataclass(frozen=True)
class DampingPartition:
    coherent_remaining_j_m3: float
    heat_j_m3: float
    transported_j_m3: float
    radiated_j_m3: float
    conservation_error_j_m3: float

@dataclass(frozen=True)
class Candidate:
    frequency_hz: float
    magnetization_regime: str
    thermal_regime: str
    carbon_regime: str
    flow_regime: str
    admissible: bool
    reason: str
    observables: tuple[str, ...]
    claim_allowed: bool = False

@dataclass(frozen=True)
class AvalancheReport:
    candidates_total: int
    candidates_admissible: int
    candidates_blocked: int
    digest_sha256: str
    claim_allowed: bool
    candidates: tuple[Candidate, ...]

def photon_energy_ev(frequency_hz: float) -> float:
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive")
    return PLANCK_EV_S * frequency_hz

def mode_frequency_hz(energy_mev: float) -> float:
    if energy_mev <= 0:
        raise ValueError("energy_mev must be positive")
    return (energy_mev * MEV_TO_EV) / PLANCK_EV_S

def ordered_infall_step(radius_m: float, phi_rad: float, *, shrink: float = SPIRAL_SHRINK,
                        delta_phi_rad: float = SPIRAL_DELTA_PHI_RAD) -> tuple[float, float]:
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    if not (0.0 < shrink <= 1.0):
        raise ValueError("shrink must be in (0, 1]")
    return radius_m * shrink, phi_rad + delta_phi_rad

def damping_partition(coherent_energy_j_m3: float, damping_rate_s_inv: float, dt_s: float,
                      *, transport_fraction: float, radiation_fraction: float) -> DampingPartition:
    if coherent_energy_j_m3 < 0 or damping_rate_s_inv < 0 or dt_s < 0:
        raise ValueError("energy, damping rate and dt must be non-negative")
    if transport_fraction < 0 or radiation_fraction < 0:
        raise ValueError("fractions must be non-negative")
    if transport_fraction + radiation_fraction > 1.0:
        raise ValueError("transport+radiation fractions cannot exceed one")
    remaining = coherent_energy_j_m3 * math.exp(-2.0 * damping_rate_s_inv * dt_s)
    lost = coherent_energy_j_m3 - remaining
    transported = lost * transport_fraction
    radiated = lost * radiation_fraction
    heat = lost - transported - radiated
    error = coherent_energy_j_m3 - (remaining + heat + transported + radiated)
    return DampingPartition(remaining, heat, transported, radiated, error)

def avalanche_multiplier(reduced_field_td: float, threshold_td: float, townsend_alpha_m_inv: float,
                         path_length_m: float, *, cap: float = 1.0e12) -> float:
    if min(reduced_field_td, threshold_td, townsend_alpha_m_inv, path_length_m) < 0:
        raise ValueError("avalanche inputs must be non-negative")
    if cap < 1.0:
        raise ValueError("cap must be >= 1")
    if reduced_field_td < threshold_td or townsend_alpha_m_inv == 0 or path_length_m == 0:
        return 1.0
    return math.exp(min(math.log(cap), townsend_alpha_m_inv * path_length_m))

def carbon_phase_admissible(carbon_regime: str, thermal_regime: str) -> tuple[bool, str]:
    if carbon_regime == "diamond_sp3" and thermal_regime in {"fully_ionized", "pair_plasma"}:
        return False, "diamond bonding is unavailable in a fully ionized or pair plasma"
    if carbon_regime == "compact_co_crystal":
        return False, "requires a degenerate-matter equation of state outside this bridge"
    if carbon_regime == "recondensing_carbon" and thermal_regime not in {"cooling", "quench"}:
        return False, "recondensation requires cooling or quench"
    return True, "admissible as a bounded candidate, not validated"

def finite_permutation_grid() -> tuple[Candidate, ...]:
    frequencies = (FUNDAMENTAL_HZ, SECOND_HARMONIC_HZ)
    magnetization = ("collision_dominated", "transition", "magnetized")
    thermal = ("heating", "cooling", "quench", "fully_ionized")
    carbon = ("carbonaceous_condensed", "diamond_sp3", "recondensing_carbon", "compact_co_crystal")
    flow = ("ordered_mean_plus_turbulence", "shock_spiral", "magnetic_reconnection")
    candidates = []
    for f, m, t, c, flow_regime in itertools.product(frequencies, magnetization, thermal, carbon, flow):
        admissible, reason = carbon_phase_admissible(c, t)
        if flow_regime == "magnetic_reconnection" and m == "collision_dominated":
            admissible = False
            reason = "reconnection candidate requires transition or magnetized transport"
        candidates.append(Candidate(
            f, m, t, c, flow_regime, admissible, reason,
            ("voltage_v","current_a","phase_vi_rad","electron_temperature_k",
             "electron_density_m3","magnetic_field_t","spectrum_power")
        ))
    return tuple(candidates)

def canonical_digest(candidates: Sequence[Candidate]) -> str:
    payload = [asdict(c) for c in candidates]
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def build_report() -> AvalancheReport:
    candidates = finite_permutation_grid()
    admitted = sum(c.admissible for c in candidates)
    return AvalancheReport(len(candidates), admitted, len(candidates)-admitted,
                           canonical_digest(candidates), False, candidates)

def baseline() -> dict:
    partition = damping_partition(10.0, 2.0, 0.1, transport_fraction=.20, radiation_fraction=.15)
    report = build_report()
    return {
      "schema":"rll.session_multiscale_avalanche.baseline.v1",
      "frequency_pair_hz":[FUNDAMENTAL_HZ,SECOND_HARMONIC_HZ],
      "photon_energy_ev":{"144_khz":photon_energy_ev(FUNDAMENTAL_HZ),
                          "288_khz":photon_energy_ev(SECOND_HARMONIC_HZ)},
      "light_matter_modes_hz":{str(x):mode_frequency_hz(x) for x in LIGHT_MATTER_MODES_MEV},
      "spiral":{"shrink":SPIRAL_SHRINK,"delta_phi_rad":SPIRAL_DELTA_PHI_RAD,
                "step_from_1m":ordered_infall_step(1.0,0.0)},
      "damping_partition":asdict(partition),
      "avalanche_examples":{"below_threshold":avalanche_multiplier(40,50,100,.01),
                            "above_threshold":avalanche_multiplier(60,50,100,.01)},
      "permutation_report":{"candidates_total":report.candidates_total,
                            "candidates_admissible":report.candidates_admissible,
                            "candidates_blocked":report.candidates_blocked,
                            "digest_sha256":report.digest_sha256},
      "boundaries":{"grmhd_solution":False,"plasma_kinetic_solution":False,
                    "carbon_eos_solution":False,"laboratory_validation":False,
                    "astrophysical_validation":False,"rll_cosmology_validation":False,
                    "claim_allowed":False}
    }

if __name__ == "__main__":
    print(json.dumps(baseline(), indent=2, sort_keys=True))
