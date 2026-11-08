#!/usr/bin/env python3
"""RLL evidence DAG: stdlib-only fail-closed topology, provenance and Bayes readiness.

This does NOT fetch articles, execute fits, invent priors or establish physical claims.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "data/contracts/rll_epistemic_evidence_graph.v1.json"
G4 = ROOT / "data/contracts/rll_g4_background_tournament.v1.json"
MODEL_SET = ("LCDM", "wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL")
SOURCE_ROLES = frozenset({
    "OBSERVATIONAL_PRIMARY", "FORMAL_REFERENCE", "SCHOLARLY_PUBLICATION",
    "ARCHIVE_REPOSITORY", "METADATA_REGISTRY", "NEWS_DISCOVERY",
    "PRIVATE_INDEX", "SOURCE_CODE_CUSTODY",
})
KINDS = frozenset({
    "FORMAL_DEDUCTIVE", "EMPIRICAL_REFERENCE", "EXPLORATORY_HYPOTHESIS",
    "MODEL_COMPARATOR", "EXPLORATORY_MODEL",
})
RELATIONS = frozenset({
    "ELIGIBLE_LIKELIHOOD_INPUT", "COMPARED_AGAINST",
    "ANALOGY_NOT_CAUSALITY", "REQUIRES_FALSIFICATION", "DEPENDS_ON",
})
RECEIPT_STATE = "PASS_SCOPED_EPISTEMIC_GRAPH_ONLY"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _acyclic(nodes, adjacency):
    state = {}
    def visit(node):
        if state.get(node) == 1:
            raise ValueError("CAUSAL_DEPENDENCY_CYCLE:" + node)
        if state.get(node) == 2:
            return
        state[node] = 1
        for next_node in adjacency.get(node, []):
            if next_node not in nodes:
                raise ValueError("UNRESOLVED_DEPENDENCY:" + next_node)
            visit(next_node)
        state[node] = 2
    for node in nodes:
        visit(node)


def evaluate(contract, g4):
    errors = []
    def invalid(message):
        errors.append(message)
    if contract.get("claim_allowed") is not False or contract.get("publication_effect") != "NONE":
        invalid("CLAIM_BOUNDARY_OR_PUBLICATION_ESCALATION")
    if contract.get("science_execution") != "NOT_RUN":
        invalid("SCIENCE_EXECUTION_FALSIFIED")
    if contract.get("security", {}).get("pr_secrets") != "DENIED":
        invalid("SECRET_EXPOSURE_TO_PR")
    if contract.get("security", {}).get("pr_network") != "DENIED":
        invalid("UNCONTROLLED_NETWORK_ON_PR")
    if contract.get("security", {}).get("pull_request_target") != "FORBIDDEN":
        invalid("PRIVILEGED_PULL_REQUEST_TARGET_NOT_ALLOWED")
    if list(g4.get("models", {})) != list(MODEL_SET) or g4.get("claim_allowed") is not False:
        invalid("G4_MODEL_OR_CLAIM_BOUNDARY_CHANGED")

    src = contract.get("sources", [])
    hyp = contract.get("hypotheses", [])
    edges = contract.get("relations", [])
    sids = [x.get("id") for x in src]
    hids = [x.get("id") for x in hyp]
    if len(set(sids)) != len(sids) or None in sids:
        invalid("DUPLICATE_SOURCE_ID")
    if len(set(hids)) != len(hids) or None in hids:
        invalid("DUPLICATE_HYPOTHESIS_ID")
    source_map = {x.get("id"): x for x in src}
    hypothesis_map = {x.get("id"): x for x in hyp}
    for s in src:
        if s.get("role") not in SOURCE_ROLES:
            invalid("UNRECOGNIZED_SOURCE_ROLE:" + str(s.get("id")))
        if not str(s.get("url", "")).startswith("https://"):
            invalid("UNTRUSTED_SOURCE_URL:" + str(s.get("id")))
        if not s.get("authority") or not s.get("status"):
            invalid("UNDECLARED_SOURCE_AUTHORITY:" + str(s.get("id")))
        if s.get("role") == "NEWS_DISCOVERY" and s.get("independence_group"):
            invalid("NEWS_CAST_AS_PRIMARY_OBSERVATION")
    for h in hyp:
        if h.get("class") not in KINDS:
            invalid("UNRECOGNIZED_HYPOTHESIS_TYPE:" + str(h.get("id")))
        if not h.get("claim") or not h.get("assumptions") or not h.get("falsifier"):
            invalid("HYPOTHESIS_NOT_FALSIFIABLE_OR_UNFORMALIZED:" + str(h.get("id")))
        if h.get("class") == "EXPLORATORY_HYPOTHESIS" and not str(h.get("state", "")).startswith("TOKEN_VAZIO"):
            invalid("SPECULATIVE_HYPOTHESIS_FALSELY_PROMOTED:" + str(h.get("id")))
    if "EUCLIDEAN_DIAGONAL" not in hypothesis_map or hypothesis_map["EUCLIDEAN_DIAGONAL"].get("class") != "FORMAL_DEDUCTIVE":
        invalid("FORMAL_PETREO_NOT_TYPED")
    if "TRIBO_XRAY_CELL" not in hypothesis_map or hypothesis_map["TRIBO_XRAY_CELL"].get("state") != "TOKEN_VAZIO_PHYSICAL_MECHANISM":
        invalid("TRIBO_XRAY_PROMOTED_WITHOUT_MECHANISM")

    adjacency = {}
    valid_nodes = {"source:" + x for x in sids} | {"hypothesis:" + x for x in hids}
    for edge in edges:
        a, b, predicate = edge.get("from"), edge.get("to"), edge.get("type")
        if a not in valid_nodes or b not in valid_nodes:
            invalid("DANGLING_RELATION:" + str(a) + "->" + str(b))
            continue
        if predicate not in RELATIONS:
            invalid("ILLEGAL_RELATION:" + str(predicate))
            continue
        if not edge.get("evidence") or not edge.get("scope"):
            invalid("UNTYPED_RELATION_EVIDENCE:" + str(a) + "->" + str(b))
        arole = source_map.get(str(a).removeprefix("source:"), {}).get("role")
        if predicate == "ELIGIBLE_LIKELIHOOD_INPUT":
            if arole != "OBSERVATIONAL_PRIMARY":
                invalid("NONPRIMARY_EVIDENCE_CANNOT_BE_LIKELIHOOD_INPUT")
            if hypothesis_map.get(str(b).removeprefix("hypothesis:"), {}).get("domain") != source_map.get(str(a).removeprefix("source:"), {}).get("domain"):
                invalid("CROSS_DOMAIN_LIKELIHOOD_WITHOUT_PHYSICAL_BRIDGE")
        if predicate == "DEPENDS_ON":
            adjacency.setdefault(a, []).append(b)
        if predicate == "COMPARED_AGAINST" and (not str(a).startswith("hypothesis:") or not str(b).startswith("hypothesis:")):
            invalid("MODEL_COMPARISON_MUST_USE_HYPOTHESES")
        if predicate == "ANALOGY_NOT_CAUSALITY" and edge.get("evidence") == "VERIFIED_CAUSAL":
            invalid("ANALOGY_TO_CAUSALITY_ESCALATION")
    try:
        _acyclic(valid_nodes, adjacency)
        stages = contract.get("execution_dag", [])
        stage_map = {x.get("id"): x for x in stages}
        if len(stage_map) != len(stages) or len(stages) < 6:
            invalid("WORKFLOW_DAG_INCOMPLETE_OR_DUPLICATE")
        _acyclic(set(stage_map), {key: row.get("requires", []) for key, row in stage_map.items()})
        for item in stages:
            if not item.get("function"):
                invalid("PIPELINE_STAGE_WITHOUT_SINGLE_RESPONSIBILITY")
    except ValueError as exc:
        invalid(str(exc))
    protocol = contract.get("bayes_protocol", {})
    if protocol.get("state") != "NOT_RUN_NO_FROZEN_LIKELIHOOD" or "posterior_by_reputation" not in protocol.get("forbid", []):
        invalid("BAYES_NOT_FAIL_CLOSED")

    return {
        "schema": "rll.epistemic_evidence_graph_gate_receipt.v1",
        "state": RECEIPT_STATE if not errors else "BLOCKED_EPISTEMIC_GRAPH",
        "claim_allowed": False,
        "source_nodes": len(src),
        "hypothesis_nodes": len(hyp),
        "relations": len(edges),
        "stages": len(contract.get("execution_dag", [])),
        "posterior": "TOKEN_VAZIO_NO_REGISTERED_LIKELIHOOD",
        "formal_validation": "AXIOMATIC_REFERENCE_NOT_AUTOMATED_PROOF",
        "network_requests": 0,
        "secrets_read": 0,
        "errors": errors,
    }


def bayesian_readiness(payload, source_registry):
    """No Bayesian numerical update. Test whether a future bound run could be reviewed."""
    required = ("prior_h1", "prior_origin", "h0", "h1", "observations_sha256",
                "likelihood_sha256", "covariance_sha256", "selection_sha256",
                "nuisance_sha256", "independence_groups", "all_preregistered",
                "model_parameter_counts")
    missing = [key for key in required if key not in payload]
    if missing:
        return "BLOCKED_TOKEN_VAZIO_BAYES:" + ",".join(missing)
    try:
        prior = float(payload["prior_h1"])
        if not (0.0 < prior < 1.0 and math.isfinite(prior)):
            raise ValueError("prior")
        if not payload["prior_origin"] or not payload["h0"] or not payload["h1"]:
            raise ValueError("prior/model identity")
        for key in ("observations_sha256", "likelihood_sha256", "covariance_sha256",
                    "selection_sha256", "nuisance_sha256"):
            val = payload[key]
            if not (isinstance(val, str) and len(val) == 64 and all(c in "0123456789abcdef" for c in val)):
                raise ValueError(key)
        if payload["all_preregistered"] is not True:
            raise ValueError("pre-registration")
        groups = payload["independence_groups"]
        if not groups or len(set(groups)) != len(groups):
            raise ValueError("dependent sample double counting")
        provenance = {s["independence_group"]: s for s in source_registry
                      if s.get("independence_group")}
        if any(group not in provenance for group in groups):
            raise ValueError("unregistered observational group")
        if any(provenance[group]["role"] != "OBSERVATIONAL_PRIMARY" for group in groups):
            raise ValueError("nonprimary observational source")
        if not (isinstance(payload["model_parameter_counts"], dict)
                and payload["h0"] in payload["model_parameter_counts"]
                and payload["h1"] in payload["model_parameter_counts"]
                and all(isinstance(n, int) and n > 0 for n in payload["model_parameter_counts"].values())):
            raise ValueError("parameter ledger")
    except (ValueError, TypeError, KeyError) as exc:
        return "BLOCKED_BAYES_INTEGRITY:" + str(exc)
    return "READY_FOR_EXTERNAL_FROZEN_LIKELIHOOD_REVIEW_NOT_POSTERIOR"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    result = evaluate(load_json(SPEC), load_json(G4))
    result["contract_sha256"] = digest(SPEC)
    result["g4_sha256"] = digest(G4)
    result["git_sha"] = os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_HEAD")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if (not args.require_pass or not result["errors"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
