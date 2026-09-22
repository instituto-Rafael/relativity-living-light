#!/usr/bin/env python3
"""Validate ethics-by-design, license friction, parable boundaries and urgency anti-regression.

This validator is structural/governance-only. It does not determine legal
enforceability and never rewrites LICENSE.md or package metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MODULE = Path("governance/modules/ethics-by-design-complex-networks.v1.json")
MODULE_SCHEMA = Path("governance/rll-module-contract.schema.json")
CONTRACT = Path("data/governance/RLL_ETHICS_LICENSE_FRICTION_CONTRACT_20260816_V1.json")
LEDGER = Path("data/governance/RLL_ETHICS_LICENSE_FRICTION_LEDGER_20260816_V1.jsonl")
PARABLES = Path("data/governance/RLL_PARABLE_INTERNAL_REFERENCE_INDEX_20260816_V1.json")
LICENSE = Path("LICENSE.md")
PYPROJECT = Path("pyproject.toml")
README = Path("README.md")
OUT = Path("artifacts/ethics-license-friction")

REQUIRED_LEDGER_FIELDS = {
    "id", "urgency", "state", "source", "provider", "use", "relation",
    "providencia", "falsifier", "provenance", "claim_allowed", "receipt",
}
CLOSED_STATES = {"CLOSED", "VERIFIED", "RESOLVED"}
EXPECTED_CHAIN = [
    "STATISTICS", "TOKENS", "METAPHORS", "WORD_VECTORS",
    "PROMISE", "EXECUTABLE_VERB", "OMEGA_N",
]
REQUIRED_FORBIDDEN = {
    "SYMBOLIC_NARRATIVE->LEGAL_TEXT",
    "SYMBOLIC_NARRATIVE->SCIENTIFIC_EVIDENCE",
    "PROMISE->PROOF",
    "TOKEN_VAZIO->VERIFIED_WITHOUT_RECEIPT",
    "INCERTEZA->CLOSED_WITHOUT_FALSIFIER",
    "EXTERNAL_SOURCE->REPO_HASH_BOUND_WITHOUT_HASH",
}


def load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def load_ledger(root: Path, path: Path = LEDGER) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, raw in enumerate((root / path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        item = json.loads(raw)
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{lineno}: entry must be an object")
        rows.append(item)
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    module = load_json(root, MODULE)
    schema = load_json(root, MODULE_SCHEMA)
    contract = load_json(root, CONTRACT)
    parables = load_json(root, PARABLES)
    ledger = load_ledger(root)

    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(module),
        key=lambda err: list(err.absolute_path),
    )
    for err in schema_errors:
        loc = ".".join(map(str, err.absolute_path)) or "<root>"
        errors.append(f"MODULE_SCHEMA:{loc}:{err.message}")

    for key in ("claim_allowed", "certification_claim", "auto_merge", "auto_license_rewrite"):
        if contract.get(key) is not False:
            errors.append(f"CONTRACT_FAIL_CLOSED:{key} must be false")
    if module.get("claim_allowed") is not False or module.get("certification_claim") is not False:
        errors.append("MODULE_FAIL_CLOSED: claim/certification must be false")
    if parables.get("claim_allowed") is not False or parables.get("certification_claim") is not False:
        errors.append("PARABLE_FAIL_CLOSED: claim/certification must be false")

    # Repository-local license surfaces: observe, do not decide legal validity.
    pyproject = tomllib.loads((root / PYPROJECT).read_text(encoding="utf-8"))
    package_license = pyproject.get("project", {}).get("license", {}).get("text")
    observed = contract.get("license_surfaces", {}).get("PACKAGE_METADATA", {}).get("observed_value")
    if package_license != observed:
        errors.append(f"PACKAGE_LICENSE_DRIFT: contract={observed!r} actual={package_license!r}")
    readme_text = (root / README).read_text(encoding="utf-8")
    if "LICENSE.md" not in readme_text:
        errors.append("README_LICENSE_REFERENCE_MISSING")
    if not (root / LICENSE).is_file():
        errors.append("LICENSE_SURFACE_MISSING")
    coherence = contract.get("license_coherence", {})
    if package_license == "MIT" and "LICENSE.md" in readme_text:
        if coherence.get("state") != "CONTRADICTION":
            errors.append("LICENSE_CONTRADICTION_MUST_REMAIN_EXPLICIT")
        if coherence.get("automatic_resolution") != "FORBIDDEN":
            errors.append("LICENSE_CONTRADICTION_CANNOT_AUTO_RESOLVE")
        if coherence.get("canonical_machine_readable_expression") != "TOKEN_VAZIO_CANONICAL_LICENSE_EXPRESSION":
            errors.append("CANONICAL_LICENSE_MUST_REMAIN_TOKEN_VAZIO_UNTIL_REVIEW")
        if coherence.get("legal_enforceability") != "TOKEN_VAZIO_LEGAL_REVIEW":
            errors.append("LEGAL_ENFORCEABILITY_MUST_REMAIN_TOKEN_VAZIO")

    chain = contract.get("transformation_chain", [])
    if [stage.get("stage") for stage in chain] != EXPECTED_CHAIN:
        errors.append("SEMANTIC_CHAIN_ORDER_DRIFT")
    by_stage = {stage.get("stage"): stage for stage in chain}
    promise = by_stage.get("PROMISE", {})
    if promise.get("evidence_capable") is not False or "never a proof" not in promise.get("boundary", "").lower():
        errors.append("PROMISE_MUST_NOT_BECOME_PROOF")
    omega = by_stage.get("OMEGA_N", {})
    omega_boundary = omega.get("boundary", "").lower()
    if omega.get("evidence_capable") is not False or "not an infinity claim" not in omega_boundary:
        errors.append("OMEGA_N_MUST_REMAIN_FINITE_VERSIONED_INDEX")
    metaphor = by_stage.get("METAPHORS", {})
    if metaphor.get("evidence_capable") is not False:
        errors.append("METAPHOR_MUST_NOT_BE_EVIDENCE_CAPABLE")
    executable = by_stage.get("EXECUTABLE_VERB", {})
    if executable.get("evidence_capable") is not True:
        errors.append("EXECUTABLE_VERB_EVIDENCE_CAPABILITY_MISSING")
    for marker in ("input", "output", "test", "receipt"):
        if marker not in executable.get("boundary", "").lower():
            errors.append(f"EXECUTABLE_VERB_BOUNDARY_MISSING:{marker}")

    forbidden = set(contract.get("forbidden_promotions", []))
    missing_forbidden = REQUIRED_FORBIDDEN - forbidden
    if missing_forbidden:
        errors.append("FORBIDDEN_PROMOTIONS_MISSING:" + ",".join(sorted(missing_forbidden)))

    symbolic = contract.get("symbolic_boundary", {})
    if symbolic.get("phrase") != "NENHUM_LIMITE_E_REAL":
        errors.append("SYMBOLIC_PHRASE_MISSING")
    if symbolic.get("classification") != "SYMBOLIC_NARRATIVE":
        errors.append("SYMBOLIC_PHRASE_MUST_NOT_BE_RUNTIME_CLAIM")
    if symbolic.get("runtime_counter_invariant") != "EVERY_OBSERVED_LIMIT_MUST_BE_EXPLICIT_TESTABLE_AND_RECEIPT_BOUND":
        errors.append("RUNTIME_LIMIT_COUNTER_INVARIANT_DRIFT")

    ids: set[str] = set()
    for row in ledger:
        missing = REQUIRED_LEDGER_FIELDS - row.keys()
        if missing:
            errors.append(f"LEDGER_FIELDS:{row.get('id', '<unknown>')}:{','.join(sorted(missing))}")
            continue
        rid = str(row["id"])
        if rid in ids:
            errors.append(f"DUPLICATE_URGENCY_ID:{rid}")
        ids.add(rid)
        urgency = row["urgency"]
        if urgency not in {"P0", "P1", "P2"}:
            errors.append(f"BAD_URGENCY:{rid}:{urgency}")
        if row["claim_allowed"] is not False:
            errors.append(f"LEDGER_CLAIM_PROMOTION:{rid}")
        if urgency in {"P0", "P1"}:
            for key in ("source", "use", "relation", "providencia", "falsifier", "provenance"):
                if not row.get(key):
                    errors.append(f"URGENT_METADATA_EMPTY:{rid}:{key}")
        if row["state"] in CLOSED_STATES and not row.get("receipt"):
            errors.append(f"CLOSED_WITHOUT_RECEIPT:{rid}")

    lic = next((row for row in ledger if row.get("id") == "ETHLIC-001"), None)
    if not lic or lic.get("urgency") != "P0" or lic.get("state") != "CONTRADICTION":
        errors.append("ETHLIC_001_MUST_BE_P0_CONTRADICTION")
    if not lic or "Do not auto-rewrite" not in lic.get("providencia", ""):
        errors.append("ETHLIC_001_MUST_FORBID_AUTO_REWRITE")

    for ref in parables.get("references", []):
        if ref.get("evidence_role") != "NONE":
            errors.append(f"PARABLE_EVIDENCE_PROMOTION:{ref.get('id')}")
    for source in parables.get("external_sources", []):
        digest = str(source.get("repo_hash", ""))
        if not digest.startswith("TOKEN_VAZIO"):
            errors.append(f"EXTERNAL_SOURCE_FALSE_HASH_BIND:{source.get('name')}")
    if "parable_as_legal_authority" not in parables.get("forbidden", []):
        errors.append("PARABLE_LEGAL_AUTHORITY_GUARD_MISSING")
    if "omega_n_as_infinity_claim" not in parables.get("forbidden", []):
        errors.append("OMEGA_INFINITY_GUARD_MISSING")

    expected_metadata = module.get("data_governance", {}).get("required_metadata", [])
    for field in REQUIRED_LEDGER_FIELDS - {"receipt"}:
        if field not in expected_metadata:
            errors.append(f"MODULE_REQUIRED_METADATA_MISSING:{field}")
    if contract.get("relations", {}).get("urgency_ledger") != LEDGER.as_posix():
        errors.append("CONTRACT_LEDGER_LINK_DRIFT")
    if contract.get("relations", {}).get("parable_index") != PARABLES.as_posix():
        errors.append("CONTRACT_PARABLE_LINK_DRIFT")

    return errors


def write_receipt(root: Path, output: Path, errors: list[str]) -> None:
    ledger = load_ledger(root)
    counts = {
        "P0": sum(row["urgency"] == "P0" for row in ledger),
        "P1": sum(row["urgency"] == "P1" for row in ledger),
        "P2": sum(row["urgency"] == "P2" for row in ledger),
        "TOKEN_VAZIO": sum(str(row["state"]).startswith("TOKEN_VAZIO") for row in ledger),
        "CONTRADICTION": sum(row["state"] == "CONTRADICTION" for row in ledger),
    }
    out = output if output.is_absolute() else root / output
    out.mkdir(parents=True, exist_ok=True)
    files = [MODULE, MODULE_SCHEMA, CONTRACT, LEDGER, PARABLES, LICENSE, PYPROJECT, README]
    payload = {
        "schema": "rll.ethics_license_friction_validation_receipt.v1",
        "passed": not errors,
        "errors": errors,
        "counts": counts,
        "sha256": {path.as_posix(): sha256_file(root / path) for path in files},
        "claim_allowed": False,
        "certification_claim": False,
        "legal_enforceability_determined": False,
        "auto_license_rewrite": False,
        "publication_effect": "NONE",
    }
    (out / "receipt.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        errors = validate(args.root)
        if args.write_receipt:
            write_receipt(args.root, args.output_dir, errors)
    except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"ERROR ETHICS_LICENSE_FRICTION: {exc}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1 if args.strict else 0
    print("ethics-license-friction: PASS; legal_enforceability=TOKEN_VAZIO; claim_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
