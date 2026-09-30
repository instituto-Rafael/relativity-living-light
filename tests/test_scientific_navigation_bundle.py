from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.build_scientific_navigation_bundle import (
    NavigationError,
    build_bundle,
    main,
    validate_registry,
    write_checksums,
)


def registry(
    required_path: str = "evidence/source.txt",
    evidence_paths: list[str] | None = None,
    expected_runtime_artifacts: list[str] | None = None,
) -> dict:
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
                "evidence_paths": evidence_paths or [],
                "expected_runtime_artifacts": expected_runtime_artifacts or [],
                "allowed_claims": ["fixture source was located"],
                "blocked_claims": ["independent validation completed"],
                "uncertainties": [
                    {
                        "token_vazio_id": "TV-RLL-FIXTURE-REVIEW",
                        "type": "MISSING_REVIEW",
                        "source_paths": [required_path],
                        "severity": "medium",
                        "blocking_claims": ["independent validation completed"],
                        "affected_artifacts": [],
                        "required_evidence": ["independent review receipt"],
                        "F_next": "Request an independent fixture review.",
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


def make_source(root: Path, relative: str, content: str = "evidence\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_ledger(output: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in (output / "TOKEN_VAZIO_LEDGER.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]


def test_bundle_emits_capsule_ledgers_and_checksums(tmp_path: Path) -> None:
    make_source(tmp_path, "evidence/source.txt")
    registry_path = write_registry(tmp_path, registry())
    output = tmp_path / "artifacts/navigation"

    manifest = build_bundle(tmp_path, registry_path, output)

    assert manifest["mechanism_count"] == 1
    assert manifest["open_token_vazio_count"] == 1
    assert manifest["claim_allowed"] is False
    assert manifest["missing_evidence_paths"] == {"fixture-mechanism": []}
    for name in (
        "INDEX.md",
        "NAVIGATION_MANIFEST.json",
        "TOKEN_VAZIO_LEDGER.jsonl",
        "CLAIM_MATRIX.csv",
        "MECHANISM_MATRIX.csv",
        "DEPENDENCY_GRAPH.json",
        "RECEIPT.json",
        "CHECKSUMS.sha256",
    ):
        assert (output / name).is_file()

    capsule = json.loads(
        (output / "capsules/fixture-mechanism/CAPSULE.json").read_text(
            encoding="utf-8"
        )
    )
    assert capsule["claim_allowed"] is False
    assert capsule["execution"]["state"] == "VERIFIED_LIMITED"
    assert capsule["artifacts"][0]["path"] == "evidence/source.txt"
    assert len(capsule["artifacts"][0]["sha256"]) == 64
    assert capsule["F_gap"] != capsule["F_next"]

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
        (output / "capsules/fixture-mechanism/CAPSULE.json").read_text(
            encoding="utf-8"
        )
    )
    assert capsule["execution"]["state"] == "TOKEN_VAZIO"
    automatic = [
        item
        for item in read_ledger(output)
        if "REQUIRED-001" in item["token_vazio_id"]
    ]
    assert automatic[0]["type"] == "MISSING_SOURCE"
    assert automatic[0]["claim_weight"] == 0
    assert automatic[0]["severity"] == "high"


def test_missing_registered_evidence_becomes_typed_token_vazio(
    tmp_path: Path,
) -> None:
    make_source(tmp_path, "evidence/source.txt")
    registry_path = write_registry(
        tmp_path,
        registry(evidence_paths=["evidence/missing-metadata.json"]),
    )
    output = tmp_path / "artifacts/navigation"

    manifest = build_bundle(tmp_path, registry_path, output)

    assert manifest["missing_required_paths"]["fixture-mechanism"] == []
    assert manifest["missing_evidence_paths"]["fixture-mechanism"] == [
        "evidence/missing-metadata.json"
    ]
    token = next(
        item
        for item in read_ledger(output)
        if "EVIDENCE-001" in item["token_vazio_id"]
    )
    assert token["source_paths"] == ["evidence/missing-metadata.json"]
    assert token["severity"] == "medium"
    assert token["claim_weight"] == 0


def test_dependency_graph_contains_uncertainty_runtime_and_blocking_edges(
    tmp_path: Path,
) -> None:
    make_source(tmp_path, "evidence/source.txt")
    registry_path = write_registry(
        tmp_path,
        registry(expected_runtime_artifacts=["RECEIPT.json"]),
    )
    output = tmp_path / "artifacts/navigation"

    build_bundle(tmp_path, registry_path, output)
    graph = json.loads(
        (output / "DEPENDENCY_GRAPH.json").read_text(encoding="utf-8")
    )

    assert graph["schema"] == "rll.scientific_navigation_graph.v2"
    node_types = {node["type"] for node in graph["nodes"]}
    relations = {edge["relation"] for edge in graph["edges"]}
    assert {
        "mechanism",
        "token_vazio",
        "expected_runtime_artifact",
        "claim",
    } <= node_types
    assert {
        "has_uncertainty",
        "expects_runtime",
        "blocks_claim",
        "requires_evidence",
    } <= relations


def test_recomputing_checksums_covers_late_workflow_files(tmp_path: Path) -> None:
    output = tmp_path / "artifact"
    output.mkdir()
    (output / "early.txt").write_text("early\n", encoding="utf-8")
    write_checksums(output)
    (output / "BUILD.log").write_text("build\n", encoding="utf-8")
    (output / "WORKFLOW_RECEIPT.json").write_text("{}\n", encoding="utf-8")

    write_checksums(output)

    checksums = (output / "CHECKSUMS.sha256").read_text(encoding="utf-8")
    assert "early.txt" in checksums
    assert "BUILD.log" in checksums
    assert "WORKFLOW_RECEIPT.json" in checksums
    assert "CHECKSUMS.sha256" not in checksums


def test_duplicate_uncertainty_ids_are_rejected() -> None:
    payload = registry()
    second = json.loads(json.dumps(payload["mechanisms"][0]))
    second["mechanism_id"] = "second-mechanism"
    payload["mechanisms"].append(second)

    with pytest.raises(NavigationError, match="duplicate token_vazio_id"):
        validate_registry(payload)


def test_strict_mode_returns_nonzero_only_for_missing_required_path(
    tmp_path: Path,
) -> None:
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


def test_strict_mode_preserves_missing_evidence_as_nonfatal_typed_gap(
    tmp_path: Path,
) -> None:
    make_source(tmp_path, "evidence/source.txt")
    registry_path = write_registry(
        tmp_path,
        registry(evidence_paths=["evidence/not-yet-produced.json"]),
    )
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

    assert status == 0
    assert any(
        "EVIDENCE-001" in item["token_vazio_id"]
        for item in read_ledger(output)
    )
