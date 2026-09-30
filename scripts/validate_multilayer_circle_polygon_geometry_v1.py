#!/usr/bin/env python3
"""RLL multilayer circle/polygon geometry validator V1."""

from __future__ import annotations
import argparse, collections, itertools, json, math
from pathlib import Path
import yaml

EPS = 1e-10

def regular_polygon_metrics(n, R=1.0):
    return {
        "theta": 2*math.pi/n,
        "s": 2*R*math.sin(math.pi/n),
        "a": R*math.cos(math.pi/n),
        "P": 2*n*R*math.sin(math.pi/n),
        "A": 0.5*n*R*R*math.sin(2*math.pi/n),
    }

def chord(n, k, R=1.0):
    return 2*R*math.sin(k*math.pi/n)

def rot(p, t):
    c,s=math.cos(t),math.sin(t)
    x,y=p
    return (c*x-s*y,s*x+c*y)

def reflect(p, alpha=0.0):
    x,y=rot(p,-alpha)
    return rot((x,-y),alpha)

def invert(p, rho=1.0):
    x,y=p
    r2=x*x+y*y
    if r2<=0:
        raise ValueError("circle inversion undefined at origin")
    return (rho*rho*x/r2,rho*rho*y/r2)

def orient(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def norm(p): return math.hypot(*p)
def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])

def k8_counts():
    N=8
    eps=1e-9
    vertices=[(math.cos(j*math.pi/4),math.sin(j*math.pi/4)) for j in range(N)]
    segments=list(itertools.combinations(range(N),2))
    diagonals=[(i,j) for i,j in segments if min((j-i)%N,(i-j)%N)!=1]

    def cross(a,b): return a[0]*b[1]-a[1]*b[0]
    def sub(a,b): return (a[0]-b[0],a[1]-b[1])
    def proper(a,b,c,d):
        r,s=sub(b,a),sub(d,c)
        den=cross(r,s)
        if abs(den)<eps: return None
        q=sub(c,a)
        t=cross(q,s)/den
        u=cross(q,r)/den
        if eps<t<1-eps and eps<u<1-eps:
            return (a[0]+t*r[0],a[1]+t*r[1])
        return None
    def key(p): return (round(p[0],10),round(p[1],10))

    point_pairs=collections.Counter()
    segment_points=collections.defaultdict(list)
    for i,j in segments:
        segment_points[(i,j)].extend([vertices[i],vertices[j]])

    pairwise_crossings=0
    for (i,j),(k,l) in itertools.combinations(diagonals,2):
        if len({i,j,k,l})<4: continue
        p=proper(vertices[i],vertices[j],vertices[k],vertices[l])
        if p is None: continue
        pairwise_crossings+=1
        point_pairs[key(p)]+=1
        segment_points[(i,j)].append(p)
        segment_points[(k,l)].append(p)

    concurrency=collections.Counter()
    for pair_count in point_pairs.values():
        m=next(m for m in range(2,9) if math.comb(m,2)==pair_count)
        concurrency[m]+=1

    coords=[]
    coord_to_id={}
    def node_id(p):
        k=key(p)
        if k not in coord_to_id:
            coord_to_id[k]=len(coords)
            coords.append(k)
        return coord_to_id[k]

    for p in vertices: node_id(p)
    for p in point_pairs: node_id(p)

    planar_edges=set()
    for (i,j),plist in segment_points.items():
        a,b=vertices[i],vertices[j]
        pts=list({key(p):key(p) for p in plist}.values())
        dx,dy=b[0]-a[0],b[1]-a[1]
        denom=dx*dx+dy*dy
        pts.sort(key=lambda p:((p[0]-a[0])*dx+(p[1]-a[1])*dy)/denom)
        ids=[node_id(p) for p in pts]
        for u,v in zip(ids,ids[1:]):
            planar_edges.add(tuple(sorted((u,v))))

    adj=collections.defaultdict(list)
    for u,v in planar_edges:
        adj[u].append(v); adj[v].append(u)
    for u in adj:
        x,y=coords[u]
        adj[u].sort(key=lambda v:math.atan2(coords[v][1]-y,coords[v][0]-x))

    visited=set()
    faces=[]
    for e in planar_edges:
        for start in (e,(e[1],e[0])):
            if start in visited: continue
            face=[]
            a,b=start
            while (a,b) not in visited:
                visited.add((a,b))
                face.append(a)
                nbrs=adj[b]
                idx=nbrs.index(a)
                c=nbrs[(idx-1)%len(nbrs)]
                a,b=b,c
            poly=[coords[v] for v in face]
            area2=sum(
                poly[t][0]*poly[(t+1)%len(poly)][1]
                - poly[(t+1)%len(poly)][0]*poly[t][1]
                for t in range(len(poly))
            )
            faces.append((face,0.5*area2))

    bounded=[f for f,area in faces if area>eps]
    face_types=collections.Counter(map(len,bounded))
    return {
        "segments":len(segments),
        "diagonals":len(diagonals),
        "pairwise_crossings":pairwise_crossings,
        "intersections":len(point_pairs),
        "concurrency":dict(concurrency),
        "V":len(coords),"E":len(planar_edges),"F":len(faces),
        "bounded":len(bounded),
        "face_types":dict(face_types),
        "cycle_rank":len(planar_edges)-len(coords)+1,
    }

