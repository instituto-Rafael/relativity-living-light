#!/usr/bin/env python3
"""Validate bounded external evidence for the M87* SGPT fire test.

This validates provenance/rights/custody structure only. It deliberately accepts
provider-blocked file SHA-256 fields as unresolved and rejects invented hashes.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "evidence" / "m87" / "source_state_evidence.v1.json"
CUSTODY = ROOT / "data" / "evidence" / "m87" / "data_custody_metadata.v1.json"
TOKEN_PREFIX = "TOKEN_VAZIO"


class EvidenceError(ValueError):
    pass


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise EvidenceError(msg)


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: root must be object")
    return value


def token(value: object) -> bool:
    return isinstance(value, str) and value.startswith(TOKEN_PREFIX)


def validate_source(d: dict) -> None:
    require(d.get("schema") == "rll.sgpt.m87.source-state-evidence/v1", "source schema drift")
    require(d.get("source") == "M87*", "source object drift")
    require(d.get("claim_allowed") is False, "source evidence cannot promote claim")
    b = d.get("observational_or_published_bindings", {})
    require(b.get("M", {}).get("value") == 6.5e9, "mass binding drift")
    require(b.get("dot_M", {}).get("min") == 3e-4 and b.get("dot_M", {}).get("max") == 2e-3, "Mdot range drift")
    require(b.get("B", {}).get("min") == 1.0 and b.get("B", {}).get("max") == 30.0, "B range drift")
    require(b.get("T_e", {}).get("min") == 1.0e10 and b.get("T_e", {}).get("max") == 1.2e11, "Te range drift")
    require(b.get("n_e", {}).get("min") == 1.0e4 and b.get("n_e", {}).get("max") == 1.0e7, "ne range drift")
    for key in ("dot_M", "B", "T_e", "n_e"):
        require("source" in b[key] and "doi" in b[key], f"{key}: source/DOI missing")
    unbound = d.get("deliberately_unbound_source_parameters", {})
    for key in ("a_star", "T_i", "Y_e", "compactness", "rho_direct"):
        require(token(unbound.get(key)), f"{key}: unresolved source parameter was silently filled")


def validate_custody(d: dict) -> None:
    require(d.get("schema") == "rll.sgpt.m87.data-custody-metadata/v1", "custody schema drift")
    require(d.get("claim_allowed") is False, "custody evidence cannot promote claim")
    products = d.get("products", {})
    for key in ("EHT_2019_D01_01", "EHT_2023_D01_01", "EHT_2021_D02_01", "EHT_2017_L1", "EHT_2024_D01_01"):
        require(key in products, f"missing product {key}")

    for key in ("EHT_2019_D01_01", "EHT_2023_D01_01", "EHT_2017_L1"):
        require(products[key].get("license_at_dataset_level") == "Open Data Commons Public Domain Dedication and License (PDDL)", f"{key}: PDDL metadata lost")
        require(token(products[key].get("file_sha256")), f"{key}: file SHA-256 cannot be fabricated")

    mwl = products["EHT_2021_D02_01"]
    require(mwl.get("official_public_repository") == "eventhorizontelescope/2021-D02-01", "MWL repository drift")
    require(mwl.get("repository_commit") == "1ed2f8bb947336b11c04767cebcbcf7888f86494", "MWL commit drift")
    f = mwl.get("primary_small_file", {})
    require(f.get("path") == "m87_2017_mwl_spectrum.csv", "MWL path drift")
    require(f.get("git_blob_sha1") == "160859ba23f0d0c9158bde7531cbcb2524be969c", "MWL blob drift")
    require(token(f.get("file_sha256")), "MWL SHA-256 cannot be invented without raw-byte materialization")
    require(f.get("content_read_state") == "READ_THROUGH_GITHUB_CONTENT_API", "MWL read state drift")

    l1 = products["EHT_2017_L1"]
    checksum = l1.get("official_checksum_resource", {})
    require(checksum.get("name") == "2016.1.01154.V.sha256sums", "L1 checksum resource name drift")
    require(checksum.get("resource_id") == "940eea05-06b8-413f-a729-619f670a9b66", "L1 checksum resource id drift")
    require(token(checksum.get("checksum_content")), "L1 checksum content cannot be invented")

    holdout = products["EHT_2024_D01_01"]
    require(holdout.get("role") == "RETROSPECTIVE_REPLICATION_SET_NOT_BLIND", "2018 semantics weakened")
    require(holdout.get("ingestion_state") == "WITHHELD_FROM_DEVELOPMENT_EXECUTION", "2018 development isolation weakened")

    provider = d.get("provider_observation", {})
    require(provider.get("scientific_interpretation") == "NONE", "provider access failure cannot become scientific evidence")
    state = d.get("current_custody_state", {})
    require(state.get("large_VLBI_bytes_ingested") is False, "VLBI ingestion falsely claimed")
    require(state.get("comparison_likelihood_ready") is False, "likelihood readiness falsely claimed")
    require(state.get("file_level_sha256") == "TOKEN_VAZIO", "global SHA-256 state falsely promoted")


def validate_all(source: dict, custody: dict) -> None:
    validate_source(source)
    validate_custody(custody)


def selftest(source: dict, custody: dict) -> list[str]:
    cases: list[tuple[str, str]] = []

    s = copy.deepcopy(source)
    s["deliberately_unbound_source_parameters"]["a_star"] = 0.94
    try:
        validate_all(s, custody)
    except EvidenceError:
        cases.append(("invent-spin", "REJECTED"))
    else:
        raise EvidenceError("invent-spin accepted")

    c = copy.deepcopy(custody)
    c["products"]["EHT_2019_D01_01"]["file_sha256"] = "0" * 64
    try:
        validate_all(source, c)
    except EvidenceError:
        cases.append(("invent-vlbi-sha256", "REJECTED"))
    else:
        raise EvidenceError("invent-vlbi-sha256 accepted")

    c = copy.deepcopy(custody)
    c["products"]["EHT_2021_D02_01"]["primary_small_file"]["git_blob_sha1"] = "0" * 40
    try:
        validate_all(source, c)
    except EvidenceError:
        cases.append(("change-official-git-blob", "REJECTED"))
    else:
        raise EvidenceError("changed Git blob accepted")

    c = copy.deepcopy(custody)
    c["products"]["EHT_2024_D01_01"]["role"] = "BLIND_PROSPECTIVE_PREDICTION"
    try:
        validate_all(source, c)
    except EvidenceError:
        cases.append(("relabel-2018-blind", "REJECTED"))
    else:
        raise EvidenceError("blind relabel accepted")

    c = copy.deepcopy(custody)
    c["provider_observation"]["scientific_interpretation"] = "SUPPORTS_SGPT"
    try:
        validate_all(source, c)
    except EvidenceError:
        cases.append(("provider-gap-as-science", "REJECTED"))
    else:
        raise EvidenceError("provider gap scientific promotion accepted")

    return [name for name, _ in cases]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=SOURCE)
    p.add_argument("--custody", type=Path, default=CUSTODY)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--receipt", type=Path)
    args = p.parse_args()

    source = read(args.source)
    custody = read(args.custody)
    validate_all(source, custody)
    rejected = selftest(source, custody) if args.selftest else []
    receipt = {
        "schema": "rll.sgpt.m87.external-evidence-preflight-receipt/v1",
        "status": "PASS_EXTERNAL_EVIDENCE_PREFLIGHT_PARTIAL",
        "source_binding": "PASS_MODEL_DEPENDENCE_EXPLICIT",
        "custody_metadata": "PASS_PARTIAL",
        "rejected_illegal_mutations": rejected,
        "raw_VLBI_byte_custody": "TOKEN_VAZIO_PROVIDER_ACCESS_BARRIER",
        "file_level_sha256": "TOKEN_VAZIO",
        "likelihood_ready": False,
        "scientific_validation": "TOKEN_VAZIO",
        "claim_allowed": False,
    }
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
