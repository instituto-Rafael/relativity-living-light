#!/usr/bin/env python3
import json, math

TOL=1e-12

def close(a,b):
    return abs(a-b) <= TOL*max(1.0,abs(a),abs(b))

def tri_area(a,b,c):
    return abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2

def polygon_area(pts):
    return abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2)

def fan_area(pts):
    return sum(tri_area(pts[0],pts[i],pts[i+1]) for i in range(1,len(pts)-1))

def gate(name,ok,observed,expected):
    return {"gate":name,"status":"PASS" if ok else "FAIL","observed":observed,"expected":expected}

def run():
    out=[]

    p0=(0.0,0.0); p1=(2.0,0.0); p2=(0.0,3.0)
    l0,l1,l2=0.2,0.3,0.5
    x=(l0*p0[0]+l1*p1[0]+l2*p2[0],l0*p0[1]+l1*p1[1]+l2*p2[1])
    out.append(gate("TS01_barycentric_sum",close(l0+l1+l2,1.0),l0+l1+l2,1.0))
    out.append(gate("TS02_barycentric_reconstruction",close(x[0],0.6) and close(x[1],1.5),x,[0.6,1.5]))

    A=((2.0,1.0),(0.0,3.0)); t=(1.0,-2.0)
    def F(p):
        return (A[0][0]*p[0]+A[0][1]*p[1]+t[0],A[1][0]*p[0]+A[1][1]*p[1]+t[1])
    det=A[0][0]*A[1][1]-A[0][1]*A[1][0]
    src_area=tri_area(p0,p1,p2)
    dst_area=tri_area(F(p0),F(p1),F(p2))
    out.append(gate("TS03_affine_area_determinant",close(dst_area,abs(det)*src_area),dst_area,abs(det)*src_area))

    tri_checks=[]
    for n in (5,8):
        pts=[(math.cos(2*math.pi*k/n),math.sin(2*math.pi*k/n)) for k in range(n)]
        tri_checks.append({"n":n,"polygon":polygon_area(pts),"fan":fan_area(pts),"triangles":n-2})
    out.append(gate("TS04_polygon_triangulation_area",
                    all(close(x["polygon"],x["fan"]) for x in tri_checks),
                    tri_checks,"fan area equals polygon area; triangle count n-2"))

    a=2.0
    K=math.sqrt(3)*a*a/4
    s=3*a/2
    rin=K/s
    rcirc=a*a*a/(4*K)
    ok=close(rin,math.sqrt(3)*a/6) and close(rcirc,math.sqrt(3)*a/3) and close(rcirc,2*rin)
    out.append(gate("TS05_equilateral_incircle_circumcircle",ok,
                    {"rin":rin,"rcirc":rcirc,"ratio":rcirc/rin},
                    {"rin":math.sqrt(3)*a/6,"rcirc":math.sqrt(3)*a/3,"ratio":2.0}))

    q=0.5; m=12
    ratio=q**m
    out.append(gate("TS06_recursive_contraction",ratio < 1e-3,ratio,"diameter ratio tends to 0 for q<1"))

    passed=sum(g["status"]=="PASS" for g in out)
    return {
      "verifier":"triangle_simplex_embedding_v1",
      "claim_allowed":False,
      "summary":{"total":len(out),"pass":passed,"fail":len(out)-passed},
      "gates":out,
      "boundaries":[
        "triangle_area_alone != complete_geometry",
        "triangulation_exact_for_polygons_not_exact_finite_representation_of_arbitrary_curves",
        "mathematical_recursive_nesting != physical_infinity"
      ]
    }

if __name__=="__main__":
    payload=run()
    print(json.dumps(payload,indent=2,ensure_ascii=False))
    raise SystemExit(0 if payload["summary"]["fail"]==0 else 1)
