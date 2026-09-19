from __future__ import annotations
import importlib.util
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"tools"/"rll_eight_connected_geometry_v1.py"
SPEC=importlib.util.spec_from_file_location("g8",P)
g=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name]=g
SPEC.loader.exec_module(g)


def close(a,b,t=1e-12):
    return math.isclose(a,b,rel_tol=t,abs_tol=t)


def test_equilateral_exact_ratio_numeric():
    assert close(g.equilateral_height(1.0),math.sqrt(3)/2)


def test_square_has_eight_slots_and_d4_has_eight_actions():
    assert len(g.square_slots())==8
    assert len({x[2] for x in g.all_d4_slot_permutations()})==8


def test_edge_midpoint_radius():
    slots=g.square_slots(1.0)
    mids=[x for x in slots if x["class"]=="EDGE_MIDPOINT"]
    assert all(close(math.hypot(*x["xy"]),1/math.sqrt(2)) for x in mids)


def test_hexagram_center_hex_ratio():
    assert close(g.hexagram_central_hex_side(1.0),1/math.sqrt(3))


def test_torus_30_degree_offsets():
    R,r=3.0,2.0
    x,y,z=g.torus_point(R,r,0.0,math.pi/6)
    assert close(x,R+r*math.sqrt(3)/2)
    assert close(y,0.0)
    assert close(z,r/2)


def test_torus_frame_orthonormal():
    eu,ev,n=g.torus_frame(0.7,0.4)
    for x in (eu,ev,n):
        assert close(g.norm(x),1.0)
    assert close(g.dot(eu,ev),0.0)
    assert close(g.dot(eu,n),0.0)
    assert close(g.dot(ev,n),0.0)


def test_sphere_geodesic_quarter_circle():
    R=2.0
    p=(R,0,0); q=(0,R,0)
    assert close(g.sphere_geodesic(p,q,R),R*math.pi/2)


def test_householder_reflection():
    y=g.householder_reflect((1,2,3),(1,0,0))
    assert all(close(a,b) for a,b in zip(y,(-1,2,3)))


def test_quadratic_mouth():
    roots=g.mouth_crossings(1,0,0,1)
    assert len(roots)==2
    assert close(roots[0],-1)
    assert close(roots[1],1)


def test_modular_full_sync_period():
    mods=[1,2,3,5,7,10,14,35,50,70]
    assert g.lcmm(mods)==1050
    assert all(g.modular_phase(1050,m)==0 for m in mods)
    assert not all(g.modular_phase(70,m)==0 for m in mods)


def test_15_degree_identity():
    assert close(math.tan(math.pi/12),2-math.sqrt(3))


def test_negative_base_roundtrip():
    for n in range(-100,101):
        d=g.negative_base_encode(n,-2)
        assert g.negative_base_decode(d,-2)==n
