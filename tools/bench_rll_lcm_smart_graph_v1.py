#!/usr/bin/env python3
"""RLL reproducible benchmark on existing 72 exact tuples. stdlib only.
Same-corpus methods, matching GCD backend controls, explicit SPF cold costs.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import time
from pathlib import Path
from rll_lcm_graph_benchmark_v1 import (
    cases, gcd_euclid, lcm_euclid, lcm_complement, lcm_graph
)
from rll_lcm_smart_graph_v1 import jump_graph, prime_lattice_trial, SmallestPrimeFactorGraph


def euclid_native_gcd(v):
    if not v: raise ValueError("empty")
    total=1
    for n in v:
        n=abs(n)
        if not n: return 0
        total=(total//math.gcd(total,n))*n
    return total


def validate():
    rows=[]
    for group,tuples in cases().items():
        for v in tuples:
            expected=math.lcm(*v)
            answer,edges=jump_graph(v,trace=True)
            p=jump_graph(v,gcd_fn=gcd_euclid)
            old,edges_seen=lcm_graph(v)
            vals={"euclid":lcm_euclid(v),"euclid_native_gcd":euclid_native_gcd(v),
                  "complement":lcm_complement(v),"jump":answer,
                  "jump_python_gcd":p,"prime_trial":prime_lattice_trial(v)}
            if any(vv!=expected for vv in vals.values()):
                raise AssertionError((v,expected,vals))
            if old is not None and old!=expected:
                raise AssertionError(("old",v,old,expected))
            if any(after != start*mult or gcd != math.gcd(start,n) or
                   mult != n//gcd for start,n,gcd,mult,after in edges):
                raise AssertionError(("edge",v))
            rows.append({"group":group,"values":list(v),"expected":expected,
                         **vals, "edges":len(edges),
                         "old_result":old if old is not None else "NOT_RUN_CAP",
                         "old_ticks":edges_seen})
    assert len(rows)==72
    return rows


def time_method(fn,rows,reps=7,loops=20):
    observed=[];checksum=0
    for _ in range(reps):
        start=time.perf_counter_ns()
        for _j in range(loops):
            for v in rows:
                checksum ^= fn(v)
        observed.append((time.perf_counter_ns()-start)/(loops*len(rows)))
    return {"median_ns":round(statistics.median(observed),1),
            "min_ns":round(min(observed),1),"max_ns":round(max(observed),1),
            "rounds":reps,"loops":loops,"case_count":len(rows),
            "anti_elision_checksum":checksum}


def run(*,quick):
    rows=validate()
    data=[tuple(r["values"]) for r in rows]
    max_input=max(abs(n) for v in data for n in v)
    t0=time.perf_counter_ns()
    sieve=SmallestPrimeFactorGraph(max_input)
    precompute_ns=time.perf_counter_ns()-t0
    for row,v in zip(rows,data):
        row["prime_spf"]=sieve.lcm(v)
        assert row["prime_spf"]==row["expected"]
    fast_loops=20 if quick else 65
    slower_loops=3 if quick else 14
    methods={
        "math_lcm_C":lambda a:math.lcm(*a),
        "euclid_python_gcd":lcm_euclid,
        "euclid_native_gcd":euclid_native_gcd,
        "complement_python_gcd":lcm_complement,
        "jump_native_gcd":jump_graph,
        "jump_python_gcd":lambda a:jump_graph(a,gcd_fn=gcd_euclid),
        "prime_spf_warm":sieve.lcm,
    }
    all_t={k:time_method(f,data,reps=7 if quick else 9,loops=fast_loops)
           for k,f in methods.items()}
    all_t["prime_trial_no_sieve"]=time_method(prime_lattice_trial,data,
                                            reps=5 if quick else 9,loops=slower_loops)
    # Same subset for all algorithms, including the former explicit walk.
    small=[v for v in data if 0<math.lcm(*v)<=350 and max(map(abs,v))<=350]
    small_t={k:time_method(f,small,reps=7,loops=fast_loops)
             for k,f in methods.items()}
    small_t["explicit_walk"]=time_method(lambda a:lcm_graph(a)[0],
                                         small,reps=5,loops=3 if quick else 5)
    saved=all_t["euclid_python_gcd"]["median_ns"]-all_t["prime_spf_warm"]["median_ns"]
    breakeven=None if saved<=0 else math.ceil(precompute_ns/saved)
    result={
        "schema":"rll.smart_lcm_graph_benchmark.v1",
        "source":"RLL existing tools/rll_lcm_graph_benchmark_v1.py",
        "scope":"HOSTED_MATHEMATICAL_ONLY",
        "claim_allowed":False,"new_algorithm_claim":False,
        "seed":20261108,"case_count":len(rows),
        "all_exact":sum(all(r[k]==r["expected"] for k in
                ("euclid","euclid_native_gcd","complement","jump",
                 "jump_python_gcd","prime_trial","prime_spf")) for r in rows),
        "old_graph":{"verified":sum(r["old_result"]!="NOT_RUN_CAP" for r in rows),
                     "cap":sum(r["old_result"]=="NOT_RUN_CAP" for r in rows)},
        "jump_graph_total_edges":sum(r["edges"] for r in rows),
        "spf":{"build_ns":precompute_ns,"max_input":max_input,
               "table_payload_bytes":sieve.payload_bytes,
               "warm_break_even_vs_euclid_python_queries":breakeven},
        "timing":{"same_72":all_t,"same_small":small_t,"small_count":len(small)},
        "environment":{"python":platform.python_version(),"machine":platform.machine(),
                       "system":platform.system()},
        "physical_claim":"TOKEN_VAZIO"
    }
    return result, rows


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--quick",action="store_true")
    p.add_argument("--output",type=Path,default=Path("results/audit/rll_smart_lcm_ci.json"))
    p.add_argument("--csv",type=Path,default=Path("results/audit/rll_smart_lcm_ci_cases.csv"))
    o=p.parse_args()
    result,rows=run(quick=o.quick)
    o.csv.parent.mkdir(parents=True,exist_ok=True)
    with o.csv.open("w",encoding="utf-8",newline="") as out:
        columns=["group","values","expected","euclid","euclid_native_gcd",
                 "complement","jump","jump_python_gcd","prime_trial",
                 "prime_spf","edges","old_result","old_ticks"]
        wr=csv.DictWriter(out,fieldnames=columns)
        wr.writeheader()
        for row in rows:
            wr.writerow({**row,"values":json.dumps(row["values"],separators=(",",":"))})
    result["csv_sha256"]=hashlib.sha256(o.csv.read_bytes()).hexdigest()
    o.output.parent.mkdir(parents=True,exist_ok=True)
    o.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"count":result["case_count"],"exact":result["all_exact"],
          "old":result["old_graph"],"jump_edges":result["jump_graph_total_edges"],
          "spf":result["spf"],"times":result["timing"],
          "claim_allowed":False},indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
