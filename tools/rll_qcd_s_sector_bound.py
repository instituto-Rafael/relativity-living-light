#!/usr/bin/env python3
"""Conservative primordial expansion bound for the canonical RLL s-sector.

Scope is intentionally narrow: only Omega_s0 * g(z). Radiation-like RLL terms
Omega_B0 and Omega_P0 are not set to zero by inference; therefore the full-RLL
primordial verdict remains TOKEN_VAZIO until those terms are independently bound.

The canonical RLL transition is g(z)=f(z)+(1-f(z))(1+z)^3 with logistic f in
[0,1]. For z>=0, g(z) <= (1+z)^3. Hence

  rho_s/rho_rad <= Omega_s0 / [Omega_rad (1+z)].

For an intentionally conservative upper envelope we further use:
- Omega_rad >= Omega_gamma;
- a rounded-down photon density floor Omega_gamma h^2 >= 2.46e-5;
- entropy mapping 1+z=(T/T0)(g_s(T)/g_s0)^(1/3), with a floor
  g_s(T)/g_s0 >= 1 in the QCD-temperature interval.

These choices maximize the allowed s-sector contribution and avoid pretending
that a lattice-QCD numerical table has already been ingested.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass

K_B_EV_PER_K = 8.617333262145e-5
DEFAULT_T0_K = 2.725
DEFAULT_OMEGA_GAMMA_H2_FLOOR = 2.46e-5
DEFAULT_OMEGA_S0_UL95 = 0.0017772301590821408
DEFAULT_H0_MAX = 90.0
DEFAULT_T_MIN_MEV = 130.0
DEFAULT_T_MAX_MEV = 400.0
DEFAULT_GS_RATIO_FLOOR = 1.0


@dataclass(frozen=True)
class BoundResult:
    temperature_MeV: float
    one_plus_z_floor: float
    omega_gamma_floor: float
    rho_s_over_radiation_upper: float
    delta_h_over_h_upper: float


def t0_mev(t0_k: float = DEFAULT_T0_K) -> float:
    if not math.isfinite(t0_k) or t0_k <= 0.0:
        raise ValueError("T0 must be positive and finite")
    return t0_k * K_B_EV_PER_K / 1.0e6


def one_plus_z_entropy_floor(
    temperature_mev: float,
    *,
    t0_k: float = DEFAULT_T0_K,
    gs_ratio_floor: float = DEFAULT_GS_RATIO_FLOOR,
) -> float:
    if not math.isfinite(temperature_mev) or temperature_mev <= 0.0:
        raise ValueError("temperature must be positive and finite")
    if not math.isfinite(gs_ratio_floor) or gs_ratio_floor < 1.0:
        raise ValueError("conservative entropy floor requires g_s(T)/g_s0 >= 1")
    return (temperature_mev / t0_mev(t0_k)) * gs_ratio_floor ** (1.0 / 3.0)


def omega_gamma_floor(
    h0_km_s_mpc: float,
    *,
    omega_gamma_h2_floor: float = DEFAULT_OMEGA_GAMMA_H2_FLOOR,
) -> float:
    if not math.isfinite(h0_km_s_mpc) or h0_km_s_mpc <= 0.0:
        raise ValueError("H0 must be positive and finite")
    if not math.isfinite(omega_gamma_h2_floor) or omega_gamma_h2_floor <= 0.0:
        raise ValueError("Omega_gamma h^2 floor must be positive and finite")
    h = h0_km_s_mpc / 100.0
    return omega_gamma_h2_floor / (h * h)


def rll_g_upper_bound(z: float) -> float:
    if not math.isfinite(z) or z < 0.0:
        raise ValueError("z must be finite and non-negative")
    return (1.0 + z) ** 3


def s_sector_fraction_upper_bound(
    omega_s0_ul: float,
    omega_radiation_floor: float,
    one_plus_z: float,
) -> float:
    if not (math.isfinite(omega_s0_ul) and omega_s0_ul >= 0.0):
        raise ValueError("Omega_s0 upper limit must be finite and non-negative")
    if not (math.isfinite(omega_radiation_floor) and omega_radiation_floor > 0.0):
        raise ValueError("radiation floor must be positive and finite")
    if not (math.isfinite(one_plus_z) and one_plus_z >= 1.0):
        raise ValueError("1+z must be finite and >= 1")
    return omega_s0_ul / (omega_radiation_floor * one_plus_z)


def delta_h_from_fraction_upper(x: float) -> float:
    if not math.isfinite(x) or x < 0.0:
        raise ValueError("fraction must be finite and non-negative")
    return x / (math.sqrt(1.0 + x) + 1.0)


def evaluate_bound(
    temperature_mev: float,
    *,
    omega_s0_ul: float = DEFAULT_OMEGA_S0_UL95,
    h0_km_s_mpc: float = DEFAULT_H0_MAX,
    t0_k: float = DEFAULT_T0_K,
    gs_ratio_floor: float = DEFAULT_GS_RATIO_FLOOR,
    omega_gamma_h2_floor: float = DEFAULT_OMEGA_GAMMA_H2_FLOOR,
) -> BoundResult:
    zp1 = one_plus_z_entropy_floor(
        temperature_mev, t0_k=t0_k, gs_ratio_floor=gs_ratio_floor
    )
    omega_g = omega_gamma_floor(
        h0_km_s_mpc, omega_gamma_h2_floor=omega_gamma_h2_floor
    )
    fraction = s_sector_fraction_upper_bound(omega_s0_ul, omega_g, zp1)
    return BoundResult(
        temperature_MeV=float(temperature_mev),
        one_plus_z_floor=zp1,
        omega_gamma_floor=omega_g,
        rho_s_over_radiation_upper=fraction,
        delta_h_over_h_upper=delta_h_from_fraction_upper(fraction),
    )


def bbn_neff_expansion_proxy(
    *,
    nnu_central: float = 2.898,
    nnu_sigma: float = 0.141,
    nnu_standard: float = 3.044,
    sigma_multiplier: float = 1.96,
) -> float:
    """Derived BBN-era comparison proxy, not a universal QCD-era H bound."""
    nnu_hi = nnu_central + sigma_multiplier * nnu_sigma
    g_std = 5.5 + 7.0 * nnu_standard / 4.0
    g_hi = 5.5 + 7.0 * nnu_hi / 4.0
    if g_hi <= 0.0 or g_std <= 0.0:
        raise ValueError("invalid effective degrees of freedom")
    return math.sqrt(g_hi / g_std) - 1.0


def build_receipt(args: argparse.Namespace) -> dict[str, object]:
    low = evaluate_bound(
        args.t_min_mev,
        omega_s0_ul=args.omega_s0_ul,
        h0_km_s_mpc=args.h0_max,
        t0_k=args.t0_k,
        gs_ratio_floor=args.gs_ratio_floor,
        omega_gamma_h2_floor=args.omega_gamma_h2_floor,
    )
    high = evaluate_bound(
        args.t_max_mev,
        omega_s0_ul=args.omega_s0_ul,
        h0_km_s_mpc=args.h0_max,
        t0_k=args.t0_k,
        gs_ratio_floor=args.gs_ratio_floor,
        omega_gamma_h2_floor=args.omega_gamma_h2_floor,
    )
    worst = max((low, high), key=lambda row: row.delta_h_over_h_upper)
    proxy = bbn_neff_expansion_proxy()
    separation = proxy / worst.delta_h_over_h_upper if worst.delta_h_over_h_upper else math.inf
    return {
        "schema": "rll.qcd_s_sector_bound.receipt.v1",
        "scope": "RLL_S_SECTOR_ONLY",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "method": "CONSERVATIVE_ANALYTIC_UPPER_BOUND",
        "inputs": {
            "omega_s0_ul95": args.omega_s0_ul,
            "H0_max_km_s_Mpc": args.h0_max,
            "T0_K": args.t0_k,
            "T_interval_MeV": [args.t_min_mev, args.t_max_mev],
            "g_s_over_g_s0_floor": args.gs_ratio_floor,
            "Omega_gamma_h2_floor": args.omega_gamma_h2_floor,
        },
        "proof_contract": [
            "0<=f(z)<=1 and z>=0 imply g_RLL(z)<= (1+z)^3",
            "Omega_radiation >= Omega_gamma",
            "g_s(T)/g_s0 >= 1 over declared QCD interval",
            "therefore rho_s/rho_r <= Omega_s0/[Omega_gamma(1+z)]",
        ],
        "endpoints": [asdict(low), asdict(high)],
        "worst_case": asdict(worst),
        "bbn_neff_expansion_proxy_95": proxy,
        "proxy_role": "COMPARISON_ONLY_NOT_QCD_LIKELIHOOD",
        "separation_factor_vs_bbn_proxy": separation,
        "separation_orders_log10": math.log10(separation),
        "s_sector_verdict": "PASS_LIMITED_DERIVED_BOUND" if worst.delta_h_over_h_upper < proxy else "FALSIFIED_PROXY_ONLY",
        "full_rll_verdict": "TOKEN_VAZIO",
        "full_rll_gaps": [
            "Omega_B0_primordial_bound",
            "Omega_P0_primordial_bound",
            "post_rng_fix_MCMC_reference_receipt",
        ],
        "forbidden_inference": "This bound does not confirm RLL and does not improve a Bayes factor.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--omega-s0-ul", type=float, default=DEFAULT_OMEGA_S0_UL95)
    parser.add_argument("--h0-max", type=float, default=DEFAULT_H0_MAX)
    parser.add_argument("--t0-k", type=float, default=DEFAULT_T0_K)
    parser.add_argument("--t-min-mev", type=float, default=DEFAULT_T_MIN_MEV)
    parser.add_argument("--t-max-mev", type=float, default=DEFAULT_T_MAX_MEV)
    parser.add_argument("--gs-ratio-floor", type=float, default=DEFAULT_GS_RATIO_FLOOR)
    parser.add_argument("--omega-gamma-h2-floor", type=float, default=DEFAULT_OMEGA_GAMMA_H2_FLOOR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.t_min_mev <= 0.0 or args.t_max_mev < args.t_min_mev:
        raise SystemExit("invalid temperature interval")
    print(json.dumps(build_receipt(args), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
