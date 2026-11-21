#!/usr/bin/env python3
"""RAFAELIA V2 — exact multibase/CRT and bounded octic-scale experiment.

The radix is NOT a congruence modulus; equality is checked through exact integer
values. All inputs are fixed synthetic mathematical fixtures. No external IO.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import reduce
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import os
import sys

RADICES = (7, 10, 14, 35, 50, 70)
VALUES = (7, 10, 14, 35, 50, 70, 350)
REFERENCE_VALUE = 350


def digits(n: int, base: int) -> tuple[int, ...]:
    if n < 0 or base < 2: raise ValueError("expect n>=0, base>=2")
    out=[]
    while n:
        n, d = divmod(n, base)
        out.append(d)
    return tuple(reversed(out)) if out else (0,)


def numeric_value(digits_: tuple[int,...], base: int) -> int:
    if base<2 or not digits_: raise ValueError("invalid base/digits")
    n=0
    for d in digits_:
        if not 0<=d<base: raise ValueError("out of range digit")
        n=n*base+d
    return n


def display_digits(items: tuple[int,...]) -> str:
    return "".join(str(d) if d<10 else f"[{d}]" for d in items)


def fraction_expansion(numer: int, denom: int, base: int, max_places: int=500) -> dict:
    if numer < 0 or denom <= 0 or base < 2 or max_places<1:
        raise ValueError("invalid fraction/base")
    f=Fraction(numer,denom)
    whole, rem=divmod(f.numerator,f.denominator)
    seen={}
    places=[]
    while rem and rem not in seen:
        if len(places)>=max_places: raise RuntimeError("unexpected bound exceeded")
        seen[rem]=len(places)
        q,rem=divmod(rem*base,f.denominator)
        places.append(q)
    period_start=seen.get(rem) if rem else None
    if not places:
        notation=display_digits(digits(whole,base))
    elif period_start is None:
        notation=f"{display_digits(digits(whole,base))}."+display_digits(tuple(places))
    else:
        notation=(f"{display_digits(digits(whole,base))}."+
                  display_digits(tuple(places[:period_start]))+"("+
                  display_digits(tuple(places[period_start:]))+")")
    return {"numerator":f.numerator,"denominator":f.denominator,"base":base,
            "terminating":rem==0,"preperiod":len(places) if rem==0 else period_start,
            "period":0 if rem==0 else len(places)-period_start,
            "digits":places,"notation":notation}



def factorization(n: int) -> dict[int,int]:
    if not isinstance(n,int) or not 1<=n<=1000000000:
        raise ValueError("factorization bound")
    factors={}
    p=2
    while p*p<=n:
        while n%p==0:
            factors[p]=factors.get(p,0)+1
            n//=p
        p+=1 if p==2 else 2
    if n>1: factors[n]=factors.get(n,0)+1
    return factors


def totient(n: int) -> int:
    result=n
    for prime in factorization(n):
        result-=result//prime
    return result


def factorization_string(n: int) -> str:
    return " * ".join(str(p) if exponent==1 else f"{p}^{exponent}"
                    for p,exponent in factorization(n).items()) or "1"


def extended_gcd(a: int,b: int) -> tuple[int,int,int]:
    r0,r1=a,b
    s0,s1,t0,t1=1,0,0,1
    while r1:
        q=r0//r1
        r0,r1=r1,r0-q*r1
        s0,s1=s1,s0-q*s1
        t0,t1=t1,t0-q*t1
    return r0,s0,t0


def crt_general(congruences: tuple[tuple[int,int],...]) -> tuple[int,int]:
    if not congruences: raise ValueError("empty CRT")
    x,modulus=0,1
    for residue,m in congruences:
        if not isinstance(residue,int) or not isinstance(m,int) or m<1:
            raise ValueError("invalid congruence")
        common,bezout,_=extended_gcd(modulus,m)
        delta=residue-x
        if delta%common: raise ValueError("incompatible CRT")
        factor=((delta//common)*bezout)%(m//common)
        x=(x+modulus*factor)%(modulus*(m//common))
        modulus*=m//common
    return x,modulus


def crt_pairwise(congruences: tuple[tuple[int,int],...]) -> tuple[int,int]:
    if any(gcd(m,other)!=1 for i,(_,m) in enumerate(congruences)
           for _,other in congruences[i+1:]):
        raise ValueError("moduli not pairwise coprime")
    return crt_general(congruences)


def nth_root_floor(n: int,k: int) -> int:
    if not isinstance(n,int) or n<0 or not isinstance(k,int) or k<1:
        raise ValueError("invalid root input")
    lo,hi=0,1
    while hi**k<=n: hi*=2
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid**k<=n: lo=mid
        else: hi=mid
    return lo


def certified_step_bounds(multiplier: int,side: Decimal,places: int=18) -> list[dict]:
    if multiplier not in (2,3) or not side.is_finite() or side<=0:
        raise ValueError("invalid scale")
    unit=10**places
    rows=[]
    for j in range(9):
        n=(multiplier**j)*(unit**8)
        q=nth_root_floor(n,8)
        lower=Fraction(side)*Fraction(q,unit)
        exact=(q**8==n)
        upper=lower if exact else Fraction(side)*Fraction(q+1,unit)
        rows.append({"step":j,"lower_exact":str(lower),"upper_exact":str(upper),
                     "exact":exact,"max_absolute_width_le":str(Fraction(side)/unit)})
    return rows

def scale_eighth(multiplier: int, side: Decimal=Decimal(1)) -> dict:
    if multiplier not in (2,3) or side<=0: raise ValueError("invalid scale")
    with localcontext() as ctx:
        ctx.prec=55
        ratio=Decimal(multiplier)**(Decimal(1)/Decimal(8))
        values=[+(side*(Decimal(multiplier)**(Decimal(j)/Decimal(8)))) for j in range(9)]
        return {"multiplier":multiplier,"side_initial":str(side),
                "ratio_8th_root_approx":str(+ratio),
                "steps_side_approx":[str(z) for z in values],
                "side_after_8_exact_symbolic":f"{multiplier} * side",
                "area_after_8_over_initial_exact":multiplier**2,
                "volume_after_8_over_initial_exact":multiplier**3,
                "numeric_end_error":str(abs(values[-1] - side*multiplier)),
                "certified_step_bounds":certified_step_bounds(multiplier,side)}


def compute() -> dict:
    B=RADICES
    table={str(n):{str(b):{"digits":list(digits(n,b)),
                          "literal":display_digits(digits(n,b)),
                          "back_decoded":numeric_value(digits(n,b),b)}
                    for b in B} for n in VALUES}
    co=[{"a":a,"b":b,"product":a*b,"lcm":lcm(a,b)}
        for i,a in enumerate(B) for b in B[i+1:] if gcd(a,b)==1]
    allgcds={str(a):{str(b):gcd(a,b) for b in B} for a in B}
    ex={str(b):fraction_expansion(1,7,b) for b in B}
    ex2={str(b):fraction_expansion(1,350,b) for b in B}
    M=reduce(lcm,B,1)
    assert M==350
    assert set((x["a"],x["b"]) for x in co)=={(7,10),(7,50)}
    assert numeric_value((7,0),50)==350
    assert numeric_value((5,0),70)==350
    assert table['350']['7']['literal']=='1010'
    assert ex['10']['notation']=='0.(142857)'
    assert ex['50']['notation']=='0.(7)'
    assert ex['70']['notation']=='0.[10]'
    assert ex2['70']['notation']=='0.0[14]'
    return {"schema":"RAFAELIA_MULTIBASE_OCTIC_V2", "status":"LOCAL_SCOPED_TEST",
      "claim_allowed":False,"data_class":"PUBLIC_SYNTHETIC_MATH", "radices":list(B),
      "radix_definition":"positional integer radix >=2; >=10 digit rendered in [decimal] brackets",
      "modulus_is_not_radix":True,"common_lcm":M,"global_base_factorization":factorization_string(M),
      "global_phi":totient(M),
      "gcd_matrix":allgcds,"coprime_radix_pairs":co,
      "crt_verified":{
        "pair_7_10":crt_pairwise(((3,7),(4,10))),
        "pair_7_50":crt_pairwise(((3,7),(4,50))),
        "shared_14_35":crt_general(((3,14),(17,35)))
      },
      "integer_representation_table":table,"fraction_one_seventh":ex,
      "fraction_one_over_350":ex2,
      "octagonal_coprime_spiral": {
        "vertices": 8, "angular_step": 3,
        "angle_indices_0_through_8": [(j*3)%8 for j in range(9)],
        "unique_directions_first_8": len({(j*3)%8 for j in range(8)}),
        "angular_step_2_negative_unique_directions": len({(j*2)%8 for j in range(8)}),
        "direction_returns_after_8": True,
        "radial_not_closed_for_multipliers_2_or_3": True,
      },
      "scale_eighth_root_2":scale_eighth(2),
      "scale_eighth_root_3":scale_eighth(3),
      "eighth_root_scaling_not_eighth_polygon_theorem":True,
      "novelty_proof":"TOKEN_VAZIO_PROOF","physical_RLL_link":"NOT_TESTED",
      "github_actions_ci":("RUN_CONTEXT_PENDING_VERIFICATION" if os.getenv("GITHUB_ACTIONS")=="true" else "NOT_EXECUTED")}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=Path('artifacts/multibase_octice_v2'))
    args=parser.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    result=compute()
    bs=(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8')
    path=args.out_dir/'report.json';path.write_bytes(bs)
    digest=sha256(bs).hexdigest()
    runtime=("GITHUB_ACTIONS_RUN_CONTEXT" if os.getenv("GITHUB_ACTIONS")=="true" else "LOCAL")
    receipt=(f"""# RAFAELIA Ω · V2 · MULTIBASE / OCTIC SCOPED RECEIPT

