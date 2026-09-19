#!/usr/bin/env python3
"""RLL form-genome composer with crossed watchdog receipts.

A structural search/audit tool. It does not establish scientific claims.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def h(obj: Any) -> str:
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def complement_bit(x: int | None) -> int | None:
    if x is None:
        return None
    if x not in (0,1):
        raise ValueError("bit must be 0,1,None")
    return 1-x


def complement_state(bits: Iterable[int | None]) -> tuple[int | None,...]:
    return tuple(complement_bit(x) for x in bits)


def rotate(seq: tuple[Any,...], k: int) -> tuple[Any,...]:
    if not seq:
        return seq
    k%=len(seq)
    return seq[-k:]+seq[:-k] if k else seq


def reflect(seq: tuple[Any,...]) -> tuple[Any,...]:
    return tuple(reversed(seq))


def d8_orbit(seq: tuple[Any,...]) -> set[tuple[Any,...]]:
    out=set()
    for k in range(len(seq)):
        r=rotate(seq,k)
        out.add(r)
        out.add(reflect(r))
    return out


@dataclass(frozen=True)
class Tick:
    seq:int
    input_hash:str
    state_hash:str
    output_hash:str
    invariants:tuple[str,...]
    claim_allowed:bool=False

    def digest(self)->str:
        return h({
            "seq":self.seq,
            "input_hash":self.input_hash,
            "state_hash":self.state_hash,
            "output_hash":self.output_hash,
            "invariants":self.invariants,
            "claim_allowed":self.claim_allowed,
        })


@dataclass(frozen=True)
class WatchReceipt:
    watcher:str
    seq:int
    target_digest:str
    decision:str
    reasons:tuple[str,...]
    peer_prev_digest:str|None
    meta_prev_digest:str|None
    implementation_id:str
    spec_version:str="form-watchdog.v1"

    def digest(self)->str:
        return h(self.__dict__)


def validate_tick(
    watcher:str,
    tick:Tick,
    prev_tick:Tick|None,
    *,
    peer_prev:WatchReceipt|None,
    meta_prev:"MetaReceipt|None",
    implementation_id:str,
)->WatchReceipt:
    reasons=[]
    if tick.claim_allowed:
        reasons.append("CLAIM_ALLOWED_TRUE")
    if prev_tick is not None:
        if tick.seq != prev_tick.seq+1:
            reasons.append("NON_MONOTONIC_SEQUENCE")
        if tick.digest()==prev_tick.digest():
            reasons.append("REPLAY")
    if not tick.invariants:
        reasons.append("MISSING_INVARIANTS")
    decision="PASS" if not reasons else "FAIL"
    return WatchReceipt(
        watcher=watcher,
        seq=tick.seq,
        target_digest=tick.digest(),
        decision=decision,
        reasons=tuple(reasons),
        peer_prev_digest=peer_prev.digest() if peer_prev else None,
        meta_prev_digest=meta_prev.digest() if meta_prev else None,
        implementation_id=implementation_id,
    )


@dataclass(frozen=True)
class MetaReceipt:
    seq:int
    a_digest:str|None
    b_digest:str|None
    decision:str
    reasons:tuple[str,...]

    def digest(self)->str:
        return h(self.__dict__)


def meta_compare(a:WatchReceipt|None,b:WatchReceipt|None,seq:int)->MetaReceipt:
    reasons=[]
    if a is None:
        reasons.append("WATCHDOG_A_SILENT")
    if b is None:
        reasons.append("WATCHDOG_B_SILENT")
    if a and b:
        if a.seq!=b.seq or a.seq!=seq:
            reasons.append("WATCHDOG_SEQUENCE_DIVERGENCE")
        if a.target_digest!=b.target_digest:
            reasons.append("TARGET_DIGEST_DIVERGENCE")
        if a.decision!=b.decision:
            reasons.append("DECISION_DIVERGENCE")
        if a.implementation_id==b.implementation_id:
            reasons.append("COMMON_MODE_UNRESOLVED")
    if any(x.endswith("DIVERGENCE") or x.endswith("SILENT") for x in reasons):
        decision="DIVERGENCE_FAIL_CLOSED"
    elif a and b and a.decision=="FAIL" and b.decision=="FAIL":
        decision="CONSENSUS_FAIL"
    elif a and b and a.decision=="PASS" and b.decision=="PASS":
        decision="CONSENSUS_PASS_WITH_COMMON_MODE_GAP" if "COMMON_MODE_UNRESOLVED" in reasons else "CONSENSUS_PASS"
    else:
        decision="FAIL_CLOSED"
    return MetaReceipt(seq,a.digest() if a else None,b.digest() if b else None,decision,tuple(reasons))


def trigram_states()->list[tuple[int,int,int]]:
    return list(itertools.product((0,1),repeat=3))


def epistemic_states()->list[tuple[int|None,int|None,int|None]]:
    return list(itertools.product((0,1,None),repeat=3))


def hexagram_states()->list[tuple[int,...]]:
    return list(itertools.product((0,1),repeat=6))


def combination_count(n:int,r:int,ordered:bool)->int:
    return math.perm(n,r) if ordered else math.comb(n,r)


def bounded_select(
    items:list[Any],
    r:int,
    *,
    ordered:bool,
    exhaustive_cap:int,
    sample_budget:int,
    seed:int,
)->dict[str,Any]:
    total=combination_count(len(items),r,ordered)
    if ordered:
        iterator=itertools.permutations(items,r)
    else:
        iterator=itertools.combinations(items,r)

    if total<=exhaustive_cap:
        values=list(iterator)
        mode="EXHAUSTIVE"
    else:
        # Deterministic random draws, bounded and de-duplicated.
        rng=random.Random(seed)
        seen=set()
        values=[]
        budget=min(sample_budget,total)
        while len(values)<budget:
            idx=tuple(rng.sample(range(len(items)),r))
            if not ordered:
                idx=tuple(sorted(idx))
            if idx in seen:
                continue
            seen.add(idx)
            values.append(tuple(items[i] for i in idx))
        mode="BOUNDED_RANDOM_SAMPLE"

    return {
        "mode":mode,
        "total_space":total,
        "returned":len(values),
        "values":values,
        "seed":seed,
        "claim_allowed":False,
    }


def form_genome(seed:dict[str,Any])->dict[str,Any]:
    directions=tuple(seed["directions"])
    if len(directions)!=8 or len(set(directions))!=8:
        raise ValueError("octagon requires 8 unique directions")
    pairs=[tuple(p) for p in seed["antipodal_pairs"]]
    if len(pairs)!=4:
        raise ValueError("requires 4 antipodal pairs")

    return {
        "schema":"rll.form_genome.v1",
        "root_hash":h(seed),
        "primitives":{
            "center":seed["center"],
            "directions":directions,
            "antipodal_pairs":pairs,
            "trigrams":trigram_states(),
            "epistemic_states":epistemic_states(),
        },
        "counts":{
            "trigrams":len(trigram_states()),
            "epistemic_trigrams":len(epistemic_states()),
            "hexagrams":len(hexagram_states()),
            "d8_actions_declared":16,
        },
        "mandala_boundary":{
            "observed_sectors":seed["mandala"]["observed_sectors"],
            "key_mapping":seed["mandala"]["key_mapping"],
        },
        "claim_allowed":False,
    }


def simulate_watch(seed:dict[str,Any])->dict[str,Any]:
    fg=form_genome(seed)
    tick=Tick(
        seq=0,
        input_hash=h(seed),
        state_hash=fg["root_hash"],
        output_hash=h(fg),
        invariants=tuple(seed["invariants"]),
        claim_allowed=False,
    )
    a=validate_tick("A",tick,None,peer_prev=None,meta_prev=None,implementation_id="watch-A.v1")
    b=validate_tick("B",tick,None,peer_prev=None,meta_prev=None,implementation_id="watch-B.v1")
    m=meta_compare(a,b,0)
    return {
        "tick":tick.__dict__,
        "watchdog_A":{**a.__dict__,"digest":a.digest()},
        "watchdog_B":{**b.__dict__,"digest":b.digest()},
        "meta":{**m.__dict__,"digest":m.digest()},
        "claim_allowed":False,
    }


def simulate_two_ticks(seed:dict[str,Any])->dict[str,Any]:
    """Demonstrate delayed reciprocal validation.

    A/B validate P at t0. M compares them. At t1, A/B receive both the peer
    receipt and M(t0) digest. M(t0) therefore cannot certify itself.
    """
    fg=form_genome(seed)
    t0=Tick(0,h(seed),fg["root_hash"],h(fg),tuple(seed["invariants"]),False)
    a0=validate_tick("A",t0,None,peer_prev=None,meta_prev=None,implementation_id="watch-A.v1")
    b0=validate_tick("B",t0,None,peer_prev=None,meta_prev=None,implementation_id="watch-B.v1")
    m0=meta_compare(a0,b0,0)

    state1={**fg,"previous_meta":m0.digest()}
    t1=Tick(1,t0.output_hash,h(state1),h({"accepted":True,"meta0":m0.digest()}),tuple(seed["invariants"]),False)
    a1=validate_tick("A",t1,t0,peer_prev=b0,meta_prev=m0,implementation_id="watch-A.v1")
    b1=validate_tick("B",t1,t0,peer_prev=a0,meta_prev=m0,implementation_id="watch-B.v1")
    m1=meta_compare(a1,b1,1)

    return {
        "ticks":[t0.__dict__,t1.__dict__],
        "A":[{**a0.__dict__,"digest":a0.digest()},{**a1.__dict__,"digest":a1.digest()}],
        "B":[{**b0.__dict__,"digest":b0.digest()},{**b1.__dict__,"digest":b1.digest()}],
        "M":[{**m0.__dict__,"digest":m0.digest()},{**m1.__dict__,"digest":m1.digest()}],
        "cross_check":{
            "A1_peer_prev_is_B0":a1.peer_prev_digest==b0.digest(),
            "B1_peer_prev_is_A0":b1.peer_prev_digest==a0.digest(),
            "A1_meta_prev_is_M0":a1.meta_prev_digest==m0.digest(),
            "B1_meta_prev_is_M0":b1.meta_prev_digest==m0.digest(),
        },
        "claim_allowed":False,
    }


def canonical_d8_assignment(values:tuple[Any,...])->tuple[Any,...]:
    """Canonical representative of an 8-position ring under D8."""
    if len(values)!=8:
        raise ValueError("D8 assignment requires exactly 8 positions")
    orbit=[]
    for k in range(8):
        r=rotate(values,k)
        orbit.append(r)
        orbit.append(reflect(r))
    return min(orbit)


def sample_mandala_assignments(seed:dict[str,Any], *, budget:int|None=None, rng_seed:int|None=None)->dict[str,Any]:
    """Bounded deterministic sampling of trigram->octagon assignments.

    Historical trigram order remains unresolved. Generated mappings are
    computational candidates only. D8-equivalent candidates are deduplicated.
    """
    directions=tuple(seed["directions"])
    trigrams=tuple("".join(map(str,x)) for x in trigram_states())
    if len(directions)!=8:
        raise ValueError("requires 8 directions")
    budget=int(budget if budget is not None else seed["search"]["sample_budget"])
    rng_seed=int(rng_seed if rng_seed is not None else seed["search"]["random_seed"])
    rng=random.Random(rng_seed)
    raw_total=math.factorial(8)
    d8_class_count=raw_total//16  # all eight trigram labels are distinct
    wanted=min(budget,d8_class_count)
    seen=set()
    out=[]
    attempts=0
    max_attempts=max(1000,wanted*100)
    while len(out)<wanted and attempts<max_attempts:
        attempts+=1
        perm=tuple(rng.sample(trigrams,8))
        canon=canonical_d8_assignment(perm)
        if canon in seen:
            continue
        seen.add(canon)
        mapping={directions[i]:perm[i] for i in range(8)}
        out.append({
            "genome_hash":h({"mapping":mapping,"canonical":canon}),
            "mapping":mapping,
            "canonical_d8":list(canon),
            "state":"STRUCTURALLY_VALID",
            "semantic_state":"TOKEN_VAZIO_HISTORICAL_ORDER",
            "claim_allowed":False,
        })
    return {
        "schema":"rll.mandala_assignment_sample.v1",
        "raw_total_space":raw_total,
        "d8_equivalence_classes_exact":d8_class_count,
        "returned":len(out),
        "budget":budget,
        "seed":rng_seed,
        "attempts":attempts,
        "candidates":out,
        "claim_allowed":False,
    }




def validate_radial_geometry(seed:dict[str,Any], *, rho:float=math.sqrt(3)/2, r_min:float=0.5, r_max:float=1.0)->dict[str,Any]:
    reasons=[]
    if not (0 < rho <= 1):
        reasons.append("INVALID_SCALE")
    if not (0 <= r_min <= r_max):
        reasons.append("DEGENERATE_RADIUS")
    state="STRUCTURALLY_VALID" if not reasons else "STRUCTURALLY_INVALID"
    q=math.sqrt(3)/2
    return {
        "schema":"rll.radial_geometry_check.v1",
        "rho":rho,
        "r_min":r_min,
        "r_max":r_max,
        "q_reference":q,
        "area_ratio_if_q":q*q,
        "state":state,
        "reasons":reasons,
        "claim_allowed":False,
    }


def mandala_candidate_descriptor(seed:dict[str,Any], *, rho:float=math.sqrt(3)/2, r_min:float=0.5, r_max:float=1.0)->dict[str,Any]:
    check=validate_radial_geometry(seed,rho=rho,r_min=r_min,r_max=r_max)
    if check["state"]!="STRUCTURALLY_VALID":
        return {
            "state":"PREREQUISITE_MISSING",
            "geometry_check":check,
            "claim_allowed":False,
        }
    return {
        "schema":"rll.mandala_candidate.v1",
        "state":"MANDALA_CANDIDATE",
        "components":[
            "recursive_rhombus",
            "triangle_up",
            "triangle_down",
            "annulus",
            "radial_rotation",
            "optional_octagonal_assignment",
        ],
        "formal_chain":seed.get("geometry_to_mandala",{}),
        "historical_order":seed.get("trigram_historical_order"),
        "key_42_semantics":seed["mandala"]["key_mapping"],
        "geometry_check":check,
        "claim_allowed":False,
    }

def risk_register(seed:dict[str,Any])->dict[str,Any]:
    cfg=seed.get("risk_register",{})
    threshold=int(cfg.get("mitigation_threshold",100))
    rows=[]
    for item in cfg.get("items",[]):
        s=int(item["severity"]); o=int(item["occurrence"]); d=int(item["detectability"])
        if any(x<1 or x>10 for x in (s,o,d)):
            raise ValueError(f"risk scores must be 1..10: {item['id']}")
        rpn=s*o*d
        rows.append({
            **item,
            "rpn":rpn,
            "mitigation_required":rpn>=threshold,
        })
    rows.sort(key=lambda x:(-x["rpn"],x["id"]))
    return {
        "schema":"rll.form_genome_risk_register.v1",
        "score_semantics":cfg.get("score_semantics"),
        "mitigation_threshold":threshold,
        "items":rows,
        "claim_allowed":False,
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed-file",required=True)
    ap.add_argument("--output")
    ap.add_argument("--mode",choices=("summary","watch","watch2","trigrams","hexagrams","mandala-sample","mandala-candidate","risks"),default="summary")
    args=ap.parse_args()

    seed=json.loads(Path(args.seed_file).read_text(encoding="utf-8"))
    if args.mode=="summary":
        result=form_genome(seed)
    elif args.mode=="watch":
        result=simulate_watch(seed)
    elif args.mode=="watch2":
        result=simulate_two_ticks(seed)
    elif args.mode=="trigrams":
        result={"states":trigram_states(),"count":8,"claim_allowed":False}
    elif args.mode=="hexagrams":
        result={"states":hexagram_states(),"count":64,"claim_allowed":False}
    elif args.mode=="risks":
        result=risk_register(seed)
    elif args.mode=="mandala-candidate":
        result=mandala_candidate_descriptor(seed)
    else:
        result=sample_mandala_assignments(seed)

    payload=json.dumps(result,indent=2,sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload+"\n",encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
