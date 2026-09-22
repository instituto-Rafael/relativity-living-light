#!/usr/bin/env python3
import cmath, json, math

def gate(name, ok, observed, expected):
    return {"gate":name,"status":"PASS" if ok else "FAIL","observed":observed,"expected":expected}

def oriented_area(a,b,c):
    return 0.5*((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))

def discriminant_for_unit_line_circle(R,d):
    return 4*(R*R-d*d)

def run():
    out=[]
    a=(0.0,0.0); b=(2.0,0.0); c=(0.0,3.0)
    A=oriented_area(a,b,c)
    Ar=oriented_area(a,c,b)
    out.append(gate("SG01_oriented_area_sign", A == -Ar and A > 0 and Ar < 0, [A,Ar], "orientation reversal changes sign only"))
    out.append(gate("SG02_metric_area_preserved", abs(A)==abs(Ar), [abs(A),abs(Ar)], "same metric area"))

    ds=[3.0,5.0,7.0]; R=5.0
    deltas=[discriminant_for_unit_line_circle(R,d) for d in ds]
    out.append(gate("SG03_discriminant_geometry", deltas[0]>0 and deltas[1]==0 and deltas[2]<0, deltas, ["secant","tangent","no real cut"]))

    # complex branch for t^2+1=0
    roots=[cmath.sqrt(-1),-cmath.sqrt(-1)]
    out.append(gate("SG04_complex_branch_retained", all(abs(z.real)<1e-15 and abs(abs(z.imag)-1)<1e-15 for z in roots), [str(z) for z in roots], ["+i","-i"]))

    examples=[(7,7),(70,100),(700,100),(142857,7)]
    qr=[]
    ok=True
    for N,base in examples:
        q,r=divmod(N,base)
        qr.append([N,base,q,r,q*base+r])
        ok &= (q*base+r==N and 0<=r<base)
    out.append(gate("SG05_quotient_remainder_reversible",ok,qr,"N=q*b+r"))

    collision=(7%7)==(14%7) and 7!=14
    out.append(gate("SG06_modulo_alone_is_lossy",collision,[7%7,14%7],"same residue may encode different integers"))

    # base-7: 7_10 = 10_7
    q,r=divmod(7,7)
    out.append(gate("SG07_base7_position",q==1 and r==0,[q,r],"7_10 = [1,0]_7; zero is a positional coefficient"))

    passed=sum(g["status"]=="PASS" for g in out)
    return {
      "verifier":"signed_geometry_positional_ledger_v1",
      "claim_allowed":False,
      "summary":{"total":len(out),"pass":passed,"fail":len(out)-passed},
      "gates":out,
      "boundaries":[
        "negative_oriented_area != negative_physical_area",
        "complex_root != real_intersection",
        "zero_digit != TOKEN_VAZIO",
        "modulo_only != reversible_state"
      ]
    }

if __name__=="__main__":
    p=run()
    print(json.dumps(p,indent=2,ensure_ascii=False))
    raise SystemExit(0 if p["summary"]["fail"]==0 else 1)
