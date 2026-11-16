#!/usr/bin/env python3
"""Validate the SGPT M87* source-specific fire-test preregistration.

This validator protects the experiment design before result-producing ingestion.
It cannot validate astrophysical truth and it cannot promote any SGPT claim.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "data" / "contracts" / "sgpt_m87_firetest.v1.json"
TOKEN_VAZIO = "TOKEN_VAZIO"
EXPECTED_SCHEMA = "rll.strong_gravity.sgpt_m87_firetest.v1"
EXPECTED_PARENT = "e287ef13be4d5e6d366f29e234c8a5d113d21729"
EXPECTED_EHT_PIPELINE = "80d230e76c08edd31548e7cfe61dc7cf94300780"
EXPECTED_BASELINES = [
    "ideal_GRMHD",
    "resistive_GRMHD",
    "two_temperature_GRRMHD",
    "GRPIC",
    "general_relativistic_radiative_transfer",
]
EXPECTED_NEGATIVE_CONTROLS = [
    "drop_Theta",
    "drop_M_f",
    "drop_R_ram",
    "flip_Theta_sign",
    "shuffle_predictor_variables",
    "permute_temporal_targets",
    "baseline_only",
]
EXPECTED_GATES = [
    "G0_IDENTITY",
    "G1_MATHEMATICS",
    "G2_DETERMINISM",
    "G3_ADVERSARIAL",
    "G4_BASELINE",
    "G5_REPRODUCTION",
    "G6_PREDICTION",
    "G7_CLAIM_PROMOTION",
]
EXPECTED_DATA = {
    "EHT_2017_L1": "10.25739/kat4-na03",
    "EHT_2019_D01_01": "10.25739/g85n-f134",
    "EHT_2021_D02_01": "10.25739/mhh2-cw46",
    "EHT_2023_D01_01": "10.25739/q46m-m857",
    "EHT_2024_D01_01": "10.25739/epm5-r371",
}


class FiretestError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FiretestError(message)


def load(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "contract root must be object")
    return value


def validate(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract.get("schema") == EXPECTED_SCHEMA, "schema drift")
    require(contract.get("id") == "SGPT_M87_FIRETEST_V1", "id drift")
    require(contract.get("authority") == "instituto-Rafael/relativity-living-light", "authority drift")
    require(contract.get("parent_model") == "B08_SGPT_V1", "parent model drift")
    require(contract.get("parent_model_commit") == EXPECTED_PARENT, "parent SGPT commit drift")
    require(contract.get("analysis_class") == "RETROSPECTIVE_EXTERNAL_SOURCE_PREREGISTRATION", "analysis class drift")
    require(contract.get("prospective_claim") is False, "already-public EHT products cannot be relabelled prospective")
    require(contract.get("claim_allowed") is False, "preregistration cannot self-promote claim")

    source = contract.get("source")
    require(isinstance(source, dict) and source.get("object") == "M87*", "source must remain M87*")
    params = source.get("parameter_values")
    require(isinstance(params, dict), "source parameter block missing")
    require(set(params) == {"M", "a_star", "dot_M", "B", "rho", "T_e"}, "source parameter key drift")
    for key, value in params.items():
        require(value == TOKEN_VAZIO, f"{key} cannot be filled before source-bound priors are recorded")

    products = contract.get("public_data_sources")
    require(isinstance(products, list) and products, "public_data_sources missing")
    indexed = {x.get("id"): x for x in products if isinstance(x, dict)}
    require(len(indexed) == len(products), "duplicate/invalid data source id")
    for product_id, doi in EXPECTED_DATA.items():
        require(product_id in indexed, f"missing data product {product_id}")
        require(indexed[product_id].get("doi") == doi, f"DOI drift for {product_id}")
        require(indexed[product_id].get("file_sha256") == TOKEN_VAZIO, f"{product_id} bytes not yet ingested; SHA cannot be invented")
        require(indexed[product_id].get("ingestion_state") == TOKEN_VAZIO, f"{product_id} ingestion cannot be pre-promoted")
    pipeline = indexed.get("EHT_2019_D01_02")
    require(isinstance(pipeline, dict), "public EHT imaging pipeline reference missing")
    require(pipeline.get("repository") == "eventhorizontelescope/2019-D01-02", "EHT pipeline repository drift")
    require(pipeline.get("commit") == EXPECTED_EHT_PIPELINE, "EHT pipeline pin drift")
    require(pipeline.get("ingestion_state") == TOKEN_VAZIO, "pipeline execution cannot be claimed before acquisition")

    split = contract.get("split")
    require(isinstance(split, dict), "split block missing")
    require(split.get("retrospective_holdout") == ["EHT_2024_D01_01"], "2018 holdout drift")
    require("not be described as a prospective blind prediction" in split.get("holdout_warning", ""), "retrospective holdout warning missing")

    hypotheses = contract.get("hypotheses")
    require(isinstance(hypotheses, list) and len(hypotheses) == 3, "hypothesis set drift")
    hmap = {x.get("id"): x for x in hypotheses}
    require(set(hmap) == {"H_down", "H_logistic_photonic", "H_temporal_ordering"}, "hypothesis id drift")
    require(hmap["H_temporal_ordering"].get("state") == "TOKEN_VAZIO_NOT_RUN", "temporal hypothesis cannot be pre-run")
    require(hmap["H_temporal_ordering"].get("primary_test") == TOKEN_VAZIO, "temporal primary test requires adequate frozen cadence data")
    for item in hypotheses:
        require(isinstance(item.get("falsifier"), str) and item["falsifier"], f"falsifier missing for {item.get('id')}")

    require(contract.get("mandatory_baselines") == EXPECTED_BASELINES, "mandatory baseline drift")
    require(contract.get("negative_controls") == EXPECTED_NEGATIVE_CONTROLS, "negative control drift")

    obs = contract.get("observables")
    require(isinstance(obs, dict), "observables block missing")
    for key in ("exact_primary_vector", "covariance_model", "likelihood"):
        require(obs.get(key) == TOKEN_VAZIO, f"{key} must be frozen later from real source metadata, not invented now")

    stats = contract.get("statistics")
    require(isinstance(stats, dict), "statistics block missing")
    require(stats.get("primary_metric") == TOKEN_VAZIO, "primary metric must remain unchosen until data format/covariance is bound")
    require(stats.get("complexity_penalty") == TOKEN_VAZIO, "complexity penalty must remain unchosen until comparison family is fixed")
    require(stats.get("post_hoc_parameter_tuning") == "FORBIDDEN", "post-hoc tuning boundary weakened")

    require(contract.get("gate_order") == EXPECTED_GATES, "gate order drift")
    gates = contract.get("gates")
    require(isinstance(gates, dict) and list(gates) == EXPECTED_GATES, "gate map/order drift")
    for gate, state in gates.items():
        require(state == TOKEN_VAZIO, f"source preregistration cannot mark {gate} PASS")

    state = contract.get("current_state")
    require(isinstance(state, dict), "current_state missing")
    require(state.get("contract") == "PREREGISTERED_UNEXECUTED", "contract state drift")
    for key in (
        "data_ingested",
        "source_parameters_frozen",
        "observable_vector_frozen",
        "baseline_models_executed",
        "negative_controls_executed",
        "retrospective_holdout_executed",
    ):
        require(state.get(key) is False, f"{key} cannot be true in the source preregistration")
    require(state.get("independent_replication") == TOKEN_VAZIO, "independent replication cannot self-close")
    require(state.get("scientific_validation") == TOKEN_VAZIO, "scientific validation cannot self-close")
    require(state.get("claim_allowed") is False, "current_state claim boundary weakened")

    return {
        "status": "PASS_PREREGISTRATION_CONTRACT_ONLY",
        "source": "M87*",
        "data_products": len(products),
        "baselines": len(EXPECTED_BASELINES),
        "negative_controls": len(EXPECTED_NEGATIVE_CONTROLS),
        "claim_allowed": False,
        "scientific_validation": TOKEN_VAZIO,
    }


def expect_rejected(base: dict[str, Any], label: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    candidate = deepcopy(base)
    mutate(candidate)
    try:
        validate(candidate)
    except FiretestError:
        return
    raise FiretestError(f"illegal preregistration mutation accepted: {label}")


def selftest(contract: dict[str, Any]) -> list[str]:
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("prospective-relabel", lambda x: x.__setitem__("prospective_claim", True)),
        ("invent-mass", lambda x: x["source"]["parameter_values"].__setitem__("M", 6.5e9)),
        ("invent-file-sha", lambda x: x["public_data_sources"][0].__setitem__("file_sha256", "0" * 64)),
        ("drop-GRPIC", lambda x: x["mandatory_baselines"].remove("GRPIC")),
        ("drop-negative-control", lambda x: x["negative_controls"].pop()),
        ("temporal-pre-run", lambda x: x["hypotheses"][2].__setitem__("state", "PASS")),
        ("invent-covariance", lambda x: x["observables"].__setitem__("covariance_model", "identity")),
        ("preselect-metric", lambda x: x["statistics"].__setitem__("primary_metric", "AIC")),
        ("G4-source-pass", lambda x: x["gates"].__setitem__("G4_BASELINE", "PASS")),
        ("claim-promotion", lambda x: x["current_state"].__setitem__("claim_allowed", True)),
        ("holdout-executed", lambda x: x["current_state"].__setitem__("retrospective_holdout_executed", True)),
    ]
    rejected: list[str] = []
    for label, mutate in cases:
        expect_rejected(contract, label, mutate)
        rejected.append(label)
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    try:
        contract = load(args.contract)
        result = validate(contract)
        rejected = selftest(contract) if args.selftest else []
        result["rejected_illegal_mutations"] = rejected
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, FiretestError) as exc:
        print(f"SGPT_M87_FIRETEST_FAIL: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
