from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "PapersPub" / "08_multiscale_validation_methods"
PROGRAM = BASE / "math_research_program_48_20260905.v1.json"
FULL = BASE / "nibiguiri_full_method_coverage_manifest_20260905.v2.json"
METHOD = BASE / "rigor_procedure_contract_20260906.v2.json"
ENGINE = BASE / "scripts" / "rigor_self_critique_matrix_v2.py"
RUNNER = BASE / "scripts" / "rigor_request_procedure_v2.py"
REQUEST = BASE / "requests" / "REQ-RIGOR-ALL48-20260906.v1.json"

def loadmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path); assert spec and spec.loader
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def load(path): return json.loads(path.read_text(encoding="utf-8"))
E = loadmod(ENGINE, "rigor_engine_v2"); R = loadmod(RUNNER, "rigor_runner_v2")
program, method, full, request = load(PROGRAM), load(METHOD), load(FULL), load(REQUEST)
def assessment(): return E.blank_assessment(program, method, request)
def bind_basis(rec):
    b={"claim_hash":"a","method_hash":"b","evidence_snapshot_hash":"c","source_commit":"d"}; rec["assessment_basis"]=dict(b); rec["current_basis"]=dict(b)
def fill_good(rec, value=4):
    for k in rec["scores_by_dimension"]: rec["scores_by_dimension"][k]=value
    rec["formal_statement"]="forall x: P(x)"; rec["falsifier"]="counterexample x with not P(x)"; rec["claim_goal"]="TRUTH"
    rec["supporting_evidence"]=[{"evidence_id":"E1","reviewer_relation":"INDEPENDENT"}]; bind_basis(rec)

def test_v2_baseline_fail_closed_and_bounds():
    a=assessment(); assert E.validate(program,method,full,a)==[]
    r=E.compute_one(a["research_units"]["H01"],method,a)
    assert r["promotion_decision"]=="BLOCKED" and r["coverage"]==0 and r["observed_score"] is None
    assert r["lower_bound"]==0 and r["upper_bound"]==100

def test_v2_hard_gate_low_score_blocks():
    a=assessment(); rec=a["research_units"]["H01"]; fill_good(rec); rec["scores_by_dimension"]["RG01"]=2
    r=E.compute_one(rec,method,a)
    assert any(x.startswith("HARD_GATE_BELOW_MIN:RG01") for x in r["promotion_blockers"]); assert r["promotion_decision"]=="BLOCKED"

def test_v2_rigor_classes_are_monotonic():
    a=assessment(); rec=a["research_units"]["H01"]; fill_good(rec); rec["scores_by_dimension"]["RG01"]=2
    assert E.compute_one(rec,method,a)["rigor_class"] in {"R0_UNASSESSED","R1_SPECULATIVE","R2_FORMALIZED"}

def test_v2_r6_requires_all_hard_gates_4():
    a=assessment(); rec=a["research_units"]["H01"]; fill_good(rec); rec["proof_status"]="PROVEN"
    assert E.compute_one(rec,method,a)["rigor_class"]=="R6_EXACT_PROVEN"
    rec["scores_by_dimension"]["RG09"]=3; assert E.compute_one(rec,method,a)["rigor_class"]!="R6_EXACT_PROVEN"

def test_v2_not_applicable_has_reason_and_profile_permission():
    a=assessment(); rec=a["research_units"]["H01"]; fill_good(rec)
    rec["scores_by_dimension"]["RG05"]={"state":E.NA,"reason":"pure proof; computation not material"}; assert E.validate(program,method,full,a)==[]
    rec["scores_by_dimension"]["RG01"]={"state":E.NA,"reason":"not allowed"}; assert any("N/A not permitted" in x for x in E.validate(program,method,full,a))

def test_v2_prior_art_only_blocks_novelty_goal():
    a=assessment(); rec=a["research_units"]["H01"]; fill_good(rec); rec["prior_art_state"]=E.TV
    assert "PRIOR_ART_TOKEN_VAZIO_FOR_NOVELTY" not in E.compute_one(rec,method,a)["promotion_blockers"]
    rec["claim_goal"]="NOVELTY"; assert "PRIOR_ART_TOKEN_VAZIO_FOR_NOVELTY" in E.compute_one(rec,method,a)["promotion_blockers"]

def test_v2_stale_basis_blocks():
    a=assessment(); rec=a["research_units"]["H01"]; fill_good(rec); rec["current_basis"]["source_commit"]="changed"
    assert "STALE_REVIEW_REQUIRED" in E.compute_one(rec,method,a)["promotion_blockers"]

def test_v2_full_96_lens_tensor():
    a=assessment(); total=sum(len(E.adversarial_prompts(uid,rec,method,full)) for uid,rec in a["research_units"].items())
    assert total==48*12*96==55296

def test_v2_procedure_p00_p14_and_next_action():
    p=R.build_packet(request,method,program,full,E); assert R.validate_no_missing_step(p)==[]
    assert [x["id"] for x in p["procedure"]]==[f"P{i:02d}" for i in range(15)] and p["next_action"] and p["claim_allowed"] is False

def test_v2_claim_states_bind_canonical_ledger_vocabulary():
    assert method["canonical_claim_states"]==["RAW_ORAL","RAW_NOTE","METAFORA","PARABOLA_DIDATICA","HIPOTESE","REF_REQUIRED","TOKEN_VAZIO","SOURCE_LINKED","METHOD_DEFINED","EVIDENCE_LINKED","RESULT_REPRODUCED","PEER_OR_REVIEW_READY","CLAIM_ALLOWED","CLAIM_BLOCKED"]
