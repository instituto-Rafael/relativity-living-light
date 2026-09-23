import yaml
from pathlib import Path
from tools.validate_rll_geometric_operator_omega_g import validate

P=Path("data/contracts/rll_geometric_operator_omega_g.v1.yaml")

def load():
    return yaml.safe_load(P.read_text(encoding="utf-8"))

def test_contract_valid_and_claim_blocked():
    r=validate(load())
    assert r["valid"], r["errors"]
    assert r["claim_allowed"] is False

def test_canonical_math_authority_is_external():
    d=load()
    assert d["canonical_math_source"]["repository"]=="rafaelmeloreisnovo/Matem-tica-"

def test_direct_likelihood_binding_is_blocked():
    d=load()
    assert d["rll_binding"]["direct_likelihood_binding"] is False

def test_binding_gate_requires_scientific_fields():
    d=load()
    fields=set(d["rll_binding"]["binding_fields"])
    assert {"mechanism","units","covariance","falsifier","provenance"} <= fields

def test_omega_g_is_distinct_from_operational_omega():
    d=load()
    assert "data/omega_operational/rll_omega7_operational.json" in d["identity"]["distinct_from"]

def test_scientific_claim_remains_blocked():
    assert load()["gates"]["scientific_claim"]=="BLOCKED"
