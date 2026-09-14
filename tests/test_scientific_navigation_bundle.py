from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.build_scientific_navigation_bundle import (
    NavigationError,
    build_bundle,
    main,
    validate_registry,
)


def registry(required_path: str = "evidence/source.txt") -> dict:
    return {
        "schema": "rll.scientific_mechanisms.v1",
        "claim_boundary": "Structural navigation only; no scientific promotion.",
        "mechanisms": [
            {
                "mechanism_id": "fixture-mechanism",
                "class": "static_registry",
                "authority": required_path,
                "description": "Synthetic test registry.",
                "required_paths": [required_path],
                "evidence_paths": [],
                "expected_runtime_artifacts": [],
                "allowed_claims": ["fixture source was located"],
                "blocked_claims": ["fixture proves physical truth"],
                "uncertainties": [
                    {
                        "token_vazio_id": "TV-RLL-FIXTURE-REVIEW",
                        "type": "MISSING_REVIEW",
                        "source_paths": [required_path],
                        "severity": "medium",
                        "blocking_claims": ["independent validation completed"],
                        "affected_artifacts": [],
                        "required_evidence": ["independent review receipt"],
                        "F_next": "Request an independent fixture review."
                    }
                ],
            }
        ],
    }


def write_registry(root: Path, payload: dict) -> Path:
    path = root / "data/navigation/scientific_mechanisms.v1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_bundle_emits_capsule_ledgers_and_checksums(tmp_path: Path) -> None:
    source = tmp_path / "evidence/source.txt"
    source.parent.mkdir(parents=True)
    source.write_text("evidence\n", encoding="utf-8")
    registry_path = write_registry(tmp_path, registry())
    output = tmp_path / "artifacts/navigation"

    manifest = build_bundle(tmp_path, registry_path, output)

    assert manifest["mechanism_count"] == 1
    assert manifest["open_token_vazio_count"] == 1
    assert manifest["claim_allowed"] is False
    assert (output / "INDEX.md").is_file()
    assert (output / "NAVIGATION_MANIFEST.json").is_file()
    assert (output / "TOKEN_VAZIO_LEDGER.jsonl").is_file()
    assert (output / "CLAIM_MATRIX.csv").is_file()
    assert (output / "MECHANISM_MATRIX.csv").is_file()
    assert (output / "DEPENDENCY_GRAPH.json").is_file()
    assert (output / "RECEIPT.json").is_file()
    assert (output / "CHECKSUMS.sha256").is_file()

    capsule = json.loads(
        (output / "capsules/fixture-mechanism/CAPSULE.json").read_text(encoding="utf-8")
    )
    assert capsule["claim_allowed"] is False
    assert capsule["execution"]["state"] == "VERIFIED_LIMITED"
    assert capsule["artifacts"][0]["path"] == "evidence/source.txt"
    assert len(capsule["artifacts"][0]["sha256"]) == 64

    checksums = (output / "CHECKSUMS.sha256").read_text(encoding="utf-8")
    assert "NAVIGATION_MANIFEST.json" in checksums
    assert "CHECKSUMS.sha256" not in checksums


def test_missing_required_path_becomes_typed_token_vazio(tmp_path: Path) -> None:
    registry_path = write_registry(tmp_path, registry("missing/source.txt"))
    output = tmp_path / "artifacts/navigation"

    manifest = build_bundle(tmp_path, registry_path, output)

    assert manifest["missing_required_paths"]["fixture-mechanism"] == [
        "missing/source.txt"
    ]
    capsule = json.loads(
        (output / "capsules/fixture-mechanism/CAPSULE.json").read_text(encoding="utf-8")
    )
    assert capsule["execution"]["state"] == "TOKEN_VAZIO"
    ledger = [
        json.loads(line)
        for line in (output / "TOKEN_VAZIO_LEDGER.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    automatic = [item for item in ledger if "REQUIRED-001" in item["token_vazio_id"]]
    assert automatic[0]["type"] == "MISSING_SOURCE"
    assert automatic[0]["claim_weight"] == 0


def test_duplicate_uncertainty_ids_are_rejected() -> None:
    payload = registry()
    second = json.loads(json.dumps(payload["mechanisms"][0]))
    second["mechanism_id"] = "second-mechanism"
    payload["mechanisms"].append(second)

    with pytest.raises(NavigationError, match="duplicate token_vazio_id"):
        validate_registry(payload)


def test_strict_mode_returns_nonzero_for_missing_required_path(tmp_path: Path) -> None:
    registry_path = write_registry(tmp_path, registry("missing/source.txt"))
    output = tmp_path / "artifact"

    status = main(
        [
            "--root",
            str(tmp_path),
            "--registry",
            str(registry_path),
            "--output",
            str(output),
            "--strict",
        ]
    )

    assert status == 3
    receipt = json.loads((output / "RECEIPT.json").read_text(encoding="utf-8"))
    assert receipt["claim_allowed"] is False
    assert receipt["automatic_commit"] is False