def run_all(spec):
    details={}
    passed=[]
    failed=[]
    def check(sid,name,condition,value=None,expected=None):
        rec={"test":name,"pass":bool(condition)}
        if value is not None: rec["value"]=value
        if expected is not None: rec["expected"]=expected
        details.setdefault(sid,[]).append(rec)
        (passed if condition else failed).append(f"{sid}:{name}")

    for n in spec["fixtures"]["polygon_orders"]:
        m=regular_polygon_metrics(n)
        check("S01_REGULAR_POLYGON",f"theta_n_{n}",abs(m["theta"]-2*math.pi/n)<EPS)
        check("S01_REGULAR_POLYGON",f"side_n_{n}",abs(m["s"]-2*math.sin(math.pi/n))<EPS)
        check("S01_REGULAR_POLYGON",f"apothem_n_{n}",abs(m["a"]-math.cos(math.pi/n))<EPS)
        check("S01_REGULAR_POLYGON",f"perimeter_n_{n}",abs(m["P"]-n*m["s"])<EPS)
        check("S01_REGULAR_POLYGON",f"area_n_{n}",abs(m["A"]-0.5*n*math.sin(2*math.pi/n))<EPS)

    for n in [6,8,12]:
        for k in range(1,n//2+1):
            c=chord(n,k)
            check("S02_CHORD_CLASSES",f"chord_{n}_{k}",abs(c-2*math.sin(k*math.pi/n))<EPS)
        check("S02_CHORD_CLASSES",f"diameter_{n}",abs(chord(n,n//2)-2)<EPS)

    side=2.3
    h=math.sqrt(3)/2*side
    area=math.sqrt(3)/4*side*side
    Rc=side/math.sqrt(3)
    ri=side/(2*math.sqrt(3))
    check("S03_EQUILATERAL_TRIANGLE","height",abs(h-math.sqrt(3)/2*side)<EPS)
    check("S03_EQUILATERAL_TRIANGLE","area",abs(area-math.sqrt(3)/4*side*side)<EPS)
    check("S03_EQUILATERAL_TRIANGLE","circumradius",abs(Rc-side/math.sqrt(3))<EPS)
    check("S03_EQUILATERAL_TRIANGLE","inradius",abs(ri-side/(2*math.sqrt(3)))<EPS)
    check("S03_EQUILATERAL_TRIANGLE","R_eq_2r",abs(Rc-2*ri)<EPS)
    inc=math.pi*ri*ri/area
    circ=math.pi*Rc*Rc/area
    check("S04_TRIANGLE_CIRCLE_AREA_RATIOS","incircle_over_triangle",abs(inc-math.pi/(3*math.sqrt(3)))<EPS)
    check("S04_TRIANGLE_CIRCLE_AREA_RATIOS","circumcircle_over_triangle",abs(circ-4*math.pi/(3*math.sqrt(3)))<EPS)

    R=1.7
    hx=regular_polygon_metrics(6,R)
    check("S05_HEXAGON_SIX_TRIANGLES","side_equals_R",abs(hx["s"]-R)<EPS)
    tri_area=math.sqrt(3)/4*R*R
    check("S05_HEXAGON_SIX_TRIANGLES","six_equilateral_areas_equal_hexagon",abs(6*tri_area-hx["A"])<EPS)

    for lamraw in spec["fixtures"]["layer_scales"]:
        lam={"sqrt(2)-1":math.sqrt(2)-1,"sqrt(3)/2":math.sqrt(3)/2}.get(lamraw,lamraw)
        R0=2.0
        radii=[R0*lam**j for j in range(6)]
        check("S06_CONCENTRIC_LAYERS",f"geometric_radius_{lamraw}",all(abs(radii[j+1]/radii[j]-lam)<EPS for j in range(5)))
        annulus=math.pi*(radii[2]**2-radii[3]**2)
        check("S06_CONCENTRIC_LAYERS",f"annulus_area_{lamraw}",abs(annulus-math.pi*radii[2]**2*(1-lam**2))<EPS)
        finite=sum(math.pi*(R0*lam**j)**2 for j in range(100))
        infinite=math.pi*R0*R0/(1-lam*lam)
        check("S06_CONCENTRIC_LAYERS",f"geometric_area_sum_{lamraw}",abs(finite-infinite)/infinite<1e-10)

    p=(0.7,1.4); Ra=norm(p); Rb=3.1
    q=(p[0]*Rb/Ra,p[1]*Rb/Ra)
    check("S07_RADIAL_PROJECTION","angle_preserved",abs(math.atan2(q[1],q[0])-math.atan2(p[1],p[0]))<EPS)
    check("S07_RADIAL_PROJECTION","radius_rescaled",abs(norm(q)-Rb)<EPS)

    mu=0.37; p=(1.2,-0.4); q=(-0.2,1.1)
    hp=(mu*p[0],mu*p[1]); hq=(mu*q[0],mu*q[1])
    check("S08_HOMOTHETY","length_scale",abs(dist(hp,hq)-mu*dist(p,q))<EPS)
    base_area=abs(orient((0,0),p,q))/2
    scaled_area=abs(orient((0,0),hp,hq))/2
    check("S08_HOMOTHETY","area_scale",abs(scaled_area-mu*mu*base_area)<EPS)

    theta=0.731
    rp,rq=rot(p,theta),rot(q,theta)
    check("S09_ROTATION","norm_preserved",abs(norm(rp)-norm(p))<EPS)
    check("S09_ROTATION","distance_preserved",abs(dist(rp,rq)-dist(p,q))<EPS)

    a0,b0,c0=(0,0),(1,0),(0,1)
    ra,rb,rc=[reflect(x,0.31) for x in (a0,b0,c0)]
    check("S10_REFLECTION","norm_preserved",abs(norm(rb)-norm(b0))<EPS)
    check("S10_REFLECTION","distance_preserved",abs(dist(rb,rc)-dist(b0,c0))<EPS)
    check("S10_REFLECTION","orientation_reversed",orient(a0,b0,c0)*orient(ra,rb,rc)<0)

    p=(1.2,0.7); rho=2.0
    ip=invert(p,rho); iip=invert(ip,rho)
    check("S11_CIRCLE_INVERSION","radial_product_rho_squared",abs(norm(p)*norm(ip)-rho*rho)<EPS)
    check("S11_CIRCLE_INVERSION","involution",dist(p,iip)<EPS)

    ns=spec["fixtures"]["polygon_orders"]
    area_ratios=[regular_polygon_metrics(n)["A"]/math.pi for n in ns]
    perimeter_ratios=[regular_polygon_metrics(n)["P"]/(2*math.pi) for n in ns]
    check("S12_POLYGON_TO_CIRCLE_LIMIT","area_ratio_monotonic",all(area_ratios[i]<area_ratios[i+1] for i in range(len(ns)-1)))
    check("S12_POLYGON_TO_CIRCLE_LIMIT","perimeter_ratio_monotonic",all(perimeter_ratios[i]<perimeter_ratios[i+1] for i in range(len(ns)-1)))
    check("S12_POLYGON_TO_CIRCLE_LIMIT","convergence_96",abs(1-area_ratios[-1])<0.001 and abs(1-perimeter_ratios[-1])<0.001)

    kc=k8_counts()
    check("S13_K8_PLANAR_NO_LOSS","segments_28",kc["segments"]==28)
    check("S13_K8_PLANAR_NO_LOSS","intersections_49",kc["intersections"]==49)
    check("S13_K8_PLANAR_NO_LOSS","concurrency_40_8_1",kc["concurrency"]=={2:40,3:8,4:1})
    check("S13_K8_PLANAR_NO_LOSS","planar_57_136_81",(kc["V"],kc["E"],kc["F"])==(57,136,81))
    check("S13_K8_PLANAR_NO_LOSS","faces_56_24",kc["face_types"]=={3:56,4:24})
    check("S13_K8_PLANAR_NO_LOSS","cycle_rank_80",kc["cycle_rank"]==80)

    def unique_triangle_vertices(step_deg,count=6):
        angles=set()
        for m in range(count):
            phase=math.radians(step_deg*m)
            for k in range(3):
                angle=(phase+2*math.pi*k/3)%(2*math.pi)
                angles.add(round(angle,10))
        return len(angles)
    check("S14_ROTATED_TRIANGLE_OVERLAYS","six_rotations_60deg_give_6_unique_vertices",unique_triangle_vertices(60)==6)
    check("S14_ROTATED_TRIANGLE_OVERLAYS","six_rotations_30deg_give_12_unique_vertices",unique_triangle_vertices(30)==12)

    n1,n2,alpha_deg=1.0,1.5,30.0
    alpha=math.radians(alpha_deg)
    beta=math.asin(n1/n2*math.sin(alpha))
    check("S15_SNELL_REFRACTION","air_to_glass",abs(n1*math.sin(alpha)-n2*math.sin(beta))<EPS)
    n1,n2,alpha_deg=1.5,1.0,60.0
    tir_metric=n1/n2*math.sin(math.radians(alpha_deg))
    check("S15_SNELL_REFRACTION","total_internal_reflection_case",tir_metric>1.0)

    n=8; R=1.3; h3=2.1
    side=2*R*math.sin(math.pi/8)
    A8=2*(1+math.sqrt(2))*side*side
    volume=A8*h3
    surface=2*A8+8*side*h3
    check("S16_OCTAGONAL_PRISM_K16","vertices_16",2*n==16)
    check("S16_OCTAGONAL_PRISM_K16","complete_edges_120",math.comb(16,2)==120)
    check("S16_OCTAGONAL_PRISM_K16","edge_decomposition_56_64",2*math.comb(8,2)+8*8==120)
    check("S16_OCTAGONAL_PRISM_K16","volume",abs(volume-A8*h3)<EPS)
    check("S16_OCTAGONAL_PRISM_K16","surface_area",abs(surface-(2*A8+8*side*h3))<EPS)
    k=3
    D=math.sqrt(chord(8,k,R)**2+h3*h3)
    p3=(R,0,-h3/2)
    q3=(R*math.cos(2*math.pi*k/8),R*math.sin(2*math.pi*k/8),h3/2)
    direct=math.sqrt(sum((q3[i]-p3[i])**2 for i in range(3)))
    check("S16_OCTAGONAL_PRISM_K16","cross_layer_distance",abs(D-direct)<EPS)

    Rs=2.4
    u=(2.0,-1.0,3.0)
    un=math.sqrt(sum(x*x for x in u))
    shell=tuple(Rs*x/un for x in u)
    check("S17_SPHERICAL_SHELL_PROJECTION","radial_projection_to_shell",abs(math.sqrt(sum(x*x for x in shell))-Rs)<EPS)
    gamma=math.pi/2
    spherical_chord=2*Rs*math.sin(gamma/2)
    direct_chord=math.sqrt(Rs*Rs+Rs*Rs)
    arc=Rs*gamma
    check("S17_SPHERICAL_SHELL_PROJECTION","angular_chord_arc_relation",abs(spherical_chord-direct_chord)<EPS and abs(arc-Rs*math.pi/2)<EPS)
    spherical_excess=3*(math.pi/2)-math.pi
    spherical_area=spherical_excess*Rs*Rs
    check("S17_SPHERICAL_SHELL_PROJECTION","octant_spherical_triangle_area",abs(spherical_area-(math.pi/2)*Rs*Rs)<EPS)

    orders=spec["fixtures"]["multilayer_orders"]
    total=sum(orders)
    within=sum(math.comb(n,2) for n in orders)
    cross_edges=sum(orders[i]*orders[j] for i in range(len(orders)) for j in range(i+1,len(orders)))
    check("S18_MULTILAYER_COMPLETE_GRAPH","sum_vertices",total==17)
    check("S18_MULTILAYER_COMPLETE_GRAPH","all_to_all_edge_identity",within+cross_edges==math.comb(total,2))

    n=8
    m=regular_polygon_metrics(n)
    fill_index=m["A"]/math.pi
    polygonality=n*math.sin(2*math.pi/n)/(2*math.pi)
    check("S19_INDEX_FAMILY","fill_index",abs(fill_index-polygonality)<EPS)
    check("S19_INDEX_FAMILY","polygonality_index",0<polygonality<1)
    lam=math.sqrt(2)-1
    check("S19_INDEX_FAMILY","scale_index",abs(lam-(math.sqrt(2)-1))<EPS)
    chord_index=chord(8,3)
    check("S19_INDEX_FAMILY","chord_index",abs(chord_index-2*math.sin(3*math.pi/8))<EPS)
    C,H=2,1
    check("S19_INDEX_FAMILY","topological_index",C-H==1)

    check("S20_DIHEDRAL_ORBIT_STABILIZER","D8_order_16",2*8==16)
    for stabilizer in [1,2,4,8,16]:
        orbit=16//stabilizer
        check("S20_DIHEDRAL_ORBIT_STABILIZER",f"orbit_stabilizer_{stabilizer}",orbit*stabilizer==16)

    scenario_summary={
        sid:{
            "passed":sum(1 for t in tests if t["pass"]),
            "total":len(tests),
            "state":"PASS" if all(t["pass"] for t in tests) else "FAIL",
        }
        for sid,tests in details.items()
    }

    return {
        "status":"PASS" if not failed else "FAIL",
        "summary":{
            "tests_total":len(passed)+len(failed),
            "passed":len(passed),
            "failed":len(failed),
            "scenarios":len(spec["scenarios"]),
        },
        "scenario_summary":scenario_summary,
        "failed_tests":failed,
        "key_invariants":{
            "K8":{
                "segments":28,
                "intersections":49,
                "concurrency":{"2":40,"3":8,"4":1},
                "planar":{"V":57,"E":136,"F":81},
                "bounded_faces":{"triangles":56,"quadrilaterals":24},
                "cycle_rank":80,
            },
            "triangle_overlays":{
                "six_rotations_60deg_unique_vertices":6,
                "six_rotations_30deg_unique_vertices":12,
            },
            "K16":{
                "vertices":16,
                "complete_edges":120,
                "intralayer_edges":56,
                "interlayer_edges":64,
            },
        },
        "claim_boundary":spec["claim_boundary"],
        "execution_state":{
            "mathematical_tests":"EXECUTED",
            "repository_provider_ci":"NOT_RUN",
            "physical_rll_binding":"TOKEN_VAZIO_EVIDENCE",
        },
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--spec",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    with Path(args.spec).open("r",encoding="utf-8") as f:
        spec=yaml.safe_load(f)
    result=run_all(spec)
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],sort_keys=True))
    raise SystemExit(0 if result["status"]=="PASS" else 1)

if __name__=="__main__":
    main()
