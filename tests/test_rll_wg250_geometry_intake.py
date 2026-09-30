import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_WG250_GEOMETRY_INTAKE_V1.json"

def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))

def test_wg250_contract_count_and_boundary():
    c = load_contract()
    assert c["source_count"] == 250
    assert c["source_namespace"] == "WG250-0001..WG250-0250"
    assert c["claim_allowed"] is False
    assert c["mapping_to_mf_state"] == "TOKEN_VAZIO_ITEM_LEVEL_DEDUP"

def test_k8_count_and_distance_spectrum():
    assert math.comb(8, 2) == 28
    R = 3.0
    ds = [2*R*math.sin(k*math.pi/8) for k in range(1,5)]
    expected = [
        R*math.sqrt(2-math.sqrt(2)),
        R*math.sqrt(2),
        R*math.sqrt(2+math.sqrt(2)),
        2*R,
    ]
    for a,b in zip(ds, expected):
        assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12)
    assert math.isclose(ds[2]/ds[0],1+math.sqrt(2),rel_tol=0,abs_tol=1e-12)

def test_angle_grid_and_c3600():
    assert 30 == 2*15
    assert 45 == 3*15
    assert 60 == 4*15
    assert 90 == 6*15
    assert math.isclose(360/0.1,3600,rel_tol=0,abs_tol=1e-12)

def test_small_angle_geodesic_orders():
    R = 2.0
    theta = 1.0e-3
    s = R*theta
    chord = 2*R*math.sin(theta/2)
    sagitta = R*(1-math.cos(theta/2))
    cubic = R*theta**3/24
    quadratic = R*theta**2/8
    assert math.isclose(s-chord,cubic,rel_tol=1e-7,abs_tol=1e-18)
    assert math.isclose(sagitta,quadratic,rel_tol=1e-7,abs_tol=1e-18)

def test_spherical_equilateral_relation():
    sigma = math.pi/5
    A = math.acos(math.cos(sigma)/(1+math.cos(sigma)))
    excess = 3*A-math.pi
    assert A > math.pi/3
    assert excess > 0
