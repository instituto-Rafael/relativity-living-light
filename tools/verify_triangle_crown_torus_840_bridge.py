#!/usr/bin/env python3
import json, math
from fractions import Fraction
from functools import reduce

TOL=1e-12
pi=math.pi
sin=math.sin
cos=math.cos
sqrt=math.sqrt
gcd=math.gcd

def lcm(a,b): return abs(a*b)//gcd(a,b)
def lcm_many(xs): return reduce(lcm,xs,1)
def close(a,b): return abs(a-b) <= TOL*max(1.0,abs(a),abs(b))
def gate(name,observed,expected,ok,note=""):
    return {"gate":name,"status":"PASS" if ok else "FAIL",
            "observed":observed,"expected":expected,"note":note}

def run():
    out=[]
    R=5.0; r=1.0; a=1.0
    h=sqrt(3)/2

    out.append(gate("G01_equilateral_kernel",h*h,0.75,close(h*h,0.75)))

    v=pi/6
    local=[r*cos(v),r*sin(v)]
    expected=[h*r,0.5*r]
    out.append(gate("G02_torus_cross_section_30deg",local,expected,
                    close(local[0],expected[0]) and close(local[1],expected[1])))

    A_crown=pi*((R+r)**2-(R-r)**2)
    out.append(gate("G03_torus_projection_annulus_area",A_crown,4*pi*R*r,
                    close(A_crown,4*pi*R*r)))

    A_torus=4*pi*pi*R*r
    out.append(gate("G04_torus_surface_vs_projection",A_torus/A_crown,pi,
                    close(A_torus/A_crown,pi)))

    for n in (3,4,6,8):
        inner=a*cos(pi/n)
        fraction=pi*(a*a-inner*inner)/(pi*a*a)
        expected=sin(pi/n)**2
        out.append(gate(f"G05_polygon_sweep_n{n}",fraction,expected,close(fraction,expected)))

    for n in (3,4,6,8):
        A_ann=pi*a*a*sin(pi/n)**2
        V_shell=2*pi*R*A_ann
        V_torus=2*pi*pi*R*a*a
        expected=sin(pi/n)**2
        out.append(gate(f"G06_toroidal_shell_fraction_n{n}",
                        V_shell/V_torus,expected,close(V_shell/V_torus,expected)))

    A6=3*sqrt(3)*r*r/2
    ratio=(2*pi*R*A6)/(2*pi*pi*R*r*r)
    expected=3*sqrt(3)/(2*pi)
    out.append(gate("G07_hexagon_to_circular_torus_volume_ratio",
                    ratio,expected,close(ratio,expected)))

    m=math.tan(pi/6)
    b1=-m*R+r*sqrt(1+m*m)
    b2=-m*R-r*sqrt(1+m*m)
    distance=abs(b1-b2)/sqrt(1+m*m)
    out.append(gate("G08_parallel_tangent_separation",
                    distance,2*r,close(distance,2*r)))

    ri=0.25*r
    ro=r
    alpha=pi/3
    total=2*pi*pi*R*(ro*ro-ri*ri)
    volumes=[]
    for k in range(6):
        v0=k*pi/3
        V=(pi*R*alpha*(ro*ro-ri*ri)
           +(4*pi/3)*(ro**3-ri**3)*cos(v0)*sin(alpha/2))
        volumes.append(V)
    pairs=[volumes[k]+volumes[k+3] for k in range(3)]
    expected_pair=total/3
    out.append(gate("G09_six_sector_opposite_pair_closure",
                    pairs,[expected_pair]*3,
                    all(close(x,expected_pair) for x in pairs)))

    out.append(gate("G10_torus_30x45_period",
                    lcm_many([12,8]),24,lcm_many([12,8])==24))

    out.append(gate("G11_lcm_5_6_7_8",
                    lcm_many([5,6,7,8]),840,lcm_many([5,6,7,8])==840))

    rays=set()
    for n in (5,6,7,8):
        for k in range(n):
            rays.add(Fraction(k,n)%1)
    out.append(gate("G12_distinct_rays_5_6_7_8",len(rays),22,len(rays)==22))

    lines=set()
    half=Fraction(1,2)
    for n in (5,6,7,8):
        for k in range(n):
            lines.add(Fraction(k,n)%half)
    out.append(gate("G13_distinct_line_orientations_5_6_7_8",
                    len(lines),16,len(lines)==16))

    out.append(gate("G14_full_line_half_rays",
                    2*len(lines),32,2*len(lines)==32))

    out.append(gate("G15_lcm_24_10_42",
                    lcm_many([24,10,42]),840,lcm_many([24,10,42])==840))

    passed=sum(g["status"]=="PASS" for g in out)
    return {
        "verifier":"triangle_crown_torus_840_bridge_v1",
        "claim_allowed":False,
        "scope":"formal_geometry_and_finite_combinatorics_only",
        "parameters":{"R":R,"r":r,"a":a,"tol":TOL},
        "summary":{"total":len(out),"pass":passed,"fail":len(out)-passed},
        "gates":out,
        "boundaries":[
            "same_numeric_period_840 != same_semantics",
            "planar_hexagram != spherical_geodesic_hexagram",
            "sphere != torus",
            "formal_torus_geometry != physical_vortex"
        ]
    }

def main():
    payload=run()
    print(json.dumps(payload,indent=2,ensure_ascii=False))
    return 0 if payload["summary"]["fail"]==0 else 1

if __name__=="__main__":
    raise SystemExit(main())
