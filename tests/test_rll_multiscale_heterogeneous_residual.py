import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rll_multiscale_heterogeneous_residual.py"

spec = importlib.util.spec_from_file_location("rll_multiscale_heterogeneous_residual", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _fixture(*, ordered=True, grouping=True):
    rows = [
        {"id":"A-01","group":"A","value":0.4,"prediction":0.5,"uncertainty":0.1},
        {"id":"A-02","group":"A","value":0.6,"prediction":0.5,"uncertainty":0.1,
         "residual_class":"DELTA_MEASUREMENT"},
        {"id":"B-01","group":"B","value":2.4,"prediction":1.5,"uncertainty":0.2,
         "residual_class":"DELTA_MODEL"},
        {"id":"B-02","group":"B","value":2.6,"prediction":1.5,"uncertainty":0.2},
        {"id":"B-03","group":"B","value":2.5,"prediction":1.5,"uncertainty":0.2},
    ]
    if not grouping:
        rows[0].pop("group")
    return {
        "schema": mod.INPUT_SCHEMA,
        "ordered": ordered,
        "critical_value": 1.96,
        "records": rows,
    }


def test_population_and_sample_variance_are_distinct():
    out = mod.evaluate(_fixture())
    g = out["global_distribution"]
    assert g["sample_variance"] > g["population_variance"]


def test_within_between_sse_closes_exactly_within_tolerance():
    out = mod.evaluate(_fixture())
    h = out["heterogeneity"]
    assert h["closure_pass"] is True
    assert math.isclose(
        h["total_sse"],
        h["within_sse"] + h["between_sse"],
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
    assert h["between_group_fraction"] > 0.9


def test_unclassified_residual_is_preserved_not_zero_filled():
    out = mod.evaluate(_fixture())
    budget = out["residual_budget"]
    assert budget["unclassified_sse"] > 0
    assert budget["partition_closure_pass"] is True


def test_fibonacci_windows_are_diagnostic_not_likelihood_weights():
    out = mod.evaluate(_fixture())
    multi = out["multiscale"]
    assert multi["weights_likelihood"] is False
    assert [x["size"] for x in multi["scales"]] == [2, 3, 5]


def test_missing_grouping_stays_token_vazio():
    out = mod.evaluate(_fixture(grouping=False))
    assert out["heterogeneity"]["state"] == "TOKEN_VAZIO_GROUPING"


def test_unordered_data_does_not_get_fibonacci_windows():
    out = mod.evaluate(_fixture(ordered=False))
    assert out["multiscale"]["state"] == "TOKEN_VAZIO_ORDERING"
    assert out["multiscale"]["weights_likelihood"] is False


def test_missing_uncertainty_is_not_replaced_by_zero():
    doc = _fixture()
    doc["records"][0].pop("uncertainty")
    out = mod.evaluate(doc)
    assert out["global_distribution"]["variance_of_mean_state"] == "TOKEN_VAZIO_UNCERTAINTY"
    assert out["records"][0]["standardized_residual"]["state"] == "TOKEN_VAZIO_UNCERTAINTY"


def test_claim_gate_stays_false():
    out = mod.evaluate(_fixture())
    assert out["claim_allowed"] is False
