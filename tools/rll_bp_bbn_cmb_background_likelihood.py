#!/usr/bin/env python3
"""BBN+CMB published-summary likelihood for the positive RLL B/P background profile.

Scope:
- canonical physical B/P profile: Omega_B0, Omega_P0 >= 0 and rho ~ a^-4;
- map the combined background density to Delta N_eff relative to photons;
- multiply independent Gaussian published summaries for BBN and ACT DR6 CMB;
- impose the physical flat prior Delta N_eff >= 0 and report the truncated
  posterior upper limit.

This is a direct likelihood evaluation of the declared *background-equivalent
profile using published posterior summaries*. It is NOT a replay of raw BBN
abundance likelihoods, ACT spectra, PMF perturbations or plasma perturbations.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from statistics import NormalDist

N_EFF_SM = 3.044
OMEGA_GAMMA_H2 = 2.4728e-5
RADIATION_FACTOR = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0)

DEFAULT_CONSTRAINTS = (
    ("PDG_BBN", 2.898, 0.141, "BBN_LIGHT_ELEMENT_SUMMARY"),
    ("ACT_DR6_CMB", 2.86, 0.13, "CMB_EXTENDED_MODEL_SUMMARY"),
)


@dataclass(frozen=True)
class GaussianConstraint:
    source: str
    neff_mean: float
    neff_sigma: float
    role: str


def constraints() -> list[GaussianConstraint]:
    return [GaussianConstraint(*row) for row in DEFAULT_CONSTRAINTS]


def delta_neff_from_omega_bp_h2(omega_bp_h2: float, omega_gamma_h2: float = OMEGA_GAMMA_H2) -> float:
    if not math.isfinite(omega_bp_h2) or omega_bp_h2 < 0.0:
        raise ValueError("physical B/P omega h^2 must be finite and non-negative")
    if not math.isfinite(omega_gamma_h2) or omega_gamma_h2 <= 0.0:
        raise ValueError("omega_gamma_h2 must be positive and finite")
    return omega_bp_h2 / (RADIATION_FACTOR * omega_gamma_h2)


def omega_bp_h2_from_delta_neff(delta_neff: float, omega_gamma_h2: float = OMEGA_GAMMA_H2) -> float:
    if not math.isfinite(delta_neff) or delta_neff < 0.0:
        raise ValueError("physical extra radiation Delta N_eff must be finite and non-negative")
    return RADIATION_FACTOR * omega_gamma_h2 * delta_neff


def gaussian_loglike(delta_neff: float, row: GaussianConstraint) -> float:
    if delta_neff < 0.0:
        return -math.inf
    model = N_EFF_SM + delta_neff
    residual = (model - row.neff_mean) / row.neff_sigma
    return -0.5 * residual * residual - math.log(row.neff_sigma * math.sqrt(2.0 * math.pi))


def combined_untruncated_gaussian(rows: list[GaussianConstraint] | None = None) -> tuple[float, float]:
    use = rows or constraints()
    precision = sum(1.0 / (row.neff_sigma * row.neff_sigma) for row in use)
    mean_delta = sum((row.neff_mean - N_EFF_SM) / (row.neff_sigma * row.neff_sigma) for row in use) / precision
    sigma_delta = math.sqrt(1.0 / precision)
    return mean_delta, sigma_delta


def truncated_upper_delta(confidence: float = 0.95, rows: list[GaussianConstraint] | None = None) -> float:
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0,1)")
    mean, sigma = combined_untruncated_gaussian(rows)
    normal = NormalDist()
    lower_cdf = normal.cdf((0.0 - mean) / sigma)
    target = lower_cdf + confidence * (1.0 - lower_cdf)
    return mean + sigma * normal.inv_cdf(target)


def likelihood_receipt(confidence: float = 0.95) -> dict:
    rows = constraints()
    mean, sigma = combined_untruncated_gaussian(rows)
    delta_upper = truncated_upper_delta(confidence, rows)
    omega_upper = omega_bp_h2_from_delta_neff(delta_upper)
    null_loglike = sum(gaussian_loglike(0.0, row) for row in rows)
    upper_loglike = sum(gaussian_loglike(delta_upper, row) for row in rows)
    return {
        "schema": "rll.bp_bbn_cmb_background_likelihood.receipt.v1",
        "scope": "RLL_BP_POSITIVE_BACKGROUND_A_MINUS_4_PROFILE",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "likelihood_kind": "PRODUCT_OF_INDEPENDENT_PUBLISHED_GAUSSIAN_SUMMARIES",
        "raw_likelihood_replay": False,
        "constraints": [asdict(row) for row in rows],
        "model": "N_eff = 3.044 + DeltaN_eff_BP; DeltaN_eff_BP >= 0",
        "combined_untruncated_delta_neff_mean": mean,
        "combined_untruncated_delta_neff_sigma": sigma,
        "physical_MAP_delta_neff": 0.0 if mean < 0.0 else mean,
        "posterior_prior": "FLAT_DELTA_NEFF_GE_0",
        "credible_level": confidence,
        "delta_neff_upper": delta_upper,
        "omega_BP_h2_upper": omega_upper,
        "Omega_BP_upper_examples": {
            "H0_50": omega_upper / 0.5**2,
            "H0_67p4": omega_upper / 0.674**2,
            "H0_90": omega_upper / 0.9**2
        },
        "combined_loglike_at_physical_MAP": null_loglike,
        "combined_loglike_at_upper_limit": upper_loglike,
        "background_profile_verdict": "PASS_BOUND_DERIVED_FROM_PUBLISHED_BBN_CMB_SUMMARIES",
        "full_PMF_plasma_perturbative_CMB_verdict": "TOKEN_VAZIO",
        "guards": [
            "BBN and ACT summary constraints are treated as independent Gaussian summaries.",
            "This does not replay raw light-element abundances or ACT spectra.",
            "This background mapping cannot substitute for PMF anisotropic stress/Faraday/heating or plasma perturbation microphysics.",
            "No RLL model-preference or Bayes-factor claim is authorized."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confidence", type=float, default=0.95)
    args = parser.parse_args()
    print(json.dumps(likelihood_receipt(args.confidence), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
