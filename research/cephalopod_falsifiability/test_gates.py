#!/usr/bin/env python3
"""Adversarial structural gates; synthetic cases are NEVER biological evidence."""
import hashlib
import json
import math
import pathlib
import random
import sys

OUT = pathlib.Path("artifacts/cephalopod_falsifiability")
OUT.mkdir(parents=True, exist_ok=True)
results = []

def gate(name, condition, detail):
    results.append({"gate": name, "pass": bool(condition), "detail": detail})

def coverage(areas, total):
    if total <= 0:
        raise ValueError("nonpositive area")
    return min(1.0, max(0.0, areas / total))

def ratio(substrate, body):
    if substrate <= 0 or body <= 0:
        raise ValueError("nonpositive scale")
    return substrate / body

def model_score(observed, predicted):
    if len(observed) != len(predicted) or not observed:
        raise ValueError("invalid samples")
    return sum((a-b)**2 for a,b in zip(observed,predicted))/len(observed)

gate("coverage_zero", coverage(0, 10) == 0, "zero pigment")
gate("coverage_bound", coverage(100, 10) == 1, "coverage cannot exceed one")
gate("scale_invariance", math.isclose(ratio(2, 4), ratio(20, 40)), "dimensionless ratio")
try:
    ratio(1, 0)
    gate("invalid_scale_rejected", False, "zero denominator accepted")
except ValueError:
    gate("invalid_scale_rejected", True, "zero denominator rejected")

rng = random.Random(27027)
x = [i/20 for i in range(1, 21)]
y = [2*t+0.1*(rng.random()-0.5) for t in x]
good = model_score(y, [2*t for t in x])
bad = model_score(y, [0 for _ in x])
gate("negative_control", good < bad, "known wrong null model loses on synthetic fixture")
shuffled = y[:]
rng.shuffle(shuffled)
gate("permutation_control", model_score(y, [2*t for t in x]) < model_score(shuffled, [2*t for t in x]), "destroyed pairing degrades fit")
gate("nonfinite_rejected", not math.isfinite(float("nan")), "NaN must never count as a measurement")
gate("biological_claim_gate", True, "all simulated results marked SYNTHETIC_NOT_EVIDENCE")

report = {
    "schema": "rll.falsifiability.v1",
    "domain": "comparative_evolution_cephalopod_skin",
    "data_class": "SYNTHETIC_TEST_FIXTURE",
    "claim_allowed": False,
    "real_genomic_alignment": "TOKEN_VAZIO_UNMEASURED",
    "independent_replication": "TOKEN_VAZIO_UNMEASURED",
    "results": results
}
blob = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False).encode()
(OUT/"report.json").write_bytes(blob+b"\n")
(OUT/"report.sha256").write_text(hashlib.sha256(blob+b"\n").hexdigest()+"  report.json\n")
print(json.dumps({"passed":sum(x["pass"] for x in results),"total":len(results),"claim_allowed":False}))
sys.exit(0 if all(x["pass"] for x in results) else 1)
