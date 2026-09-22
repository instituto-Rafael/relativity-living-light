#!/usr/bin/env python3
"""Fail-closed validator for RLL primordial assurance V2 artifacts."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data/results/rll_primordial_assurance_v2.receipt.json"
HOTQCD = ROOT / "data/inputs/qcd_primordial/hotqcd_2014_eos_fit.v1.json"
EVIDENCE = ROOT / "data/inputs/qcd_primordial/rll_primordial_evidence_registry.v2.json"
ATTENTION = ROOT / "data/inputs/qcd_primordial/rll_primordial_attention_ledger.v1.json"
FIXTURES = ROOT / "data/fixtures/qcd_primordial/rll_primordial_negative_fixtures.v1.json"


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: root must be object")
    return payload


def _source(payload: dict[str, Any], source_id: str) -> dict[str, Any]:
    for row in payload.get("sources", []):
        if row.get("source_id") == source_id:
            return row
    raise ValueError(f"missing evidence source: {source_id}")


def _attention(payload: dict[str, Any], entry_id: str) -> dict[str, Any]:
    for row in payload.get("entries", []):
        if row.get("id") == entry_id:
            return row
    raise ValueError(f"missing attention entry: {entry_id}")


def validate(receipt: dict[str, Any], hotqcd: dict[str, Any], evidence: dict[str, Any], attention: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if receipt.get("publication_effect") != "NONE":
        errors.append("publication_effect must remain NONE")
    gates = receipt.get("gates", {})
    exact_states = {
        "Omega_B0_sign_authority": "PHYSICAL_PROFILE_NONNEGATIVE_RESOLVED",
        "Omega_P0_sign_authority": "PHYSICAL_PROFILE_NONNEGATIVE_RESOLVED_CONDITIONAL_A_MINUS_4",
        "full_SM_g_rho_g_s_numeric_ingestion": "MATERIALIZED_BORSANYI_TABLE_S3",
        "BP_background_BBN_CMB_summary_likelihood": "PASS_BOUND_DERIVED_FROM_PUBLISHED_BBN_CMB_SUMMARIES",
        "direct_RLL_early_universe_likelihood": "TOKEN_VAZIO_RAW_AND_PERTURBATIVE_REPLAY",
        "full_RLL_primordial_verdict": "TOKEN_VAZIO",
    }
    for key, expected in exact_states.items():
        if gates.get(key) != expected:
            errors.append(f"{key} must equal {expected}")
    required_token_vazio = (
        "Omega_B0_P0_perturbation_physics",
        "post_rng_fix_MCMC_reference_receipt",
    )
    for key in required_token_vazio:
        if gates.get(key) != "TOKEN_VAZIO":
            errors.append(f"{key} must remain TOKEN_VAZIO")
    if gates.get("claim_allowed") is not False:
        errors.append("gates.claim_allowed must remain false")
    closure = receipt.get("closure_extensions", {})
    if closure.get("full_SM_gstar", {}).get("status") != "MATERIALIZED_BORSANYI_TABLE_S3":
        errors.append("closure full-SM g-star state must be materialized from Borsanyi Table S3")
    bp = closure.get("BP_physical_profile", {})
    if bp.get("Omega_B0_sign") != "NONNEGATIVE" or bp.get("Omega_P0_sign") != "NONNEGATIVE_CONDITIONAL_RADIATION_LIKE_PROFILE":
        errors.append("B/P physical sign closure must remain non-negative")
    if bp.get("perturbations") != "TOKEN_VAZIO":
        errors.append("B/P perturbations must remain TOKEN_VAZIO")
    bbn_cmb = closure.get("BP_background_BBN_CMB", {})
    if bbn_cmb.get("status") != "PASS_BOUND_DERIVED_FROM_PUBLISHED_BBN_CMB_SUMMARIES":
        errors.append("B/P background BBN+CMB summary likelihood status invalid")
    if bbn_cmb.get("raw_likelihood_replay") is not False:
        errors.append("B/P BBN+CMB summary receipt must not claim raw likelihood replay")
    if bbn_cmb.get("full_PMF_plasma_perturbative_CMB") != "TOKEN_VAZIO":
        errors.append("full PMF/plasma perturbative CMB must remain TOKEN_VAZIO")
    if receipt.get("transition_contract", {}).get("standard_cosmic_QCD") != "CROSSOVER":
        errors.append("standard cosmic QCD contract must remain CROSSOVER")
    if hotqcd.get("superseded_provenance", {}).get("active_use") is not False:
        errors.append("superseded HotQCD result cannot be active")
    try:
        blueprint = _source(evidence, "RMR_BLUEPRINT_METADATA")
        if blueprint.get("kind") != "BLUEPRINT_NOT_AUTHORITY":
            errors.append("RMR blueprint must not be promoted to authoritative prior")
        alice = _source(evidence, "ALICE_LIGHT_ION_FLOW_2026")
        if alice.get("epistemic_type") == "DIRECT_RLL_LIKELIHOOD":
            errors.append("collider QGP cannot be promoted to direct RLL likelihood")
    except ValueError as exc:
        errors.append(str(exc))
    try:
        censorship = _attention(attention, "CENSORSHIP_CLASSIFICATION")
        if censorship.get("epistemic_status") == "DOCUMENTED_CENSORSHIP" and not censorship.get("provenance"):
            errors.append("censorship promotion requires provenance")
    except ValueError as exc:
        errors.append(str(exc))
    if attention.get("claim_allowed") is not False or evidence.get("claim_allowed") is not False:
        errors.append("all registries must keep claim_allowed=false")
    return errors


def set_path(payload: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur: dict[str, Any] = payload
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value


def _decode_mutation_descriptor(descriptor: dict[str, Any]) -> dict[str, Any]:
    path_tokens = {"CLAIM_ALLOWED": "claim_allowed"}
    value_tokens: dict[str, Any] = {"BOOLEAN_TRUE": True, "BOOLEAN_FALSE": False, "NULL": None}
    path_token = descriptor.get("path_token")
    value_token = descriptor.get("value_token")
    if path_token not in path_tokens:
        raise ValueError(f"unknown mutation path token: {path_token}")
    if value_token not in value_tokens:
        raise ValueError(f"unknown mutation value token: {value_token}")
    return {path_tokens[path_token]: value_tokens[value_token]}


def apply_fixture(case: dict[str, Any], base: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], str]:
    mutated = copy.deepcopy(base)
    kind = case["kind"]
    if "mutation" in case:
        mutation = case["mutation"]
    elif "mutation_descriptor" in case:
        descriptor = case["mutation_descriptor"]
        if not isinstance(descriptor, dict):
            raise ValueError("mutation_descriptor must be an object")
        mutation = _decode_mutation_descriptor(descriptor)
    else:
        raise ValueError(f"negative fixture {case.get('id')} has no mutation")
    expected = case["expected_error"]
    if kind in {"receipt", "hotqcd"}:
        for path, value in mutation.items():
            set_path(mutated[kind], path, value)
    elif kind == "attention":
        row = _attention(mutated["attention"], "CENSORSHIP_CLASSIFICATION")
        for path, value in mutation.items():
            prefix = "censorship."
            key = path[len(prefix):] if path.startswith(prefix) else path
            set_path(row, key, value)
    elif kind == "evidence":
        for path, value in mutation.items():
            source_id, field = path.split(".", 1)
            set_path(_source(mutated["evidence"], source_id), field, value)
    else:
        raise ValueError(f"unknown negative fixture kind: {kind}")
    return mutated, expected


def run_negative_fixtures(base: dict[str, dict[str, Any]], fixtures: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for case in fixtures.get("cases", []):
        mutated, expected = apply_fixture(case, base)
        got = validate(mutated["receipt"], mutated["hotqcd"], mutated["evidence"], mutated["attention"])
        if expected not in got:
            errors.append(f"negative fixture {case.get('id')} did not fail closed: expected {expected!r}, got {got!r}")
    return errors


def run() -> dict[str, Any]:
    base = {"receipt": load(RECEIPT), "hotqcd": load(HOTQCD), "evidence": load(EVIDENCE), "attention": load(ATTENTION)}
    fixtures = load(FIXTURES)
    direct_errors = validate(base["receipt"], base["hotqcd"], base["evidence"], base["attention"])
    negative_errors = run_negative_fixtures(base, fixtures)
    errors = direct_errors + negative_errors
    return {
        "schema": "rll.primordial_assurance.validator_receipt.v1",
        "status": "PASS" if not errors else "FAIL",
        "claim_allowed": False,
        "negative_fixture_count": len(fixtures.get("cases", [])),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
