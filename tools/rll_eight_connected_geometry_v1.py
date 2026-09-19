#!/usr/bin/env python3
"""Exact/bounded geometry helpers for the RLL eight-connected fold model."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from functools import reduce
from pathlib import Path
from typing import Iterable


def equilateral_height(side: float) -> float:
    return side * math.sqrt(3.0) / 2.0


def square_slots(radius: float = 1.0):
    out=[]
    for q in range(4):
        a=q*math.pi/2
        b=(q+1)*math.pi/2
        v=(radius*math.cos(a),radius*math.sin(a))
        vn=(radius*math.cos(b),radius*math.sin(b))
        m=((v[0]+vn[0])/2,(v[1]+vn[1])/2)
        out.append({"q":q,"class":"VERTEX","xy":v})
        out.append({"q":q,"class":"EDGE_MIDPOINT","xy":m})
    return out


def d4_action(q: int, action: str, k: int = 0) -> int:
    q%=4; k%=4
    if action=="rotation":
        return (q+k)%4
    if action=="reflection":
        return (k-q)%4
    raise ValueError("action must be rotation or reflection")


def all_d4_slot_permutations():
    slots=[(q,c) for q in range(4) for c in ("V","M")]
    actions=[]
    for action in ("rotation","reflection"):
        for k in range(4):
            perm=tuple((d4_action(q,action,k),c) for q,c in slots)
            actions.append((action,k,perm))
    return actions


def hexagram_vertices(R: float = 1.0):
    up=[math.pi/2 + k*2*math.pi/3 for k in range(3)]
    down=[math.pi/6 + k*2*math.pi/3 for k in range(3)]
    cv=lambda a:(R*math.cos(a),R*math.sin(a))
    return {"up":[cv(a) for a in up],"down":[cv(a) for a in down]}


def hexagram_central_hex_side(R: float = 1.0) -> float:
    return R/math.sqrt(3.0)


def torus_point(R: float, r: float, u: float, v: float):
    return (
        (R+r*math.cos(v))*math.cos(u),
        (R+r*math.cos(v))*math.sin(u),
        r*math.sin(v),
    )


def torus_frame(u: float, v: float):
    eu=(-math.sin(u),math.cos(u),0.0)
    ev=(-math.sin(v)*math.cos(u),-math.sin(v)*math.sin(u),math.cos(v))
    n=(math.cos(v)*math.cos(u),math.cos(v)*math.sin(u),math.sin(v))
    return eu,ev,n


def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a): return math.sqrt(dot(a,a))


def sphere_project(x, radius: float):
    n=norm(x)
    if n==0:
        raise ValueError("cannot radially project zero vector")
    return tuple(radius*v/n for v in x)


def sphere_geodesic(p,q,radius: float):
    c=max(-1.0,min(1.0,dot(p,q)/(radius*radius)))
    return radius*math.acos(c)


def householder_reflect(x, unit_normal):
    nn=norm(unit_normal)
    if not math.isclose(nn,1.0,rel_tol=1e-12,abs_tol=1e-12):
        unit_normal=tuple(v/nn for v in unit_normal)
    k=2*dot(x,unit_normal)
    return tuple(xi-k*ni for xi,ni in zip(x,unit_normal))


def quadratic_roots(a: float,b: float,c: float):
    if a==0:
        raise ValueError("a must be nonzero")
    d=b*b-4*a*c
    if d<0:
        return ()
    s=math.sqrt(d)
    return ((-b-s)/(2*a),(-b+s)/(2*a))


def mouth_crossings(a: float,b: float,c: float,target_radius: float):
    return quadratic_roots(a,b,c-target_radius)


def modular_phase(n: int,m: int) -> Fraction:
    if m<=0:
        raise ValueError("modulus must be positive")
    return Fraction(n % m,m)


def lcmm(values: Iterable[int]) -> int:
    vals=list(values)
    if not vals:
        raise ValueError("empty values")
    def lcm(a,b): return abs(a*b)//math.gcd(a,b)
    return reduce(lcm,vals,1)


def modular_phase_groups(n: int, modules: Iterable[int]):
    groups={}
    for m in modules:
        p=modular_phase(n,m)
        groups.setdefault(str(p),[]).append(m)
    return {k:v for k,v in groups.items() if len(v)>=2}


def negative_base_encode(n: int, base: int):
    if base>-2:
        raise ValueError("base must be <= -2")
    if n==0:
        return [0]
    digits=[]
    b=base
    while n!=0:
        n,rem=divmod(n,b)
        if rem<0:
            n+=1
            rem-=b
        digits.append(rem)
    return digits[::-1]


def negative_base_decode(digits, base: int):
    if base>-2:
        raise ValueError("base must be <= -2")
    n=0
    for d in digits:
        n=n*base+d
    return n


def summary():
    mods=[1,2,3,5,7,10,14,35,50,70]
    v=math.pi/6
    R,r=3.0,1.0
    p=torus_point(R,r,0.0,v)
    return {
      "claim_allowed":False,
      "eight_slots":square_slots(),
      "d4_unique_actions":len({x[2] for x in all_d4_slot_permutations()}),
      "hexagram":{"central_hex_side_R1":hexagram_central_hex_side(1.0)},
      "torus_30deg":{"point_R3_r1_u0":p,"radial_offset":r*math.cos(v),"z_offset":r*math.sin(v)},
      "angles":{"tan15":math.tan(math.pi/12),"two_minus_sqrt3":2-math.sqrt(3)},
      "modular":{"modules":mods,"sync_period":lcmm(mods),"phase_groups_at_70":modular_phase_groups(70,mods)},
      "boundaries":["ROTATED_SQUARE != HEXAGRAM","RADIAL_PROJECTION != ISOMETRY","8_TO_42 = TOKEN_VAZIO"]
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    args=ap.parse_args()
    payload=json.dumps(summary(),indent=2,sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload+"\n",encoding="utf-8")
    else:
        print(payload)


if __name__=="__main__":
    main()
