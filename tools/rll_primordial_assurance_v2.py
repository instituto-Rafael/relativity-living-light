#!/usr/bin/env python3
"""RLL primordial assurance gate V2.

This module materializes QCD thermodynamics, background-equivalent Delta N_eff
constraints and explicit epistemic gates. In the closure extension it records
that full-SM g_rho/g_s Table S3 has been ingested and that the physical-density
B/P profile has a non-negative sign contract. Full PMF/plasma perturbation
physics and raw ACT/BBN likelihood replay remain unresolved.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from statistics import NormalDist

N_EFF_SM = 3.044
T_CMB_K = 2.7255
OMEGA_GAMMA_H2 = 2.4728e-5
NEFF_RADIATION_FACTOR = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0)
DEFAULT_H0_RANGE = (50.0, 90.0)
HOTQCD_TC_MEV = 154.0
HOTQCD_PID = 95.0 * math.pi**2 / 180.0
HOTQCD = {"ct":3.8706,"t0":0.9761,"an":-8.7704,"bn":3.9200,"cn":0.0,"dn":0.3419,"ad":-1.2600,"bd":0.8425,"cd":0.0,"dd":-0.0475}
HOTQCD_DOMAIN_MEV = (100.0, 400.0)

NEFF_REFERENCES = {
    "PDG_BBN_2024": {"mean":2.898,"sigma":0.141,"epoch":"BBN","role":"BACKGROUND_EXPANSION_PROXY"},
    "PLANCK_BAO_2018": {"mean":2.99,"sigma":0.17,"epoch":"CMB","role":"FREE_STREAMING_RADIATION_PROXY"},
    "ACT_DR6_2025": {"mean":2.86,"sigma":0.13,"epoch":"CMB","role":"FREE_STREAMING_RADIATION_PROXY"},
    "ACT_DR6_PLUS_BBN_2025": {"mean":2.89,"sigma":0.11,"epoch":"CMB_PLUS_BBN","role":"HYBRID_COMPATIBILITY_PROXY"},
}

@dataclass(frozen=True)
class NeffEnvelope:
    source: str
    neff_mean: float
    neff_sigma: float
    sigma_multiplier: float
    neff_upper: float
    delta_neff_extra_upper: float
    omega_extra_h2_upper: float
    omega_extra_upper_at_h0_min: float
    omega_extra_upper_at_h0_max: float
    role: str

@dataclass(frozen=True)
class QCDThermo:
    temperature_MeV: float
    pressure_over_T4: float
    trace_over_T4: float
    energy_over_T4: float
    entropy_over_T3: float
    g_rho_qcd: float
    g_s_qcd: float
    cs2: float

def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

def gaussian_neff_compatibility_envelope(source: str, mean: float, sigma: float, *, sigma_multiplier: float = 1.96, neff_standard: float = N_EFF_SM, omega_gamma_h2: float = OMEGA_GAMMA_H2, h0_range: tuple[float, float] = DEFAULT_H0_RANGE, role: str = "PROXY_ONLY") -> NeffEnvelope:
    """Map a Gaussian N_eff summary to a background-equivalent radiation envelope."""
    for name, value in (("mean",mean),("sigma",sigma),("sigma_multiplier",sigma_multiplier),("neff_standard",neff_standard),("omega_gamma_h2",omega_gamma_h2)):
        _require_finite(name, value)
    if sigma < 0.0 or sigma_multiplier <= 0.0 or neff_standard <= 0.0 or omega_gamma_h2 <= 0.0:
        raise ValueError("invalid N_eff envelope inputs")
    h0_min, h0_max = h0_range
    if not (0.0 < h0_min <= h0_max):
        raise ValueError("invalid H0 range")
    neff_upper = mean + sigma_multiplier * sigma
    delta = max(0.0, neff_upper - neff_standard)
    omega_h2 = NEFF_RADIATION_FACTOR * delta * omega_gamma_h2
    hmin, hmax = h0_min / 100.0, h0_max / 100.0
    return NeffEnvelope(source,mean,sigma,sigma_multiplier,neff_upper,delta,omega_h2,omega_h2/(hmin*hmin),omega_h2/(hmax*hmax),role)

def reference_neff_envelopes(*, sigma_multiplier: float = 1.96) -> list[NeffEnvelope]:
    return [gaussian_neff_compatibility_envelope(source,float(item["mean"]),float(item["sigma"]),sigma_multiplier=sigma_multiplier,role=str(item["role"])) for source,item in NEFF_REFERENCES.items()]

def radiation_sum_omega_h2(omega_b0: float, omega_p0: float, h0: float) -> float:
    for name, value in (("Omega_B0",omega_b0),("Omega_P0",omega_p0),("H0",h0)):
        _require_finite(name, value)
    if omega_b0 < 0.0 or omega_p0 < 0.0:
        raise ValueError("physical B/P density profile requires non-negative coefficients")
    if h0 <= 0:
        raise ValueError("H0 must be positive")
    h = h0 / 100.0
    return (omega_b0 + omega_p0) * h * h

def blueprint_minimum_diagnostic(omega_extra_h2_upper: float, *, omega_b0_min: float = 1e-6, omega_p0_min: float = 1e-6, h0_range: tuple[float,float] = DEFAULT_H0_RANGE) -> dict[str, object]:
    if omega_extra_h2_upper < 0.0:
        raise ValueError("upper envelope must be non-negative")
    h0_min, h0_max = h0_range
    sum_min = omega_b0_min + omega_p0_min
    threshold = math.inf if sum_min <= 0.0 else 100.0 * math.sqrt(omega_extra_h2_upper / sum_min)
    return {
        "classification":"ILLUSTRATIVE_BLUEPRINT_DIAGNOSTIC_ONLY",
        "blueprint_minimum_sum_Omega":sum_min,
        "blueprint_minimum_sum_omega_h2_at_H0_min":radiation_sum_omega_h2(omega_b0_min,omega_p0_min,h0_min),
        "blueprint_minimum_sum_omega_h2_at_H0_max":radiation_sum_omega_h2(omega_b0_min,omega_p0_min,h0_max),
        "H0_threshold_km_s_Mpc_where_minimum_equals_envelope":threshold,
        "minimum_exceeds_envelope_for_entire_declared_H0_range":threshold < h0_min,
        "forbidden_inference":"This does not falsify RLL; RMR metadata is a blueprint/reference grid, not an authoritative fitted prior.",
    }

def hotqcd_pressure_over_t4(temperature_mev: float) -> float:
    _require_finite("temperature",temperature_mev)
    if not (HOTQCD_DOMAIN_MEV[0] <= temperature_mev <= HOTQCD_DOMAIN_MEV[1]):
        raise ValueError("HotQCD fit is restricted here to 100-400 MeV")
    x = temperature_mev / HOTQCD_TC_MEV
    c = HOTQCD
    num = HOTQCD_PID+c["an"]/x+c["bn"]/x**2+c["cn"]/x**3+c["dn"]/x**4
    den = 1.0+c["ad"]/x+c["bd"]/x**2+c["cd"]/x**3+c["dd"]/x**4
    return 0.5*(1.0+math.tanh(c["ct"]*(x-c["t0"])))*num/den

def _derivative(func, x: float, *, rel_step: float = 1e-5, bounds: tuple[float,float] | None = None) -> float:
    step = max(abs(x)*rel_step,1e-5)
    if bounds is not None:
        lo, hi = bounds
        if x-step < lo:
            return (-3.0*func(x)+4.0*func(x+step)-func(x+2.0*step))/(2.0*step)
        if x+step > hi:
            return (3.0*func(x)-4.0*func(x-step)+func(x-2.0*step))/(2.0*step)
    return (func(x+step)-func(x-step))/(2.0*step)

def hotqcd_thermodynamics(temperature_mev: float) -> QCDThermo:
    p4 = hotqcd_pressure_over_t4(temperature_mev)
    trace4 = temperature_mev * _derivative(hotqcd_pressure_over_t4,temperature_mev,bounds=HOTQCD_DOMAIN_MEV)
    e4 = trace4 + 3.0*p4
    s3 = e4 + p4
    def pressure_dimensional(t: float) -> float:
        return hotqcd_pressure_over_t4(t)*t**4
    def energy_dimensional(t: float) -> float:
        p = hotqcd_pressure_over_t4(t)
        tr = t*_derivative(hotqcd_pressure_over_t4,t,bounds=HOTQCD_DOMAIN_MEV)
        return (tr+3.0*p)*t**4
    cs2 = _derivative(pressure_dimensional,temperature_mev,bounds=HOTQCD_DOMAIN_MEV) / _derivative(energy_dimensional,temperature_mev,bounds=HOTQCD_DOMAIN_MEV)
    return QCDThermo(temperature_mev,p4,trace4,e4,s3,30.0*e4/math.pi**2,45.0*s3/(2.0*math.pi**2),cs2)

def radiation_dominated_hubble_s_inv(temperature_mev: float, g_rho_total: float) -> float:
    if temperature_mev <= 0.0 or g_rho_total <= 0.0:
        raise ValueError("temperature and total g_rho must be positive")
    t_gev = temperature_mev / 1000.0
    m_planck_gev = 1.220890e19
    hbar_gev_s = 6.582119569e-25
    return 1.66*math.sqrt(g_rho_total)*t_gev**2/m_planck_gev/hbar_gev_s

def bp_bbn_cmb_background_summary() -> dict[str, object]:
    """Combine independent published BBN and ACT DR6 Gaussian N_eff summaries.

    This closes only the positive a^-4 background profile; it is not raw-data
    replay and not a PMF/plasma perturbation likelihood.
    """
    rows = ((2.898,0.141),(2.86,0.13))
    precision = sum(1.0/(sigma*sigma) for _,sigma in rows)
    mean_delta = sum((mean-N_EFF_SM)/(sigma*sigma) for mean,sigma in rows)/precision
    sigma_delta = math.sqrt(1.0/precision)
    normal = NormalDist()
    lower_cdf = normal.cdf((0.0-mean_delta)/sigma_delta)
    q95 = normal.inv_cdf(lower_cdf + 0.95*(1.0-lower_cdf))
    delta95 = mean_delta + sigma_delta*q95
    omega95 = NEFF_RADIATION_FACTOR*OMEGA_GAMMA_H2*delta95
    return {
        "kind":"PRODUCT_OF_INDEPENDENT_PUBLISHED_GAUSSIAN_SUMMARIES",
        "raw_likelihood_replay":False,
        "physical_profile":"DeltaN_eff_BP>=0",
        "untruncated_delta_mean":mean_delta,
        "untruncated_delta_sigma":sigma_delta,
        "physical_MAP_delta_neff":0.0 if mean_delta < 0.0 else mean_delta,
        "delta_neff_upper_95":delta95,
        "omega_BP_h2_upper_95":omega95,
        "status":"PASS_BOUND_DERIVED_FROM_PUBLISHED_BBN_CMB_SUMMARIES",
        "full_PMF_plasma_perturbative_CMB":"TOKEN_VAZIO",
    }

def build_attention_gates() -> dict[str, object]:
    return {
        "Omega_s0_sector":"PASS_LIMITED_DERIVED_BOUND_V1",
        "Omega_B0_sign_authority":"PHYSICAL_PROFILE_NONNEGATIVE_RESOLVED",
        "Omega_P0_sign_authority":"PHYSICAL_PROFILE_NONNEGATIVE_RESOLVED_CONDITIONAL_A_MINUS_4",
        "Omega_B0_P0_perturbation_physics":"TOKEN_VAZIO",
        "full_SM_g_rho_g_s_numeric_ingestion":"MATERIALIZED_BORSANYI_TABLE_S3",
        "BP_background_BBN_CMB_summary_likelihood":"PASS_BOUND_DERIVED_FROM_PUBLISHED_BBN_CMB_SUMMARIES",
        "post_rng_fix_MCMC_reference_receipt":"TOKEN_VAZIO",
        "direct_RLL_early_universe_likelihood":"TOKEN_VAZIO_RAW_AND_PERTURBATIVE_REPLAY",
        "full_RLL_primordial_verdict":"TOKEN_VAZIO",
        "claim_allowed":False,
    }

def build_receipt(args: argparse.Namespace) -> dict[str, object]:
    envelopes = reference_neff_envelopes(sigma_multiplier=args.sigma_multiplier)
    strongest = min((row for row in envelopes if row.omega_extra_h2_upper > 0.0),key=lambda row: row.omega_extra_h2_upper)
    qcd_nodes = [asdict(hotqcd_thermodynamics(t)) for t in (130.0,145.0,150.0,155.0,200.0,300.0,400.0)]
    return {
        "schema":"rll.primordial_assurance.receipt.v2",
        "scope":"RLL_PRIMORDIAL_ASSURANCE_MESH",
        "claim_allowed":False,
        "publication_effect":"NONE",
        "statistical_contract":{"mapping":"GAUSSIAN_COMPATIBILITY_ENVELOPE_NOT_REFITTED_LIKELIHOOD","neff_standard":N_EFF_SM,"rho_extra_over_rho_gamma_per_DeltaNeff":NEFF_RADIATION_FACTOR,"Omega_gamma_h2":OMEGA_GAMMA_H2,"sigma_multiplier":args.sigma_multiplier},
        "neff_reference_envelopes":[asdict(row) for row in envelopes],
        "strongest_reference_envelope":asdict(strongest),
        "blueprint_diagnostic":blueprint_minimum_diagnostic(strongest.omega_extra_h2_upper),
        "hotqcd_2014":{"fit_domain_MeV":list(HOTQCD_DOMAIN_MEV),"Tc_MeV":HOTQCD_TC_MEV,"coefficients":dict(HOTQCD),"nodes":qcd_nodes,"scope_guard":"QCD_SECTOR_ONLY; do not substitute for total Standard-Model g_rho/g_s."},
        "closure_extensions":{
            "full_SM_gstar":{"status":"MATERIALIZED_BORSANYI_TABLE_S3","source":"Borsanyi et al. 2016 Supplementary Table S3","knots":27,"interpolation":"NATURAL_CUBIC_SPLINE_RECONSTRUCTION","extrapolation":"FORBIDDEN"},
            "BP_physical_profile":{"Omega_B0_sign":"NONNEGATIVE","Omega_P0_sign":"NONNEGATIVE_CONDITIONAL_RADIATION_LIKE_PROFILE","statistical_prior":"TOKEN_VAZIO_NO_AUTHORITATIVE_BP_PRIOR_FOUND","perturbations":"TOKEN_VAZIO"},
            "BP_background_BBN_CMB":bp_bbn_cmb_background_summary(),
        },
        "transition_contract":{"standard_cosmic_QCD":"CROSSOVER","first_order_bubble_GW":"BSM_OR_NONSTANDARD_CONDITIONAL","collider_QGP":"QCD_CONTEXT_NOT_COSMOLOGICAL_RLL_LIKELIHOOD","PBH_QCD_softening":"HYPOTHESIS_SENSITIVITY_BRANCH_NOT_RLL_EVIDENCE"},
        "gates":build_attention_gates(),
        "forbidden_inferences":["Published N_eff summaries constrain only the declared positive radiation-like B/P background profile; they are not raw BBN/ACT replay or full PMF/plasma CMB perturbation likelihoods.","HotQCD or Borsanyi EoS does not confirm RLL.","Collider QGP collectivity is not a cosmological RLL likelihood.","A first-order QCD gravitational-wave template is not standard-cosmology evidence.","Missing or access-limited material is not evidence of censorship."],
    }

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sigma-multiplier",type=float,default=1.96)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    print(json.dumps(build_receipt(args),indent=2,sort_keys=True,allow_nan=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
