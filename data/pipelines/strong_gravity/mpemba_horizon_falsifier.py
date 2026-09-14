"""Bounded black-hole thermodynamics / Mpemba-horizon falsification bridge.

Separates semiclassical analytic identities, supplied relaxation trajectories,
literature provenance, real observations, symbolic/internal hypotheses, and
protected TOKEN_VAZIO gaps. It is not a GRMHD solver and does not claim an
astrophysical Mpemba detection.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from typing import Sequence

C_M_S = 299_792_458.0
G_M3_KG_S2 = 6.67430e-11
HBAR_J_S = 1.054_571_817e-34
K_B_J_K = 1.380_649e-23
PI = math.pi
SOLAR_MASS_KG = 1.98847e30
TOKEN_VAZIO = "TOKEN_VAZIO"


def _finite_positive(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def schwarzschild_radius_m(mass_kg: float) -> float:
    mass_kg = _finite_positive("mass_kg", mass_kg)
    return 2.0 * G_M3_KG_S2 * mass_kg / C_M_S**2


def hawking_temperature_k(mass_kg: float) -> float:
    mass_kg = _finite_positive("mass_kg", mass_kg)
    return HBAR_J_S * C_M_S**3 / (8.0 * PI * G_M3_KG_S2 * K_B_J_K * mass_kg)


def bekenstein_hawking_entropy_j_k(mass_kg: float) -> float:
    mass_kg = _finite_positive("mass_kg", mass_kg)
    return 4.0 * PI * K_B_J_K * G_M3_KG_S2 * mass_kg**2 / (HBAR_J_S * C_M_S)


def schwarzschild_heat_capacity_j_k(mass_kg: float) -> float:
    """dE/dT_H in the Schwarzschild semiclassical model."""
    mass_kg = _finite_positive("mass_kg", mass_kg)
    return -8.0 * PI * G_M3_KG_S2 * K_B_J_K * mass_kg**2 / (HBAR_J_S * C_M_S)


def d_hawking_temperature_d_mass_k_kg(mass_kg: float) -> float:
    mass_kg = _finite_positive("mass_kg", mass_kg)
    return -hawking_temperature_k(mass_kg) / mass_kg


def static_redshift_factor(mass_kg: float, radius_m: float) -> float:
    """sqrt(1-r_s/r) for a static Schwarzschild observer; requires r > r_s."""
    mass_kg = _finite_positive("mass_kg", mass_kg)
    radius_m = _finite_positive("radius_m", radius_m)
    rs = schwarzschild_radius_m(mass_kg)
    if radius_m <= rs:
        raise ValueError("static Schwarzschild observer requires radius_m > r_s")
    return math.sqrt(1.0 - rs / radius_m)


def tolman_local_temperature_k(
    temperature_at_infinity_k: float, mass_kg: float, radius_m: float
) -> float:
    """Static-equilibrium Tolman temperature; not a free-fall thermometer."""
    temperature_at_infinity_k = _finite_positive(
        "temperature_at_infinity_k", temperature_at_infinity_k
    )
    return temperature_at_infinity_k / static_redshift_factor(mass_kg, radius_m)


def validate_relaxation_curve(
    times: Sequence[float], distances: Sequence[float]
) -> None:
    if len(times) != len(distances) or len(times) < 2:
        raise ValueError("times and distances must have equal length >= 2")
    if any(not math.isfinite(float(t)) for t in times):
        raise ValueError("times must be finite")
    if any(not math.isfinite(float(d)) or float(d) < 0.0 for d in distances):
        raise ValueError("distances must be finite and non-negative")
    if any(float(b) <= float(a) for a, b in zip(times, times[1:])):
        raise ValueError("times must be strictly increasing")


def first_passage_time(
    times: Sequence[float], distances: Sequence[float], epsilon: float
) -> float | None:
    validate_relaxation_curve(times, distances)
    if not math.isfinite(epsilon) or epsilon < 0.0:
        raise ValueError("epsilon must be finite and non-negative")
    for t, d in zip(times, distances):
        if float(d) <= epsilon:
            return float(t)
    return None


@dataclass(frozen=True)
class MpembaWitness:
    initial_farther: bool
    crossing_observed: bool
    tau_far: float | None
    tau_near: float | None
    faster_far_relaxation: bool
    witness: bool

    def to_dict(self) -> dict:
        return asdict(self)


def mpemba_witness(
    times: Sequence[float],
    far_distances: Sequence[float],
    near_distances: Sequence[float],
    epsilon: float,
) -> MpembaWitness:
    validate_relaxation_curve(times, far_distances)
    validate_relaxation_curve(times, near_distances)
    if len(far_distances) != len(near_distances):
        raise ValueError("far and near curves must have equal length")
    initial_farther = float(far_distances[0]) > float(near_distances[0])
    crossing_observed = any(
        float(f) < float(n)
        for f, n in zip(far_distances[1:], near_distances[1:])
    )
    tau_far = first_passage_time(times, far_distances, epsilon)
    tau_near = first_passage_time(times, near_distances, epsilon)
    faster = tau_far is not None and tau_near is not None and tau_far < tau_near
    return MpembaWitness(
        initial_farther,
        crossing_observed,
        tau_far,
        tau_near,
        faster,
        initial_farther and crossing_observed and faster,
    )


def slow_mode_suppression_ratio(
    far_slowest_mode_amplitude: float, near_slowest_mode_amplitude: float
) -> float:
    if not all(
        math.isfinite(float(x))
        for x in (far_slowest_mode_amplitude, near_slowest_mode_amplitude)
    ):
        raise ValueError("mode amplitudes must be finite")
    denom = abs(float(near_slowest_mode_amplitude))
    if denom == 0.0:
        raise ValueError("near slow-mode amplitude must be non-zero")
    return abs(float(far_slowest_mode_amplitude)) / denom


@dataclass(frozen=True)
class SymbolicBHBridgeGate:
    dimensional_map_declared: bool
    area_law_recovered: bool
    schwarzschild_first_law_recovered: bool
    observer_covariance_declared: bool
    no_posthoc_unit_adjustment: bool
    independent_prediction_declared: bool
    eligible_for_physical_equivalence_test: bool

    def to_dict(self) -> dict:
        return asdict(self)


def symbolic_bh_bridge_gate(
    *,
    dimensional_map_declared: bool,
    area_law_recovered: bool,
    schwarzschild_first_law_recovered: bool,
    observer_covariance_declared: bool,
    no_posthoc_unit_adjustment: bool,
    independent_prediction_declared: bool,
) -> SymbolicBHBridgeGate:
    """Gate symbolic/internal entropy/time mappings before physical equivalence.

    A numerical resemblance or shared symbol is insufficient. All requirements
    must be explicit before a RAFAELIA/Exacordex-like symbolic expression can be
    compared as a candidate physical map to black-hole thermodynamics.
    """
    checks = (
        bool(dimensional_map_declared),
        bool(area_law_recovered),
        bool(schwarzschild_first_law_recovered),
        bool(observer_covariance_declared),
        bool(no_posthoc_unit_adjustment),
        bool(independent_prediction_declared),
    )
    return SymbolicBHBridgeGate(*checks, eligible_for_physical_equivalence_test=all(checks))


def analytic_invariants(mass_kg: float) -> dict:
    mass_kg = _finite_positive("mass_kg", mass_kg)
    t = hawking_temperature_k(mass_kg)
    s = bekenstein_hawking_entropy_j_k(mass_kg)
    c_bh = schwarzschild_heat_capacity_j_k(mass_kg)
    dtdm = d_hawking_temperature_d_mass_k_kg(mass_kg)
    t_ratio = hawking_temperature_k(2.0 * mass_kg) / t
    s_ratio = bekenstein_hawking_entropy_j_k(2.0 * mass_kg) / s
    return {
        "mass_kg": mass_kg,
        "schwarzschild_radius_m": schwarzschild_radius_m(mass_kg),
        "hawking_temperature_k": t,
        "bekenstein_hawking_entropy_j_k": s,
        "heat_capacity_j_k": c_bh,
        "dT_dM_k_kg": dtdm,
        "mass_doubling_temperature_ratio": t_ratio,
        "mass_doubling_entropy_ratio": s_ratio,
        "checks": {
            "negative_heat_capacity": c_bh < 0.0,
            "temperature_decreases_with_mass": dtdm < 0.0,
            "T_inverse_mass_scaling": math.isclose(t_ratio, 0.5, rel_tol=1e-12),
            "S_mass_squared_scaling": math.isclose(s_ratio, 4.0, rel_tol=1e-12),
        },
    }


def claim_ledger(mpemba: MpembaWitness | None = None) -> list[dict]:
    astro_reason = (
        "No checksum-verified matched astrophysical relaxation trajectories with "
        "a preregistered distance functional and covariance are ingested by this module."
    )
    if mpemba is not None and mpemba.witness:
        astro_reason += (
            " A supplied trajectory can establish only a dataset-local witness; "
            "a synthetic/model trajectory is not an astrophysical detection."
        )
    return [
        {"id": "BH-MP-01", "claim": "Schwarzschild Hawking temperature scales as M^-1 and heat capacity is negative.", "state": "SUPPORTED_ANALYTIC_SEMICLASSICAL", "claim_allowed": True},
        {"id": "BH-MP-02", "claim": "A static near-horizon Tolman temperature is equivalent to a freely falling thermometer reading.", "state": "FALSIFIED_AS_EQUIVALENCE", "claim_allowed": False},
        {"id": "BH-MP-03", "claim": "Past, present and future literally coexist as one locally measured thermodynamic state at the horizon.", "state": "REJECT_LITERAL_CLAIM", "claim_allowed": False},
        {"id": "BH-MP-04", "claim": "Observed relativistic jets are matter emitted from inside the event horizon.", "state": "FALSIFIED_BY_CAUSAL_BOUNDARY", "claim_allowed": False},
        {"id": "BH-MP-05", "claim": "Magnetized exterior plasma and spin/flux extraction are physically relevant standard jet-launching candidates.", "state": "LITERATURE_OBSERVATION_SUPPORTED_BOUNDED", "claim_allowed": True},
        {"id": "BH-MP-06", "claim": "An astrophysical black hole has a directly observed Mpemba relaxation.", "state": TOKEN_VAZIO, "reason": astro_reason, "claim_allowed": False},
        {"id": "BH-MP-07", "claim": "Mpemba-like anomalous relaxation has rigorous relativistic-QFT/holographic precedents.", "state": "LITERATURE_SUPPORTED_THEORY", "claim_allowed": True},
        {"id": "BH-MP-08", "claim": "Hawking temperature has been directly measured for M87* or Sgr A*.", "state": TOKEN_VAZIO, "reason": "No direct astrophysical Hawking thermometry is registered.", "claim_allowed": False},
        {"id": "BH-MP-09", "claim": "Generic curved spacetime guarantees a single globally conserved scalar energy for the full system.", "state": "REJECT_OVERGENERALIZATION", "reason": "Use local covariant conservation and symmetry-dependent conserved quantities.", "claim_allowed": False},
        {"id": "BH-MP-10", "claim": "An internal RAFAELIA/Exacordex symbolic entropy expression is physically identical to Bekenstein-Hawking entropy without an explicit dimensional and covariant bridge.", "state": "REJECT_UNCALIBRATED_EQUIVALENCE", "reason": "Symbolic/numerical resemblance does not establish physical dimensions, the area law, the first law, covariance, or independent prediction.", "claim_allowed": False},
        {"id": "BH-MP-11", "claim": "A symbolic cyclic-time or direct/inverse operator by itself proves general-relativistic horizon-time structure or cosmology.", "state": "ANALOGY_ONLY_TOKEN_VAZIO_COVARIANT_DYNAMICS", "reason": "Requires an explicit metric/dynamics, observer-independent observables and falsifiable predictions against GR/cosmological nulls.", "claim_allowed": False},
    ]


def falsifier_matrix() -> list[dict]:
    return [
        {"id": "F-BH-MP-01", "target": "BH-MP-01", "test": "dT_H/dM < 0 and C_BH < 0 in the Schwarzschild semiclassical domain"},
        {"id": "F-BH-MP-02", "target": "BH-MP-02", "test": "static formulas reject r <= r_s and remain observer-specific"},
        {"id": "F-BH-MP-04", "target": "BH-MP-04", "test": "reject any descendant requiring causal transport from r < r_+ to infinity"},
        {"id": "F-BH-MP-06A", "target": "BH-MP-06", "test": "D_far(0)>D_near(0), crossing, and tau_far(epsilon)<tau_near(epsilon) on matched trajectories"},
        {"id": "F-BH-MP-06B", "target": "BH-MP-06", "test": "survive covariance, uncertainty, admissible distance-family, hold-out and look-elsewhere controls"},
        {"id": "F-BH-MP-07", "target": "BH-MP-07", "test": "holographic/Unruh/quantum sources remain theory-labelled"},
        {"id": "F-BH-MP-08", "target": "BH-MP-08", "test": "EHT synchrotron/plasma observables are never relabelled Hawking thermometry"},
        {"id": "F-BH-MP-10", "target": "BH-MP-10", "test": "require an explicit units/dimensions map, recovery of S_BH proportional to area, Schwarzschild dE=T_H dS, observer/covariance statement, no post-hoc unit adjustment, and an independent prediction before physical-equivalence testing"},
        {"id": "F-BH-MP-11", "target": "BH-MP-11", "test": "require explicit metric or covariant dynamics, operational observables, coordinate/observer treatment and quantitative comparison against GR/cosmological null models; numerology or cyclic symbolism alone fails"},
    ]


def baseline() -> dict:
    """Deterministic synthetic witness demonstrating the gate, not nature."""
    times = [0.0, 1.0, 2.0, 3.0, 4.0]
    far = [1.0, 0.50, 0.18, 0.06, 0.02]
    near = [0.70, 0.55, 0.40, 0.20, 0.05]
    witness = mpemba_witness(times, far, near, epsilon=0.10)
    analytic = analytic_invariants(10.0 * SOLAR_MASS_KG)
    analytic_pass = all(analytic["checks"].values())
    symbolic_gate = symbolic_bh_bridge_gate(
        dimensional_map_declared=False,
        area_law_recovered=False,
        schwarzschild_first_law_recovered=False,
        observer_covariance_declared=False,
        no_posthoc_unit_adjustment=False,
        independent_prediction_declared=False,
    )
    return {
        "schema": "rll.strong_gravity.mpemba_horizon_falsifier.v1",
        "evidence_grade": "SYNTHETIC_GATE_FIXTURE_PLUS_ANALYTIC_IDENTITIES",
        "analytic": analytic,
        "synthetic_relaxation": {
            "times": times,
            "far_distances": far,
            "near_distances": near,
            "epsilon": 0.10,
            "result": witness.to_dict(),
            "astrophysical_evidence": False,
        },
        "symbolic_drive_crosswalk": {
            "gate": symbolic_gate.to_dict(),
            "physical_equivalence_claim_allowed": False,
            "boundary": "Internal symbolic hypotheses remain auditable but cannot inherit black-hole-thermodynamics evidence without closing the dimensional/covariant bridge.",
        },
        "claim_ledger": claim_ledger(witness),
        "falsifiers": falsifier_matrix(),
        "decision": "BOUNDED_PASS" if analytic_pass and witness.witness and not symbolic_gate.eligible_for_physical_equivalence_test else "FAIL",
        "global_scientific_claim_allowed": False,
        "token_vazio": [
            "direct astrophysical Hawking temperature measurement",
            "matched M87*/Sgr A* Mpemba relaxation trajectories",
            "pre-registered astrophysical distance functional D[X(t),X_eq]",
            "checksum-verified EHT time-domain numeric ingest",
            "covariance-aware inference and independent reproduction",
            "dimensionally and covariantly closed RAFAELIA/Exacordex-to-Bekenstein-Hawking physical map",
            "covariant dynamical bridge from symbolic cyclic-time operators to GR/cosmological observables",
        ],
        "next": [
            "ingest public EHT time-resolved products with checksums/source metadata",
            "freeze observable/equilibrium/distance/epsilon before outcome inspection",
            "fit matched null and candidate relaxation models with covariance",
            "run dimensional/covariant falsifiers on internal symbolic black-hole mappings",
            "run every registered falsifier and quarantine failed descendants",
            "retain TOKEN_VAZIO until the relevant promotion gate closes",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(baseline(), indent=2, sort_keys=True))
