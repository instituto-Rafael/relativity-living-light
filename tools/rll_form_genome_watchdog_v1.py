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


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed-file",required=True)
    ap.add_argument("--output")
    ap.add_argument("--mode",choices=("summary","watch","trigrams","hexagrams"),default="summary")
    args=ap.parse_args()

    seed=json.loads(Path(args.seed_file).read_text(encoding="utf-8"))
    if args.mode=="summary":
        result=form_genome(seed)
    elif args.mode=="watch":
        result=simulate_watch(seed)
    elif args.mode=="trigrams":
        result={"states":trigram_states(),"count":8,"claim_allowed":False}
    else:
        result={"states":hexagram_states(),"count":64,"claim_allowed":False}

    payload=json.dumps(result,indent=2,sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload+"\n",encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
