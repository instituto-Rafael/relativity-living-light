#!/usr/bin/env python3
"""RLL Ω · Exact LCM cycle-graph vs Euclid/complement arithmetic.

Hosted Python stdlib benchmark of classical integer algorithms, not physics.
No network, no secrets, no packages, no claim of a novel algorithm.
"""
from __future__ import annotations
import argparse
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path

SEED = 20261108
GRAPH_STEP_CAP = 5000


def canonical(values):
    vals = tuple(int(v) for v in values)
    if not vals:
        raise ValueError("MMC requires a nonempty integer tuple")
    return tuple(abs(v) for v in vals)


def gcd_euclid(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def gcd_complement(a, b):
    """One exact complemented Euclid step, then ordinary Euclid.

    Repeating only complemented steps may degrade to O(b) on near-neighbor
    inputs like gcd(1_000_004,1_000_003); preserving the invariant does NOT
    guarantee an efficient algorithm. Do not silently repeat these steps.
    """
    a, b = abs(a), abs(b)
    if not b:
        return a
    r = a % b
    return gcd_euclid(b, b - r if r else 0)


def gcd_repeated_complement_bounded(a, b, max_steps=5000):
    """Adversarial foil; return (result, steps) or (None, max_steps)."""
    a, b = abs(a), abs(b)
    for steps in range(max_steps):
        if not b:
            return a, steps
        r = a % b
        a, b = b, (b - r if r else 0)
    if b:
        return None, max_steps
    return a, max_steps


def lcm_euclid(values):
    vals = canonical(values)
    result = 1
    for n in vals:
        if not n:
            return 0
        result = (result // gcd_euclid(result, n)) * n
    return result


def lcm_complement(values):
    vals = canonical(values)
    result = 1
    for n in vals:
        if not n:
            return 0
        result = (result // gcd_complement(result, n)) * n
    return result


def lcm_graph(values, limit=GRAPH_STEP_CAP):
    """Finite-state graph: synchronous residue vector, add one at each edge.

    Return (answer, examined_edges) or (None, limit) on a bounded skip.
    Zero is meaningful: lcm with 0 is 0, not missing information.
    """
    vals = canonical(values)
    if 0 in vals:
        return 0, 0
    residues = [0] * len(vals)
    for tick in range(1, limit + 1):
        for i, n in enumerate(vals):
            r = residues[i] + 1
            residues[i] = 0 if r == n else r
        if not any(residues):
            return tick, tick
    return None, limit


def cases():
    groups = {
        "user_examples": [(7,10,14), (7,35,50,70), (7,10,14,35,50,70),
                          (7,70), (7,3,10,100), (7,13,17)],
        "shared_factors": [(6,10,15),(8,12,16),(12,18,30),(25,40,60),
                           (7,14,28), (35,50,70), (144,360,840)],
        "primes": [(13,17),(101,103),(1009,1013),(10007,10009),
                   (1000003,1000033)],
        "prime_powers": [(2**10,2**8),(3**6,3**4),(2**10,3**6,5**3),
                         (7**5,7**3),(2**16,3**10)],
        "zero_and_sign": [(0,7,10),(1,),(0,),(-7,10,14),(-7,-35,50),
                          (1,1,1),(7,7,7)],
        "random_seeded": [],
    }
    rng = random.Random(SEED)
    for i in range(42):
        vals = tuple(rng.randint(1,120) for _ in range(rng.randint(2,5)))
        if i%13 == 0:
            vals = (-vals[0],)+vals[1:]
        groups["random_seeded"].append(vals)
    return groups


def run_cases():
    rows = []
    for group, tuples in cases().items():
        for vals in tuples:
            expected = math.lcm(*vals)
            e = lcm_euclid(vals)
            c = lcm_complement(vals)
            if not (expected == e == c):
                raise AssertionError((vals, expected, e, c))
            g, steps = lcm_graph(vals)
            if g is not None and g != expected:
                raise AssertionError((vals, expected, g))
            if 0 not in vals and expected <= GRAPH_STEP_CAP and g is None:
                raise AssertionError("bounded graph missed cycle")
            if 0 not in vals and expected > GRAPH_STEP_CAP and g is not None:
                raise AssertionError("graph claimed early cycle")
            rows.append({"group":group, "values":list(vals), "expected_lcm":expected,
                         "euclid":e, "complement":c,
                         "graph":g if g is not None else "SKIPPED_CAP",
                         "graph_edges":steps,
                         "graph_status":"PASS_SCOPED" if g is not None else "NOT_RUN_CAP"})
    return rows


def timing(rows):
    # Different execution backends are not inherently apples-to-apples.
    data = [tuple(r["values"]) for r in rows]
    def sample(fn, workload, rounds=11, loops=250):
        measurements=[];acc=0
        for _ in range(rounds):
            t0=time.perf_counter_ns()
            for _ in range(loops):
                for row in workload:
                    acc ^= fn(row)
            measurements.append((time.perf_counter_ns()-t0)/(loops*len(workload)))
        return {"median_ns_per_call":int(statistics.median(measurements)),
                "min_ns_per_call":int(min(measurements)),
                "max_ns_per_call":int(max(measurements)),
                "repetitions":rounds,"loops_per_repetition":loops,"anti_dce":acc}
    measurements={
        "math_lcm_C_reference":sample(lambda arr:math.lcm(*arr),data),
        "euclid_python":sample(lcm_euclid,data),
        "complement_python":sample(lcm_complement,data),
    }
    small = [tuple(r["values"]) for r in rows if r["group"] != "random_seeded" and r["expected_lcm"]>0 and r["expected_lcm"]<=350]
    measurements["math_lcm_C_same_small"] = sample(lambda arr: math.lcm(*arr),small,rounds=11,loops=250)
    measurements["euclid_python_same_small"] = sample(lcm_euclid,small,rounds=11,loops=250)
    measurements["complement_python_same_small"] = sample(lcm_complement,small,rounds=11,loops=250)
    measurements["graph_python_small_only"] = sample(lambda arr:lcm_graph(arr)[0],small,rounds=7,loops=15)
    return measurements, len(small)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path, default=Path(__file__).resolve().parent/"results.json")
    p.add_argument("--no-timing",action="store_true")
    args=p.parse_args()
    rows=run_cases()
    pathology = gcd_repeated_complement_bounded(1_000_004, 1_000_003)
    assert pathology == (None,5000)
    stats={"repeated_complement_near_neighbor": "SKIPPED_COST_AFTER_5000_STEPS",
           "total_cases":len(rows),
           "all_exact_cases":sum(r["euclid"]==r["expected_lcm"] and r["complement"]==r["expected_lcm"] for r in rows),
           "graph_verified":sum(r["graph_status"]=="PASS_SCOPED" for r in rows),
           "graph_skipped_cap":sum(r["graph_status"]=="NOT_RUN_CAP" for r in rows)}
    observed,small=(timing(rows) if not args.no_timing else ({},0))
    result={"schema":"rll.multibase_lcm_graph_benchmark.v1",
            "classification":"HOSTED_PYTHON_ONLY_NOT_ORBITAL_PHYSICS",
            "claim_allowed":False,"new_algorithm_claim":False,
            "seed":SEED,"graph_step_cap":GRAPH_STEP_CAP,
            "input_groups":{g:len(v) for g,v in cases().items()},
            "stats":stats,"runtime":observed,"graph_timing_cases":small,
            "environment":{"python":platform.python_version(),"machine":platform.machine(),"system":platform.system()},
            "rows":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},indent=2,ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
