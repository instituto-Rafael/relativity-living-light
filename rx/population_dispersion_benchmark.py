"""Deterministic hidden-truth benchmark for the RLL population-dispersion layer."""
from __future__ import annotations

import math
import random


def _logpdf(x, mu, sigma):
    sigma = max(float(sigma), 1.0e-9)
    return (
        -0.5 * math.log(2.0 * math.pi * sigma * sigma)
        -0.5 * ((float(x) - float(mu)) / sigma) ** 2
    )


def _logsumexp2(a, b):
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


def _mean_sigma(values):
    if len(values) < 2:
        raise ValueError("at least two observations are required")
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / len(values)
    return mean, max(math.sqrt(var), 1.0e-6)


def _quantile(values, q):
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * float(q)))
    return ordered[idx]


def fit_one_gaussian(values):
    mu, sigma = _mean_sigma(values)
    loglike = sum(_logpdf(x, mu, sigma) for x in values)
    # mean + variance
    bic = 2.0 * math.log(len(values)) - 2.0 * loglike
    return {
        "model": "one_gaussian",
        "mu": mu,
        "sigma": sigma,
        "loglike": loglike,
        "parameter_count": 2,
        "bic": bic,
    }


def fit_two_gaussian_mixture(values, iterations=200):
    if len(values) < 10:
        raise ValueError("at least ten observations are required")
    mu1 = _quantile(values, 0.25)
    mu2 = _quantile(values, 0.75)
    _, pooled_sigma = _mean_sigma(values)
    sigma1 = pooled_sigma
    sigma2 = pooled_sigma
    weight = 0.5

    for _ in range(int(iterations)):
        resp = []
        for x in values:
            a = math.log(max(weight, 1.0e-9)) + _logpdf(x, mu1, sigma1)
            b = math.log(max(1.0 - weight, 1.0e-9)) + _logpdf(x, mu2, sigma2)
            denom = _logsumexp2(a, b)
            resp.append(math.exp(a - denom))

        sum_r = sum(resp)
        sum_1mr = len(values) - sum_r
        weight = min(max(sum_r / len(values), 1.0e-4), 1.0 - 1.0e-4)

        mu1 = sum(r * x for r, x in zip(resp, values)) / max(sum_r, 1.0e-9)
        mu2 = sum((1.0 - r) * x for r, x in zip(resp, values)) / max(sum_1mr, 1.0e-9)

        var1 = sum(r * (x - mu1) ** 2 for r, x in zip(resp, values)) / max(sum_r, 1.0e-9)
        var2 = sum((1.0 - r) * (x - mu2) ** 2 for r, x in zip(resp, values)) / max(sum_1mr, 1.0e-9)
        sigma1 = max(math.sqrt(var1), 1.0e-3)
        sigma2 = max(math.sqrt(var2), 1.0e-3)

    loglike = 0.0
    for x in values:
        a = math.log(weight) + _logpdf(x, mu1, sigma1)
        b = math.log(1.0 - weight) + _logpdf(x, mu2, sigma2)
        loglike += _logsumexp2(a, b)

    # weight + two means + two variances
    bic = 5.0 * math.log(len(values)) - 2.0 * loglike
    return {
        "model": "two_gaussian_mixture",
        "weight_1": weight,
        "mu_1": mu1,
        "sigma_1": sigma1,
        "mu_2": mu2,
        "sigma_2": sigma2,
        "loglike": loglike,
        "parameter_count": 5,
        "bic": bic,
    }


def generate_hidden_truth(case="mixture", seed=42, n=500):
    rng = random.Random(int(seed))
    values = []
    if case == "mixture":
        for _ in range(int(n)):
            if rng.random() < 0.60:
                values.append(rng.gauss(-2.0, 0.70))
            else:
                values.append(rng.gauss(2.0, 1.00))
    elif case == "null":
        values = [rng.gauss(0.0, 1.20) for _ in range(int(n))]
    else:
        raise ValueError("unsupported hidden-truth case: %s" % case)
    return values


def benchmark(case="mixture", seed=42, n=500):
    values = generate_hidden_truth(case=case, seed=seed, n=n)
    one = fit_one_gaussian(values)
    two = fit_two_gaussian_mixture(values)
    delta_bic_one_minus_two = one["bic"] - two["bic"]
    preferred = "two_gaussian_mixture" if delta_bic_one_minus_two > 0.0 else "one_gaussian"
    expected = "two_gaussian_mixture" if case == "mixture" else "one_gaussian"
    return {
        "schema": "rll.population_dispersion.hidden_truth_benchmark.v1",
        "case": case,
        "seed": int(seed),
        "n": int(n),
        "one_gaussian": one,
        "two_gaussian_mixture": two,
        "delta_bic_one_minus_two": delta_bic_one_minus_two,
        "preferred_by_bic": preferred,
        "expected": expected,
        "status": "PASS" if preferred == expected else "FAIL",
        "boundary": (
            "This synthetic benchmark demonstrates detectability/complexity control only. "
            "It does not establish an astrophysical population or an RLL deformation."
        ),
        "claim_allowed": False,
    }
