from rx.population_dispersion_benchmark import benchmark


def test_hidden_truth_mixture_survives_bic_penalty():
    out = benchmark(case="mixture", seed=42, n=500)
    assert out["status"] == "PASS"
    assert out["preferred_by_bic"] == "two_gaussian_mixture"
    assert out["delta_bic_one_minus_two"] > 10.0
    assert out["claim_allowed"] is False


def test_null_case_rejects_unneeded_extra_population():
    out = benchmark(case="null", seed=42, n=500)
    assert out["status"] == "PASS"
    assert out["preferred_by_bic"] == "one_gaussian"
    assert out["delta_bic_one_minus_two"] < 0.0
    assert out["claim_allowed"] is False
