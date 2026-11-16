#!/usr/bin/env python3
"""Validate the six SGPT M87* pre-execution locks.

Structural/governance validator only. It cannot validate M87* astrophysics,
close G4-G7, or promote claim_allowed.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "contracts" / "m87"
TOKEN = "TOKEN_VAZIO"

FILES = {
    "regime": "source_regime_admissibility.v1.json",
    "times": "process_timescale_registry.v1.json",
    "data": "data_custody_and_transform_dag.v1.json",
    "stats": "statistical_analysis_lock.v1.json",
    "repro": "reproducibility_environment_lock.v1.json",
    "claims": "claim_ladder.v1.json",
}


class LockError(ValueError):
    pass


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise LockError(msg)


def load_all(base: Path = BASE) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key, name in FILES.items():
        path = base / name
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
        require(isinstance(value, dict), f"{name}: root must be object")
        out[key] = value
    return out


def validate_regime(d: dict[str, Any]) -> None:
    require(d.get("schema") == "rll.sgpt.m87.source-regime-admissibility/v1", "regime schema drift")
    require(d.get("source") == "M87*", "regime source drift")
    require(d.get("claim_allowed") is False, "regime cannot promote claim")
    allowed = set(d.get("allowed_states", []))
    require({TOKEN, "APPLICABLE", "NOT_APPLICABLE_WITH_JUSTIFICATION", "OUT_OF_DOMAIN", "EXECUTED"}.issubset(allowed), "regime state enum incomplete")
    source = d.get("source_state_required", {})
    require(source and all(v == TOKEN for v in source.values()), "source state cannot be invented")
    regimes = d.get("regimes", {})
    require(regimes, "regime map missing")
    for name, item in regimes.items():
        require(item.get("state") == TOKEN, f"{name}: applicability cannot be pre-promoted")
        require(item.get("evidence") == TOKEN, f"{name}: evidence cannot be invented")


def validate_times(d: dict[str, Any]) -> None:
    require(d.get("schema") == "rll.sgpt.m87.process-timescale-registry/v1", "timescale schema drift")
    require(d.get("definition") == "D_i=tau_residence/tau_i", "timescale definition drift")
    require(d.get("claim_allowed") is False, "timescale lock cannot promote claim")
    processes = d.get("processes", {})
    require(len(processes) >= 10, "timescale process set incomplete")
    for name, item in processes.items():
        fields = ("tau", "units", "rate_model", "source", "domain", "receipt")
        require(all(item.get(field) == TOKEN for field in fields), f"{name}: process rate cannot be pre-filled")


def validate_data(d: dict[str, Any]) -> None:
    require(d.get("schema") == "rll.sgpt.m87.data-custody-transform-dag/v1", "data DAG schema drift")
    require(d.get("claim_allowed") is False, "data lock cannot promote claim")
    stages = d.get("stages", [])
    ids = [x.get("id") for x in stages]
    expected = [
        "S0_OFFICIAL_BYTES", "S1_CALIBRATION", "S2_FLAG_FILTER", "S3_OBSERVABLE_VECTOR",
        "S4_COVARIANCE_SYSTEMATICS", "S5_LIKELIHOOD_INPUT", "S6_FIT_OUTPUT", "S7_COMPARISON_RECEIPT",
    ]
    require(ids == expected, "data transformation stage/order drift")
    for item in stages:
        for field in ("input_sha256", "output_sha256", "software_commit", "config_hash", "units", "calibration_state", "systematics", "operator", "receipt"):
            require(item.get(field) == TOKEN, f"{item.get('id')}: {field} cannot be pre-filled")
    require(d.get("rights_status") == TOKEN, "rights cannot be inferred")


def validate_stats(d: dict[str, Any]) -> None:
    require(d.get("schema") == "rll.sgpt.m87.statistical-analysis-lock/v1", "statistics schema drift")
    require(d.get("claim_allowed") is False, "statistics lock cannot promote claim")
    for key in ("primary_observable_vector", "covariance_model", "likelihood", "priors", "primary_metric", "complexity_penalty", "multiplicity_rule", "stopping_rule", "accept_reject_threshold", "numerical_failure_policy"):
        require(d.get(key) == TOKEN, f"{key} cannot be selected before source/data binding")
    require(d.get("retrospective_2018_semantics") == "RETROSPECTIVE_REPLICATION_SET_OR_PROCEDURAL_HOLDOUT_NOT_BLIND", "2018 semantics weakened")
    require(d.get("post_hoc_parameter_tuning") == "FORBIDDEN", "post-hoc tuning must remain forbidden")


def validate_repro(d: dict[str, Any]) -> None:
    require(d.get("schema") == "rll.sgpt.m87.reproducibility-environment-lock/v1", "repro schema drift")
    require(d.get("claim_allowed") is False, "repro lock cannot promote claim")
    env = d.get("execution_environment", {})
    require(env and all(v == TOKEN for v in env.values()), "execution environment cannot be invented")
    rep = d.get("independent_reproduction", {})
    require(rep.get("state") == TOKEN, "independent reproduction cannot be pre-promoted")
    require(rep.get("selected_independence_axis") == TOKEN, "independence axis cannot be invented")
    require(rep.get("agreement_tolerance") == TOKEN, "agreement tolerance cannot be post-selected")
    require(len(rep.get("must_differ_in_at_least_one", [])) >= 5, "independence axes incomplete")


def validate_claims(d: dict[str, Any]) -> None:
    require(d.get("schema") == "rll.sgpt.m87.claim-ladder/v1", "claim ladder schema drift")
    require(d.get("claim_allowed") is False, "claim ladder cannot self-promote")
    levels = d.get("levels", [])
    ids = [x.get("id") for x in levels]
    require(len(ids) == 7 and ids[0].startswith("L0_") and ids[-1].startswith("L6_"), "claim ladder must span L0-L6")
    require(d.get("current_level") == "L1_SOFTWARE_IMPLEMENTATION_PASS", "current claim level cannot exceed available software receipt")
    require("L1->L6" in d.get("forbidden_jumps", []), "direct software-to-new-physics jump must remain forbidden")
    ceiling = d.get("hypothesis_ceiling", {})
    require(ceiling.get("H_down") == "L1_SOFTWARE_IMPLEMENTATION_PASS", "H_down ceiling pre-promoted")
    require(ceiling.get("H_logistic_photonic") == "L1_SOFTWARE_IMPLEMENTATION_PASS", "logistic ceiling pre-promoted")


def validate_all(docs: dict[str, dict[str, Any]]) -> None:
    validate_regime(docs["regime"])
    validate_times(docs["times"])
    validate_data(docs["data"])
    validate_stats(docs["stats"])
    validate_repro(docs["repro"])
    validate_claims(docs["claims"])


def expect_rejected(base: dict[str, dict[str, Any]], label: str, mutate: Callable[[dict[str, dict[str, Any]]], None]) -> None:
    candidate = deepcopy(base)
    mutate(candidate)
    try:
        validate_all(candidate)
    except LockError:
        return
    raise LockError(f"illegal lock mutation accepted: {label}")


def selftest(docs: dict[str, dict[str, Any]]) -> list[str]:
    cases: list[tuple[str, Callable[[dict[str, dict[str, Any]]], None]]] = [
        ("invent-M87-nuclear-regime", lambda x: x["regime"]["regimes"]["nuclear_network"].__setitem__("state", "APPLICABLE")),
        ("invent-M87-spin-QED", lambda x: x["regime"]["regimes"]["spin_Landau_QED"].__setitem__("state", "APPLICABLE")),
        ("invent-reconnection-rate", lambda x: x["times"]["processes"]["reconnection"].__setitem__("tau", 1.0)),
        ("invent-rate-source", lambda x: x["times"]["processes"]["cooling"].__setitem__("source", "memory")),
        ("skip-byte-hash", lambda x: x["data"]["stages"][0].__setitem__("output_sha256", "0" * 64)),
        ("infer-rights", lambda x: x["data"].__setitem__("rights_status", "PUBLIC_MEANS_REUSABLE")),
        ("choose-identity-covariance", lambda x: x["stats"].__setitem__("covariance_model", "identity")),
        ("preselect-AIC", lambda x: x["stats"].__setitem__("primary_metric", "AIC")),
        ("call-2018-blind", lambda x: x["stats"].__setitem__("retrospective_2018_semantics", "BLIND_PROSPECTIVE_PREDICTION")),
        ("invent-independent-reproduction", lambda x: x["repro"]["independent_reproduction"].__setitem__("state", "PASS")),
        ("postselect-tolerance", lambda x: x["repro"]["independent_reproduction"].__setitem__("agreement_tolerance", "after_results")),
        ("jump-L1-L6", lambda x: x["claims"].__setitem__("current_level", "L6_NEW_PHYSICS_CLAIM_ELIGIBLE")),
        ("promote-Hdown", lambda x: x["claims"]["hypothesis_ceiling"].__setitem__("H_down", "L6_NEW_PHYSICS_CLAIM_ELIGIBLE")),
        ("claim-allowed", lambda x: x["claims"].__setitem__("claim_allowed", True)),
    ]
    rejected: list[str] = []
    for label, mutate in cases:
        expect_rejected(docs, label, mutate)
        rejected.append(label)
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        docs = load_all(args.base)
        validate_all(docs)
        rejected = selftest(docs) if args.selftest else []
        receipt = {
            "schema": "rll.sgpt.m87.execution-locks-receipt/v1",
            "status": "PASS_LOCKS_CONTRACT_ONLY",
            "locks": list(FILES.values()),
            "rejected_illegal_mutations": rejected,
            "source_regime_execution": TOKEN,
            "process_timescale_execution": TOKEN,
            "data_ingestion": TOKEN,
            "statistical_fit": TOKEN,
            "independent_reproduction": TOKEN,
            "G4_BASELINE": TOKEN,
            "G5_REPRODUCTION": TOKEN,
            "G6_PREDICTION": TOKEN,
            "G7_CLAIM_PROMOTION": TOKEN,
            "scientific_validation": TOKEN,
            "claim_allowed": False,
        }
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, sort_keys=True))
    except (OSError, json.JSONDecodeError, LockError) as exc:
        print(f"SGPT_M87_EXECUTION_LOCKS_FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
