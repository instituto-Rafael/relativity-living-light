#!/usr/bin/env python3
"""RLL V2 six epistemic *types* orthogonal to evidence states (stdlib, fail closed).

This is a locally proposed working taxonomy, not a universal academic ranking.
Never computes Bayes posteriors, never promotes observations or edits V1 sources.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAX = ROOT / "data/contracts/rll_epistemic_taxonomy.v2.json"
V1 = ROOT / "data/contracts/rll_epistemic_evidence_graph.v1.json"
STATES = ROOT / "data/contracts/rll_scientific_validation_orchestrator.v1.json"
SIX = (
    "PROPOSITION_CONJECTURE", "SCIENTIFIC_HYPOTHESIS",
    "MATHEMATICAL_PHYSICAL_MODEL", "FORMAL_THEOREM_IDENTITY",
    "EMPIRICAL_LAW", "SCIENTIFIC_THEORY",
)
UNKNOWN = "UNCLASSIFIED_TOKEN_VAZIO"
PROOF = "FORMAL_THEOREM_IDENTITY"
MODELS = "MATHEMATICAL_PHYSICAL_MODEL"
PRE_REGISTERED = "SCIENTIFIC_HYPOTHESIS"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def git_blob_digest(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def hash_value(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def validate(spec, graph, validation, *, check_source_hash=True):
    errors = []
    def fail(code):
        errors.append(code)
    if spec.get("schema") != "rll.epistemic_taxonomy.v2":
        fail("SCHEMA_NOT_V2")
    if spec.get("claim_allowed") is not False:
        fail("CLAIM_BOUNDARY_BROKEN")
    if spec.get("status") != "LOCAL_TAXONOMY_PROPOSAL_NOT_CANONICAL_ACADEMIC_SIX_LEVEL_SCALE":
        fail("FALSE_UNIVERSAL_ACADEMIC_LADDER")
    boundary = spec.get("execution", {})
    for key in ("no_network", "no_secrets", "no_database_mutation",
                "no_model_fit", "no_new_workflow"):
        if boundary.get(key) is not True:
            fail("UNSAFE_EXECUTION_BOUNDARY:" + key)
    known = spec.get("types", [])
    ids = [v.get("id") for v in known]
    if len(ids) != 6 or set(ids) != set(SIX):
        fail("SIX_TYPE_SET_MISMATCH")
    for item in known:
        if item.get("ordinal") is not None or not item.get("required_for_manual_readiness"):
            fail("TYPE_NOT_NONORDINAL_OR_UNDEFINED:" + str(item.get("id")))
        if not item.get("definition") or not item.get("verification"):
            fail("TYPE_DEFINITION_MISSING:" + str(item.get("id")))
    if spec.get("unclassified_sentinel") != UNKNOWN or UNKNOWN in ids:
        fail("TOKEN_VAZIO_NOT_PRESERVED_AS_SENTINEL")
    official = set(validation.get("evidence_states", []))
    if official != {"TOKEN_VAZIO", "DECLARED_BY_AUTHOR",
                    "OBSERVED_PENDING_REPLICATION", "VERIFIED_LIMITED",
                    "VERIFIED_REPRODUCIBLE", "CONTRADICTION",
                    "FALSIFIED_IN_SCOPE"}:
        fail("OFFICIAL_EVIDENCE_STATE_DRIFT")
    refs = spec.get("source_contracts", [])
    names = {entry.get("path") for entry in refs}
    if names != {str(V1.relative_to(ROOT)), str(STATES.relative_to(ROOT))}:
        fail("SOURCE_CONTRACT_ROUTING_DRIFT")
    if check_source_hash:
        for ref in refs:
            path = ROOT / ref["path"]
            if not path.is_file() or git_blob_digest(path) != ref.get("git_blob_sha1"):
                fail("SOURCE_GIT_BLOB_CHANGED_REQUIRES_REVIEW:" + ref["path"])
    base_cases = {v["id"]: v for v in graph.get("hypotheses", [])}
    cases = spec.get("case_bindings", [])
    if len(cases) != len(base_cases) or len({x.get("id") for x in cases}) != len(cases):
        fail("CASE_BINDINGS_NOT_EXACTLY_V1")
    if {x.get("id") for x in cases} != set(base_cases):
        fail("CASE_MAPPING_INCOMPLETE")
    for case in cases:
        ident, typ, state = case.get("id"), case.get("type"), case.get("evidence_state")
        orig = base_cases.get(ident)
        if typ not in set(SIX) | {UNKNOWN}:
            fail("UNDECLARED_EPISTEMIC_TYPE:" + str(ident))
        if state not in official:
            fail("UNDECLARED_EVIDENCE_STATE:" + str(ident))
        if not case.get("rationale") or not case.get("scope") or not case.get("readiness"):
            fail("UNTYPED_CASE_OR_SCOPE:" + str(ident))
        if orig and case.get("domain") != orig.get("domain"):
            fail("UNSUPPORTED_CROSS_DOMAIN_RECLASSIFICATION:" + str(ident))
        if ident == "EUCLIDEAN_DIAGONAL" and typ != PROOF:
            fail("MATH_THEOREM_CAST_AS_EMPIRICAL_LAW")
        if ident == "MITO_ATP" and typ in ("EMPIRICAL_LAW", "SCIENTIFIC_THEORY"):
            fail("REFERENCE_FALSELY_ELEVATED_TO_LAW_OR_THEORY")
        if ident == "TRIBO_XRAY_CELL":
            if typ == PRE_REGISTERED and "TOKEN_VAZIO" in orig.get("state", ""):
                fail("UNTYPED_EXPLORATION_FALSELY_TESTABLE")
            if state not in ("TOKEN_VAZIO", "DECLARED_BY_AUTHOR"):
                fail("SPECULATIVE_BIOLOGY_FALSELY_VERIFIED")
        if ident in ("LCDM_BACKGROUND", "RLL_BACKGROUND") and typ != MODELS:
            fail("COSMOLOGICAL_MODEL_FALSELY_PROMOTED_TO_THEORY")
        if state in ("VERIFIED_LIMITED", "VERIFIED_REPRODUCIBLE"):
            fail("CLAIMED_VERIFIED_WITHOUT_BINDING_AND_REVIEW:" + str(ident))
    links = spec.get("type_relations", [])
    if not links:
        fail("NO_TYPED_RELATIONS")
    permitted = set(SIX)
    for edge in links:
        if edge.get("from") not in permitted or edge.get("to") not in permitted:
            fail("DANGLING_TYPE_RELATION")
        if edge.get("implies_validity") is not False or not edge.get("requires"):
            fail("RELATION_AS_IMPLICIT_SCIENTIFIC_PROMOTION")
    policy = spec.get("promotion_policy", {})
    if (policy.get("effect") != "REVIEW_ONLY_NO_AUTOMATIC_STATUS_WRITE"
        or policy.get("claim_allowed") is not False
        or policy.get("automatic_reclassification") is not False
        or policy.get("no_fictional_six_step_ladder") is not True):
        fail("PROMOTION_POLICY_NOT_FAIL_CLOSED")
    if set(policy.get("evidence_requirements", {})) != set(SIX):
        fail("INCOMPLETE_PER_TYPE_EVIDENCE_REQUIREMENTS")
    if len(policy.get("required_provenance", [])) < 5:
        fail("INSUFFICIENT_PROVENANCE_REQUIREMENTS")
    return {
        "schema": "rll.epistemic_taxonomy_gate_receipt.v2",
        "status": "PASS_SCOPED_TAXONOMY_ONLY" if not errors else "BLOCKED_TAXONOMY",
        "classes": len(known),
        "mapped_cases": len(cases),
        "typed_relations": len(links),
        "states_from_official_contract": sorted(official),
        "claim_allowed": False,
        "physical_validation": "NOT_RUN",
        "posterior": "NOT_RUN",
        "automatic_promotions": 0,
        "errors": errors,
    }


def promotion_readiness(spec, case, target, receipt):
    """Evaluate only whether a *human* may review evidence, never update any state."""
    policy = spec["promotion_policy"]
    valid = {"VERIFIED_LIMITED", "VERIFIED_REPRODUCIBLE"}
    if target not in valid:
        return "BLOCKED_UNSUPPORTED_TARGET"
    typ = case.get("type")
    if typ not in SIX or typ == "PROPOSITION_CONJECTURE":
        return "BLOCKED_TYPE_NOT_READY_FOR_VERIFICATION"
    if case.get("evidence_state") in ("CONTRADICTION", "FALSIFIED_IN_SCOPE"):
        return "BLOCKED_NEGATIVE_EVIDENCE_REQUIRES_NEW_SUPERSEDING_REVIEW"
    required = list(policy["required_provenance"]) + list(policy["evidence_requirements"][typ])
    if target == "VERIFIED_REPRODUCIBLE":
        required += ["independent_replication_sha256"]
    missing = [k for k in required if not receipt.get(k)]
    if missing:
        return "BLOCKED_TOKEN_VAZIO:" + ",".join(missing)
    invalid = [k for k in required if k.endswith("_sha256") and not hash_value(receipt[k])]
    if invalid:
        return "BLOCKED_INVALID_SHA256:" + ",".join(invalid)
    if receipt.get("independence_verified") is not True and target == "VERIFIED_REPRODUCIBLE":
        return "BLOCKED_REPLICATION_INDEPENDENCE_NOT_VERIFIED"
    if receipt.get("reviewer_verified") is not True or receipt.get("source_verified") is not True:
        return "BLOCKED_SOURCE_OR_REVIEWER_NOT_VERIFIED"
    return "READY_FOR_HUMAN_REVIEW_NOT_A_CLAIM_OR_STATUS_MUTATION"


def compose_matrix(spec):
    """Non-ranked six-class graph, including unknown nodes as legitimate gap."""
    by_id = {x["id"]: x for x in spec["types"]}
    return [
        {"id":v["id"], "epistemic_type":v["type"],
         "verification_method":by_id.get(v["type"], {}).get("verification", "TOKEN_VAZIO"),
         "evidence_state":v["evidence_state"],
         "domain":v["domain"],
         "ready_for_scientific_promotion": False,
         "claim_allowed": False}
        for v in sorted(spec["case_bindings"], key=lambda x:x["id"])
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-pass", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    spec = load(TAX)
    result = validate(spec, load(V1), load(STATES))
    result["case_matrix"] = compose_matrix(spec)
    result["source_git_blob_sha1"] = {ref["path"]: ref["git_blob_sha1"]
                                     for ref in spec["source_contracts"]}
    data = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data+"\n", encoding="utf8")
    print(data)
    return 2 if result["errors"] and args.require_pass else 0


if __name__ == "__main__":
    raise SystemExit(main())