- status: `LOCAL_SCOPED_TEST`
- predecessor_package: `RAFAELIA_PRIME_GEOMETRY_V1_REVIEW_ONLY`
- source_scope: `public synthetic integer and rational tests`
- schema: `RAFAELIA_MULTIBASE_OCTIC_V2`
- coprime_pairs: `(7,10), (7,50)`
- lcm: `350`
- eights: `a*(2)^(1/8), a*(3)^(1/8)`
- execution_environment: `{runtime}`
- github_actions: `NOT_EXECUTED`
- online_write: `NOT_EXECUTED`
- physical_claim: `NOT_TESTED`
- new_theorem_claim: `TOKEN_VAZIO_PROOF`
- claim_allowed: `false`
- report_sha256_type: `actual generated JSON bytes`
- source_sha256: `{sha256(Path(__file__).read_bytes()).hexdigest()}`
- python_version: `{sys.version.split()[0]}`
- github_commit: `{os.getenv("GITHUB_SHA", "TOKEN_VAZIO_NOT_OBSERVED")}`
- certified_steps: `9 per scale; exact rational brackets`
""" + f'- report_sha256: `{digest}`\n')
    (args.out_dir/'receipt.md').write_text(receipt,encoding='utf-8')
    print(json.dumps({'report_sha256':digest,'lcm':result['common_lcm'],
         'phi':result['global_phi'],'coprime_pairs':result['coprime_radix_pairs'],
         'claim_allowed':False},ensure_ascii=False,sort_keys=True))

if __name__=='__main__': main()