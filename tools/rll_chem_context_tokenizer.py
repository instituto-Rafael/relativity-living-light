#!/usr/bin/env python3
"""RAFAELIA typed science context resolver. Stdlib only, no physical inference."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "data/governance/RLL_TYPED_CHEM_WATER_SESSION_TOKENS_V1.json"
REQUIRED = {
    "H3": ("chem:cluster:H3", "nuclear:isotope:H-3"),
    "³H": ("nuclear:isotope:H-3",),
    "H3+": ("chem:ion:H3+",),
    "He2": ("chem:molecule:He2", "nuclear:isotope:He-2"),
    "He3": ("chem:cluster:He3", "nuclear:isotope:He-3"),
    "³He": ("nuclear:isotope:He-3",),
    "He²⁺": ("chem:ion:He+2",),
    "C3": ("chem:cluster:C3",),
    "C3+": ("chem:ion:C+3",),
    "C³⁺": ("chem:ion:C+3",),
    "C IV": ("spectroscopy:ion:C-IV",),
    "H2O": ("chem:molecule:H2O",),
    "H2O2": ("chem:molecule:H2O2",),
    "H2O3": ("chem:molecule:H2O3",),
    "HO3": ("chem:radical:HO3",),
    "H2O_anomaly": ("water:anomaly:thermodynamic_network",),
    "H(z)": ("cosmology:function:Hubble",),
    "h": ("physics:constant:Planck_h",),
    "head": ("document:heading", "ml:attention_head:metadata_only"),
}
EXPECTED = {
    "chem:molecule:H2O": ({"H": 2, "O": 1}, 0, None),
    "chem:molecule:H2O2": ({"H": 2, "O": 2}, 0, None),
    "chem:molecule:H2O3": ({"H": 2, "O": 3}, 0, None),
    "chem:radical:HO3": ({"H": 1, "O": 3}, 0, None),
    "chem:molecule:O3": ({"O": 3}, 0, None),
    "chem:cluster:C3": ({"C": 3}, 0, None),
    "chem:ion:C+3": ({"C": 1}, 3, None),
    "chem:ion:H3+": ({"H": 3}, 1, None),
    "nuclear:isotope:He-3": ({"He": 1}, 0, 3),
    "nuclear:isotope:H-3": ({"H": 1}, 0, 3),
    "chem:ion:He+2": ({"He": 1}, 2, None),
}
STATES = {"ESTABLISHED", "CONDITIONAL", "AMBIGUOUS_ALIAS"}
INVARIANTS = {"I%02d" % k for k in range(1, 15)}

def issues(g):
    bad = []
    if not isinstance(g, dict):
        return ["manifest_not_an_object"]
    if g.get("schema") != "rafaelia.contextual_chem_token.v1":
        bad.append("schema_version")
    for k in ("claim_allowed", "model_hidden_attention_heads_accessible",
              "raw_conversation_dump_materialized"):
        if g.get(k) is not False:
            bad.append("unverified_promotion:" + k)
    for k in ("surface_records", "sources", "invariant_of_invariants",
              "session_context_links", "unverified_cross_scale_claims"):
        if not isinstance(g.get(k), list):
            return bad + ["invalid_list:" + k]
    records = g["surface_records"]
    if any(not isinstance(r, dict) or not isinstance(r.get("surface"), str)
           or not isinstance(r.get("candidates"), list) or not r["candidates"] for r in records):
        return bad + ["malformed_surface_record"]
    surfaces = [r["surface"] for r in records]
    if len(set(surfaces)) != len(surfaces):
        bad.append("duplicate_surface")
    by_raw = {r["surface"]: r["candidates"] for r in records}
    for raw, expected in REQUIRED.items():
        candidates = by_raw.get(raw)
        if candidates is None or any(not isinstance(c, dict) for c in candidates):
            bad.append("required_alias_missing:" + raw)
            continue
        if tuple(sorted(c.get("id", "") for c in candidates)) != expected:
            bad.append("required_alias_drift:" + raw)
    canonical = {}
    for r in records:
        for c in r["candidates"]:
            if not isinstance(c, dict):
                bad.append("malformed_candidate")
                continue
            ident, kind = c.get("id"), c.get("kind")
            stoich, charge, isotope = c.get("stoichiometry"), c.get("charge"), c.get("isotope")
            if not isinstance(ident, str) or not ident or not isinstance(kind, str) or not kind:
                bad.append("invalid_typed_id")
                continue
            if c.get("status") not in STATES:
                bad.append("invalid_epistemic_state:" + ident)
            if stoich is not None and (not isinstance(stoich, dict) or not stoich
                                       or any(k not in {"H", "He", "O", "C"} or
                                              type(v) is not int or v < 1 for k, v in stoich.items())):
                bad.append("invalid_composition:" + ident)
            if charge is not None and type(charge) is not int:
                bad.append("invalid_charge:" + ident)
            if isotope is not None and (type(isotope) is not int or isotope < 1):
                bad.append("invalid_isotope:" + ident)
            signature = (kind, json.dumps(stoich, sort_keys=True), charge, isotope)
            if ident in canonical and canonical[ident] != signature:
                bad.append("canonical_collision:" + ident)
            canonical[ident] = signature
    for ident, (formula, charge, isotope) in EXPECTED.items():
        matches = [c for r in records for c in r["candidates"]
                   if isinstance(c, dict) and c.get("id") == ident]
        if not matches or any(x.get("stoichiometry") != formula or
                              x.get("charge") != charge or
                              x.get("isotope") != isotope for x in matches):
            bad.append("protected_physical_identity:" + ident)
    sources = g["sources"]
    if any(not isinstance(s, dict) or not isinstance(s.get("id"), str) or
           not str(s.get("url", "")).startswith("https://") for s in sources):
        bad.append("malformed_provenance")
    source_ids = [s["id"] for s in sources if isinstance(s, dict) and isinstance(s.get("id"), str)]
    if len(source_ids) != len(set(source_ids)):
        bad.append("duplicate_source")
    invariants = g["invariant_of_invariants"]
    if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) or not x.get("rule")
           for x in invariants):
        bad.append("malformed_invariant")
    if {x["id"] for x in invariants if isinstance(x, dict) and isinstance(x.get("id"), str)} != INVARIANTS:
        bad.append("invariant_set_drift")
    for x in g["session_context_links"]:
        if not isinstance(x, dict) or x.get("source") not in source_ids or x.get("id") not in canonical:
            bad.append("untraced_session_bridge")
    if not isinstance(g.get("tokenizer_contract"), dict) or (
            g["tokenizer_contract"].get("on_collision") != "TOKEN_VAZIO_AMBIGUOUS" or
            g["tokenizer_contract"].get("on_missing") != "TOKEN_VAZIO_UNKNOWN" or
            g["tokenizer_contract"].get("model_heads") != "NOT_OBSERVABLE"):
        bad.append("resolver_contract_drift")
    if len(g["unverified_cross_scale_claims"]) < 5:
        bad.append("insufficient_rejected_analogies")
    return sorted(set(bad))

def resolve(g, surface, *, kind=None, canonical_id=None):
    matches = [r for r in g["surface_records"] if r["surface"] == surface]
    if not matches:
        return {"raw": surface, "status": "TOKEN_VAZIO_UNKNOWN", "candidates": [],
                "claim_allowed": False}
    possibilities = matches[0]["candidates"]
    if kind is not None:
        possibilities = [c for c in possibilities if c["kind"] == kind]
    if canonical_id is not None:
        possibilities = [c for c in possibilities if c["id"] == canonical_id]
    if not possibilities:
        status = "TOKEN_VAZIO_CONTEXT_CONTRADICTORY"
    elif len(possibilities) > 1:
        status = "TOKEN_VAZIO_AMBIGUOUS"
    else:
        status = "RESOLVED_TYPED_REFERENCE"
    return {"raw": surface, "status": status, "candidates": possibilities,
            "claim_allowed": False, "model_heads_observed": False}

def adversarial(g):
    def r(raw):
        return next(x for x in raw["surface_records"] if x["surface"] == "H2O3")
    def c(raw, surface):
        return next(x for x in raw["surface_records"] if x["surface"] == surface)["candidates"][0]
    mutate = [
        lambda x: x.update(schema="bad"),
        lambda x: x.update(claim_allowed=True),
        lambda x: x.update(model_hidden_attention_heads_accessible=True),
        lambda x: x.update(raw_conversation_dump_materialized=True),
        lambda x: r(x)["candidates"][0].update(stoichiometry={"H": 2, "O": 1}),
        lambda x: c(x, "C3").update(stoichiometry={"C": 1}, charge=3),
        lambda x: c(x, "C³⁺").update(stoichiometry={"C": 3}, charge=0),
        lambda x: c(x, "³He").update(isotope=None),
        lambda x: x["surface_records"].append(copy.deepcopy(x["surface_records"][0])),
        lambda x: x["surface_records"].append({"surface": "H2O3", "candidates": []}),
        lambda x: c(x, "H3+").update(charge=0),
        lambda x: x["sources"].clear(),
        lambda x: x["invariant_of_invariants"].pop(),
        lambda x: x["tokenizer_contract"].update(model_heads="OBSERVED"),
        lambda x: c(x, "HO3").update(stoichiometry={"H": 2, "O": 3}),
    ]
    for i, modification in enumerate(mutate, start=1):
        candidate = copy.deepcopy(g)
        modification(candidate)
        if not issues(candidate):
            raise AssertionError("unfalsified metadata mutation: %d" % i)
    for raw, kwargs, status in [
        ("H3", {}, "TOKEN_VAZIO_AMBIGUOUS"),
        ("He3", {}, "TOKEN_VAZIO_AMBIGUOUS"),
        ("head", {}, "TOKEN_VAZIO_AMBIGUOUS"),
        ("He3", {"kind": "isotope"}, "RESOLVED_TYPED_REFERENCE"),
        ("H2O", {}, "RESOLVED_TYPED_REFERENCE"),
        ("H2O3", {}, "RESOLVED_TYPED_REFERENCE"),
        ("C3", {"canonical_id": "chem:ion:C+3"}, "TOKEN_VAZIO_CONTEXT_CONTRADICTORY"),
        ("unknown", {}, "TOKEN_VAZIO_UNKNOWN"),
    ]:
        if resolve(g, raw, **kwargs)["status"] != status:
            raise AssertionError("resolver violated fail-closed context contract: " + raw)
    return len(mutate), 8

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=DEFAULT)
    p.add_argument("--token", default=None)
    p.add_argument("--kind", default=None)
    p.add_argument("--canonical-id", default=None)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    raw = a.manifest.read_bytes()
    g = json.loads(raw)
    err = issues(g)
    negative = 0
    resolution = 0
    if a.self_test and not err:
        negative, resolution = adversarial(g)
    receipt = {"schema": "rll.chem_context_tokenizer_receipt.v1",
               "status": "PASS_SCOPED_METADATA_ONLY" if not err else "HOLD_INVALID",
               "sha256": hashlib.sha256(raw).hexdigest(),
               "validation_errors": err,
               "negative_mutations": negative,
               "resolver_tests": resolution,
               "claim_allowed": False,
               "physical_validation": "NOT_RUN",
               "hidden_model_heads": "NOT_ACCESSIBLE"}
    if a.token is not None and not err:
        receipt["resolution"] = resolve(g, a.token, kind=a.kind, canonical_id=a.canonical_id)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 2 if err else 0

if __name__ == "__main__":
    raise SystemExit(main())
