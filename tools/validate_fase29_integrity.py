#!/usr/bin/env python3
"""Validate FASE 29 through thirty non-compensatory scientific-integrity lenses."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LENSES_PATH = Path("data/contracts/fase29_integrity_lenses.v1.json")
BUNDLE_PATH = Path("data/contracts/rll_falsifier_bundle.json")
RIGHTS_PATH = Path("data/contracts/dataset_rights_manifest.json")
LEDGER_PATH = Path("results/state_transition_ledger.jsonl")
REPORT_PATH = Path("artifacts/fase29-integrity/validation.json")

EXPECTED_WORDS = [
    "aritmética", "licença", "relógio", "genealogia", "assimetria",
    "silêncio", "redundância", "reversibilidade", "granularidade", "fronteira",
    "entropia", "custódia", "causalidade", "ambiguidade", "cobertura",
    "desvio", "identidade", "proveniência", "saturação", "refutação",
    "latência", "diversidade", "monotonicidade", "fragilidade", "observabilidade",
    "proporcionalidade", "independência", "conservação", "reparabilidade", "legado",
]


def read_json(root: Path, relative: Path) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def read_ledger(root: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (root / LEDGER_PATH).read_text(encoding="utf-8").splitlines() if line.strip()]


def iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def event_digest(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def threshold_pass(item: dict[str, Any]) -> bool:
    value = item["result"]
    threshold = item["threshold_value"]
    operator = item["operator"]
    if operator == "lt":
        return value < threshold
    if operator == "gt":
        return value > threshold
    if operator == "in_interval":
        return threshold[0] <= value <= threshold[1]
    raise ValueError(f"unsupported operator: {operator}")


def validate_documents(
    lenses: dict[str, Any],
    bundle: dict[str, Any],
    rights: dict[str, Any],
    ledger: list[dict[str, Any]],
    root: Path = ROOT,
) -> dict[str, list[str]]:
    errors = {word: [] for word in EXPECTED_WORDS}

    def require(word: str, condition: bool, message: str) -> None:
        if not condition:
            errors[word].append(message)

    lens_rows = lenses.get("lenses", [])
    words = [row.get("word") for row in lens_rows]
    require("identidade", lenses.get("schema") == "rll.fase29_integrity_lenses.v1", "invalid lenses schema")
    require("cobertura", len(lens_rows) == 30, "exactly thirty lenses required")
    require("redundância", len(set(words)) == len(words), "lens words must be unique")
    require("legado", words == EXPECTED_WORDS, "lenses must preserve canonical order and vocabulary")
    require("fronteira", lenses.get("claim_allowed") is False, "lenses claim boundary must be false")
    require("assimetria", lenses.get("aggregation_rule") == "NON_COMPENSATORY", "aggregation must be non-compensatory")

    falsifiers = bundle.get("falsifiers", [])
    by_id = {item.get("id"): item for item in falsifiers}
    expected_ids = {f"F-COS-{index:02d}" for index in range(1, 6)}
    require("cobertura", set(by_id) == expected_ids and len(falsifiers) == 5, "F-COS-01..05 required exactly once")
    require("redundância", len(by_id) == len(falsifiers), "duplicate falsifier IDs")
    require("identidade", bundle.get("schema") == "rll.falsifier_bundle.v2", "invalid falsifier schema")
    require("fronteira", bundle.get("claim_allowed") is False, "bundle claim_allowed must be false")
    require("fronteira", all(item.get("claim_allowed") is False for item in falsifiers), "each falsifier must block claims")

    statuses = {"PASS": [], "FAIL": [], "TOKEN_VAZIO": []}
    for item in falsifiers:
        status = item.get("status")
        require("desvio", status in statuses, f"invalid status for {item.get('id')}")
        if status in statuses:
            statuses[status].append(item["id"])
            require("desvio", threshold_pass(item) == (status == "PASS"), f"threshold/status mismatch for {item['id']}")
        require("proveniência", bool(item.get("method")) and bool(item.get("source_phase")), f"method/source phase missing for {item.get('id')}")
        source = item.get("source", "")
        require("custódia", bool(source), f"source missing for {item.get('id')}")
        require("observabilidade", bool(source) and (root / source).exists(), f"source artifact not found: {source}")
        require("independência", item.get("holdout_status") == "TOKEN_VAZIO", f"holdout must remain TOKEN_VAZIO for {item.get('id')}")

    summary = bundle.get("summary", {})
    require("proporcionalidade", summary.get("total") == len(falsifiers), "summary total mismatch")
    require("proporcionalidade", summary.get("pass") == len(statuses["PASS"]), "summary PASS mismatch")
    require("proporcionalidade", summary.get("fail") == len(statuses["FAIL"]), "summary FAIL mismatch")
    require("proporcionalidade", summary.get("token_vazio") == len(statuses["TOKEN_VAZIO"]), "summary TOKEN_VAZIO mismatch")
    require("proporcionalidade", set(summary.get("pass_ids", [])) == set(statuses["PASS"]), "pass_ids mismatch")
    require("proporcionalidade", set(summary.get("fail_ids", [])) == set(statuses["FAIL"]), "fail_ids mismatch")
    require("saturação", summary.get("claim_allowed") is False, "summary cannot be promoted by vote counting")
    require("assimetria", bool(statuses["FAIL"]) and bundle.get("claim_allowed") is False, "failed falsifiers must block global claim")

    f1 = by_id.get("F-COS-01", {})
    expected_aic_rll = f1.get("chi2_rll", math.nan) + 2 * f1.get("parameter_count_rll", math.nan)
    expected_aic_lcdm = f1.get("chi2_lcdm", math.nan) + 2 * f1.get("parameter_count_lcdm", math.nan)
    expected_delta = expected_aic_rll - expected_aic_lcdm
    require("aritmética", math.isclose(f1.get("aic_rll", math.nan), expected_aic_rll, abs_tol=1e-9), "RLL AIC does not derive")
    require("aritmética", math.isclose(f1.get("aic_lcdm", math.nan), expected_aic_lcdm, abs_tol=1e-9), "LCDM AIC does not derive")
    require("aritmética", math.isclose(f1.get("result", math.nan), expected_delta, abs_tol=1e-9), "DeltaAIC does not derive")
    require("granularidade", f1.get("release_observation_count", 0) > f1.get("used_observation_count", 0), "release and used counts must be distinct")
    require("ambiguidade", "parameter_count_rll" in f1 and "parameter_count_lcdm" in f1, "parameter counts must not be called dof")

    f2 = by_id.get("F-COS-02", {})
    reduced = f2.get("chi2_rll", math.nan) / f2.get("degrees_of_freedom", math.nan)
    require("aritmética", math.isclose(f2.get("result", math.nan), reduced, rel_tol=2e-4), "reduced chi2 does not derive")
    require("ambiguidade", f2.get("degrees_of_freedom") == f2.get("used_observation_count") - f2.get("parameter_count"), "dof must equal n-k")
    require("fragilidade", "not evidence of superiority" in f2.get("limitation", ""), "low chi2 limitation missing")

    f3 = by_id.get("F-COS-03", {})
    require("causalidade", "does not by itself prove" in f3.get("limitation", ""), "F-COS-03 causal boundary missing")
    require("refutação", f3.get("status") == "FAIL" and bool(f3.get("falsification_strength")), "F-COS-03 refutation scope missing")
    f4 = by_id.get("F-COS-04", {})
    derived_lnb = f4.get("logZ_rll", math.nan) - f4.get("logZ_lcdm", math.nan)
    require("aritmética", math.isclose(f4.get("result", math.nan), derived_lnb, abs_tol=1e-12), "lnB10 does not derive from logZ")
    require("fragilidade", f4.get("result_uncertainty", 0) > 0, "Bayes uncertainty missing")
    require("refutação", "not a universal proof" in f4.get("limitation", ""), "Bayes limitation missing")
    f5 = by_id.get("F-COS-05", {})
    derived_delta = f5.get("result", math.nan) - f5.get("chi2_lcdm", math.nan)
    require("aritmética", math.isclose(f5.get("comparative_delta_chi2_rll_minus_lcdm", math.nan), derived_delta, abs_tol=1e-9), "DESI comparative delta does not derive")
    require("fragilidade", f5.get("threshold_provenance") == "CONVENTION", "arbitrary threshold must be disclosed")
    require("saturação", f5.get("promotion_effect") == "NONE", "weak sanity PASS cannot promote claim")
    require("diversidade", set(bundle.get("evidence_contexts", {})) == {"pantheon_point_fit", "fase20_joint_bayesian", "desi_nominal"}, "evidence contexts must remain separate")

    datasets = rights.get("datasets", [])
    gaps = rights.get("gaps", [])
    require("identidade", rights.get("schema") == "rll.dataset_rights_manifest.v2", "invalid rights schema")
    require("fronteira", rights.get("claim_allowed") is False and rights.get("training_allowed") is False and rights.get("redistribution_allowed") is False, "rights global gates must fail closed")
    require("redundância", len({item.get("dataset_id") for item in datasets}) == len(datasets), "duplicate dataset IDs")
    for item in datasets:
        evidence = item.get("license_evidence")
        require("silêncio", evidence is not None and item.get("license_expression") is not None, f"unknown rights must not be null: {item.get('dataset_id')}")
        if item.get("license_verified"):
            require("licença", evidence not in ("", "TOKEN_VAZIO"), f"verified license lacks evidence: {item.get('dataset_id')}")
        require("licença", item.get("rights_complete") is bool(item.get("license_verified")), f"rights_complete mismatch: {item.get('dataset_id')}")
        require("independência", item.get("training_allowed") is False, f"training must remain blocked: {item.get('dataset_id')}")
        require("fronteira", item.get("redistribution_allowed") is False, f"redistribution must remain blocked: {item.get('dataset_id')}")
        require("reversibilidade", bool(item.get("next_action")) and bool(item.get("exit_criteria")), f"repair path missing: {item.get('dataset_id')}")
    verified = sum(bool(item.get("license_verified")) for item in datasets)
    complete = sum(bool(item.get("rights_complete")) for item in datasets)
    rsummary = rights.get("summary", {})
    require("entropia", rsummary.get("rights_incomplete") == len(datasets) - complete, "rights unknown count mismatch")
    require("proporcionalidade", rsummary.get("rights_complete") == complete and rsummary.get("license_verified") == verified, "rights summary mismatch")

    all_gaps = list(bundle.get("gaps", [])) + gaps
    for gap in all_gaps:
        require("reparabilidade", all(bool(gap.get(key)) for key in ("owner", "next_action", "exit_criteria")), f"gap repair metadata missing: {gap.get('gap_id')}")
        require("fronteira", gap.get("state") in ("TOKEN_VAZIO", "OPEN"), f"gap prematurely closed: {gap.get('gap_id')}")

    require("cobertura", len(ledger) == 17, "ledger must contain 17 initial events")
    require("redundância", len({event.get("event_id") for event in ledger}) == len(ledger), "duplicate event IDs")
    previous_hash = "GENESIS"
    previous_recorded = None
    for index, event in enumerate(ledger, start=1):
        require("identidade", event.get("event_id") == f"EVT-{index:03d}", "event IDs must be sequential")
        require("legado", event.get("schema") == "rll.state_transition_event.v2", f"legacy schema at {event.get('event_id')}")
        require("relógio", bool(event.get("effective_at")) and bool(event.get("recorded_at")), f"dual time missing: {event.get('event_id')}")
        effective, recorded = iso(event["effective_at"]), iso(event["recorded_at"])
        require("latência", recorded >= effective, f"recorded before effective: {event.get('event_id')}")
        if previous_recorded is not None:
            require("monotonicidade", recorded > previous_recorded, f"recording order not monotonic: {event.get('event_id')}")
        previous_recorded = recorded
        require("genealogia", event.get("previous_event_sha256") == previous_hash, f"previous hash mismatch: {event.get('event_id')}")
        digest = event_digest(event)
        require("conservação", event.get("event_sha256") == digest, f"event hash mismatch: {event.get('event_id')}")
        previous_hash = digest
        require("fronteira", event.get("claim_allowed") is False, f"ledger claim promoted: {event.get('event_id')}")
        require("custódia", bool(event.get("refs")), f"event refs missing: {event.get('event_id')}")
        require("genealogia", event.get("supersedes") is None or event.get("supersedes") in {row.get("event_id") for row in ledger[:index-1]}, f"supersedes unknown event: {event.get('event_id')}")
    require("conservação", previous_hash == ledger[-1].get("event_sha256"), "ledger terminal hash mismatch")

    return errors


def validate_root(root: Path = ROOT) -> dict[str, Any]:
    lenses = read_json(root, LENSES_PATH)
    bundle = read_json(root, BUNDLE_PATH)
    rights = read_json(root, RIGHTS_PATH)
    ledger = read_ledger(root)
    errors = validate_documents(lenses, bundle, rights, ledger, root)
    failed = {word: messages for word, messages in errors.items() if messages}
    return {
        "schema": "rll.fase29_integrity_validation.v1",
        "status": "PASS" if not failed else "FAIL",
        "claim_allowed": False,
        "lens_count": len(EXPECTED_WORDS),
        "passed_lenses": [word for word in EXPECTED_WORDS if not errors[word]],
        "failed_lenses": failed,
        "ledger_terminal_sha256": ledger[-1]["event_sha256"] if ledger else "TOKEN_VAZIO",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = validate_root(args.root)
    text = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.write_report:
        path = args.root / REPORT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if args.strict and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
