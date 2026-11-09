#!/usr/bin/env python3
"""Fail-closed, no new physical claim: validate RLL cross-scale blind-spot addendum."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL = "data/governance/RLL_NEGLECTED_CROSS_SCALE_FALSIFIERS_20261108_V1.json"
ALLOWED = {"observational_systematic","model_candidate","cross_scale_guard","model_identifiability","analogy_only","dimensional_guard"}

def validate(root=ROOT):
    root=Path(root)
    path=root/REL
    text=path.read_bytes()
    c=json.loads(text)
    if c["schema"]!="rll.neglected_cross_scale_falsifiers.v1":
        raise ValueError("WRONG_SCHEMA")
    if any(c[k] is not False for k in ("claim_allowed","scientific_confirmation","global_fit_performed","publication_ready")):
        raise ValueError("CLAIM_PROMOTION_FORBIDDEN")
    parent_file=root/c["parent_graph"]
    parent_b=parent_file.read_bytes()
    parent=json.loads(parent_b)
    if parent["claim_allowed"] is not False or parent["scientific_fit_performed"] is not False:
        raise ValueError("PARENT_CLAIM_DRIFT")
    closure=json.loads((root/c["parent_closure"]).read_text())
    if closure["claim_allowed"] is not False:
        raise ValueError("PERTURBATION_CLAIM_DRIFT")
    if not (root/c["parent_cosmology"]).is_file():
        raise ValueError("MISSING_COSMOLOGY_COMPARATOR")
    base_nodes={n["id"] for n in parent["nodes"]}
    src={s["id"]:s for s in c["sources"]}
    nodes={n["id"]:n for n in c["items"]}
    if len(src)!=len(c["sources"]) or len(nodes)!=len(c["items"]) or len(c["edges"])!=len(c["items"]):
        raise ValueError("DUPLICATE_OR_UNMATCHED_GRAPH_NODE")
    if len(nodes)<10 or len(src)<10:
        raise ValueError("INCOMPLETE_AUDIT")
    for sid,s in src.items():
        if not s["uri"].startswith("https://"):
            raise ValueError("SOURCE_URL_INVALID_"+sid)
        if s["year"]>2026 or s["year"]<2025:
            raise ValueError("SOURCE_YEAR_OUT_OF_BOUNDS_"+sid)
        if not s["tier"] or not s["note"]:
            raise ValueError("SOURCE_PROVENANCE_INCOMPLETE_"+sid)
    for n in c["items"]:
        if n["class"] not in ALLOWED or n["priority"] not in ("P0","P1","P2"):
            raise ValueError("NODE_TYPE_OR_PRIORITY_INVALID_"+n["id"])
        if n["upstream_node"] not in base_nodes:
            raise ValueError("UNDEFINED_UPSTREAM_NODE_"+n["id"])
        if any(q not in src for q in n["source_ids"]):
            raise ValueError("UNREFERENCED_PAPER_"+n["id"])
        if not all(n.get(k) for k in ("title","observable","baseline","falsifier","next","rll_status")):
            raise ValueError("MISSING_FALSIFIER_OR_ROUTE_"+n["id"])
        if n["physical_bridge"] is not False:
            raise ValueError("PHYSICAL_BRIDGE_NOT_DEMONSTRATED_"+n["id"])
    seen=set()
    for e in c["edges"]:
        if e["id"] in seen or e["from"] not in base_nodes or e["to"] not in nodes:
            raise ValueError("BROKEN_EDGE")
        seen.add(e["id"])
        target=nodes[e["to"]]
        if (e["relation_class"]!=target["class"] or e["physical_bridge_claimed"] is not False
            or e["evidence_source_ids"]!=target["source_ids"]):
            raise ValueError("EDGE_CLAIM_OR_PROVENANCE_MISMATCH")
    if any(x["class"]=="analogy_only" and x["rll_status"]!="UNSUPPORTED_PHYSICAL_BRIDGE" for x in c["items"]):
        raise ValueError("METAPHOR_PROMOTED")
    if not {"NG01","NG03","NG05","NG07","NG09","NG10","NG11"}.issubset(nodes):
        raise ValueError("CRITICAL_FALSIFIERS_MISSING")
    # Independent SI compactness identity: C=GM/(Rc^2), no collapse inference.
    G=6.67430e-11
    c_light=299792458.0
    solar_kg=1.98847e30
    compactness=G*(1.4*solar_kg)/(12000.0*c_light*c_light)
    if not (math.isfinite(compactness) and 0.17<compactness<0.18):
        raise ValueError("COMPACTNESS_DIMENSION_CHECK")
    return {
       "schema":"rll.neglected_cross_scale_gate_receipt.v1",
       "state":"PASS_SCOPED_STRUCTURE_ONLY",
       "claim_allowed":False,
       "source_graph_sha256":hashlib.sha256(parent_b).hexdigest(),
       "addendum_sha256":hashlib.sha256(text).hexdigest(),
       "nodes":len(nodes),"edges":len(seen),"papers":len(src),
       "P0":sum(x["priority"]=="P0" for x in c["items"]),
       "compactness_1p4Msun_12km":compactness,
       "evidence":"LITERATURE_CONTEXT_NOT_RLL_FIT",
       "physical_model_validation":"NOT_RUN",
       "next":"Only producer-governed preregistered physical equations and matched likelihood can resolve TOKEN_VAZIO"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=validate(a.root)
    blob=json.dumps(report,indent=2)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(blob,encoding="utf-8")
    print(blob,end="")
if __name__=="__main__":
    main()
