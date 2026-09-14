#!/usr/bin/env python3
"""Build a claim-bounded RLL scientific navigation bundle.

The builder inventories registered mechanisms, hashes repository evidence,
emits one evidence capsule per mechanism, and consolidates unresolved
uncertainties as TOKEN_VAZIO records. It never promotes scientific claims.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REGISTRY_SCHEMA = "rll.scientific_mechanisms.v1"
CAPSULE_SCHEMA = "rll.evidence_capsule.v1"
TOKEN_SCHEMA = "rll.token_vazio.v1"
ALLOWED_CLASSES = {"workflow", "static_registry", "script", "dataset", "audit"}


class NavigationError(RuntimeError):
    """Raised when the navigation contract is structurally invalid."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise NavigationError(f"required JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise NavigationError(f"invalid JSON in {path}: {exc}") from exc


def git_commit(root: Path) -> str:
    env_sha = os.getenv("GITHUB_SHA", "").strip()
    if env_sha:
        return env_sha
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "TOKEN_VAZIO_COMMIT_SHA"


def require_keys(record: dict[str, Any], keys: Iterable[str], context: str) -> None:
    missing = [key for key in keys if key not in record]
    if missing:
        raise NavigationError(f"{context} missing keys: {', '.join(missing)}")


def validate_registry(registry: dict[str, Any]) -> None:
    require_keys(registry, ("schema", "claim_boundary", "mechanisms"), "registry")
    if registry["schema"] != REGISTRY_SCHEMA:
        raise NavigationError(
            f"registry schema must be {REGISTRY_SCHEMA!r}, got {registry['schema']!r}"
        )
    if not isinstance(registry["mechanisms"], list) or not registry["mechanisms"]:
        raise NavigationError("registry mechanisms must be a non-empty list")

    seen_mechanisms: set[str] = set()
    seen_tokens: set[str] = set()
    for index, mechanism in enumerate(registry["mechanisms"]):
        context = f"mechanism[{index}]"
        if not isinstance(mechanism, dict):
            raise NavigationError(f"{context} must be an object")
        require_keys(
            mechanism,
            (
                "mechanism_id",
                "class",
                "authority",
                "description",
                "required_paths",
                "evidence_paths",
                "expected_runtime_artifacts",
                "allowed_claims",
                "blocked_claims",
                "uncertainties",
            ),
            context,
        )
        mechanism_id = mechanism["mechanism_id"]
        if not isinstance(mechanism_id, str) or not mechanism_id:
            raise NavigationError(f"{context}.mechanism_id must be non-empty")
        if mechanism_id in seen_mechanisms:
            raise NavigationError(f"duplicate mechanism_id: {mechanism_id}")
        seen_mechanisms.add(mechanism_id)
        if mechanism["class"] not in ALLOWED_CLASSES:
            raise NavigationError(
                f"{context}.class must be one of {sorted(ALLOWED_CLASSES)}"
            )
        for list_key in (
            "required_paths",
            "evidence_paths",
            "expected_runtime_artifacts",
            "allowed_claims",
            "blocked_claims",
            "uncertainties",
        ):
            if not isinstance(mechanism[list_key], list):
                raise NavigationError(f"{context}.{list_key} must be a list")
        for uncertainty in mechanism["uncertainties"]:
            if not isinstance(uncertainty, dict):
                raise NavigationError(f"{context}.uncertainties entries must be objects")
            require_keys(
                uncertainty,
                (
                    "token_vazio_id",
                    "type",
                    "source_paths",
                    "severity",
                    "blocking_claims",
                    "affected_artifacts",
                    "required_evidence",
                    "F_next",
                ),
                f"{context}.uncertainty",
            )
            token_id = uncertainty["token_vazio_id"]
            if token_id in seen_tokens:
                raise NavigationError(f"duplicate token_vazio_id: {token_id}")
            seen_tokens.add(token_id)


def path_record(root: Path, relative: str, role: str) -> dict[str, str] | None:
    path = root / relative
    if not path.is_file():
        return None
    return {
        "path": relative,
        "sha256": sha256_file(path),
        "role": role,
        "state": "VERIFIED_LIMITED",
    }


def auto_missing_token(mechanism_id: str, relative: str, ordinal: int) -> dict[str, Any]:
    safe_id = "".join(char if char.isalnum() else "-" for char in mechanism_id.upper())
    return {
        "schema": TOKEN_SCHEMA,
        "token_vazio_id": f"TV-RLL-{safe_id}-REQUIRED-{ordinal:03d}",
        "type": "MISSING_SOURCE",
        "mechanism_id": mechanism_id,
        "source_paths": [relative],
        "state": "OPEN",
        "claim_weight": 0,
        "severity": "high",
        "blocking_claims": ["registered mechanism is complete"],
        "affected_artifacts": [],
        "required_evidence": [f"repository object present at {relative}", "content hash"],
        "resolution_evidence": [],
        "F_next": f"Locate, restore or explicitly retire the required path {relative}.",
    }


def normalize_uncertainty(mechanism_id: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": TOKEN_SCHEMA,
        "token_vazio_id": item["token_vazio_id"],
        "type": item["type"],
        "mechanism_id": mechanism_id,
        "source_paths": list(item["source_paths"]),
        "state": item.get("state", "OPEN"),
        "claim_weight": 0,
        "severity": item.get("severity", "medium"),
        "blocking_claims": list(item["blocking_claims"]),
        "affected_artifacts": list(item.get("affected_artifacts", [])),
        "required_evidence": list(item["required_evidence"]),
        "resolution_evidence": list(item.get("resolution_evidence", [])),
        "F_next": item["F_next"],
    }


def build_capsule(
    root: Path,
    mechanism: dict[str, Any],
    commit_sha: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    mechanism_id = mechanism["mechanism_id"]
    artifacts: list[dict[str, str]] = []
    missing_required: list[str] = []

    for relative in mechanism["required_paths"]:
        record = path_record(root, relative, "required_source")
        if record is None:
            missing_required.append(relative)
        else:
            artifacts.append(record)

    for relative in mechanism["evidence_paths"]:
        record = path_record(root, relative, "repository_evidence")
        if record is not None:
            artifacts.append(record)

    uncertainties = [
        normalize_uncertainty(mechanism_id, item)
        for item in mechanism["uncertainties"]
    ]
    uncertainties.extend(
        auto_missing_token(mechanism_id, relative, ordinal)
        for ordinal, relative in enumerate(missing_required, start=1)
    )

    if missing_required:
        execution_state = "TOKEN_VAZIO"
    elif mechanism["class"] == "workflow":
        execution_state = "METADATA_READY"
    else:
        execution_state = "VERIFIED_LIMITED"

    f_ok = [
        f"located {len(artifacts)} registered repository artifacts",
        "calculated SHA-256 for every located file",
        "preserved claim_allowed=false",
    ]
    f_gap = [item["F_next"] for item in uncertainties if item["state"] != "RESOLVED"]
    if mechanism["expected_runtime_artifacts"]:
        f_gap.append(
            "runtime artifact contents require a concrete workflow run and are not inferred from workflow source"
        )
    f_next = list(dict.fromkeys(f_gap)) or ["Maintain evidence state and re-audit after the next material change."]

    capsule = {
        "schema": CAPSULE_SCHEMA,
        "capsule_id": f"rll-{mechanism_id}-{commit_sha[:12]}",
        "mechanism_id": mechanism_id,
        "source": {
            "commit_sha": commit_sha,
            "workflow": mechanism["authority"],
            "inputs": list(mechanism["required_paths"]),
        },
        "execution": {
            "state": execution_state,
            "environment": "repository_read_only_inventory",
            "commands": [
                "python tools/build_scientific_navigation_bundle.py --root . --output artifacts/rll-scientific-navigation"
            ],
        },
        "claims": {
            "allowed": list(mechanism["allowed_claims"]),
            "blocked": list(mechanism["blocked_claims"]),
        },
        "uncertainties": {
            "token_vazio_count": sum(
                1 for item in uncertainties if item["state"] != "RESOLVED"
            ),
            "ledger": "TOKEN_VAZIO_LEDGER.jsonl",
        },
        "artifacts": artifacts,
        "expected_runtime_artifacts": list(mechanism["expected_runtime_artifacts"]),
        "claim_allowed": False,
        "F_ok": f_ok,
        "F_gap": f_gap,
        "F_next": f_next,
    }
    return capsule, uncertainties, missing_required


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_checksums(output: Path) -> None:
    checksum_path = output / "CHECKSUMS.sha256"
    records: list[str] = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path != checksum_path:
            records.append(f"{sha256_file(path)}  {path.relative_to(output).as_posix()}")
    checksum_path.write_text("\n".join(records) + "\n", encoding="utf-8")


def build_bundle(root: Path, registry_path: Path, output: Path) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    registry = read_json(registry_path.resolve())
    validate_registry(registry)
    commit_sha = git_commit(root)
    generated_at = datetime.now(timezone.utc).isoformat()

    output.mkdir(parents=True, exist_ok=True)
    capsules_dir = output / "capsules"
    capsules_dir.mkdir(parents=True, exist_ok=True)

    capsules: list[dict[str, Any]] = []
    all_uncertainties: list[dict[str, Any]] = []
    missing_by_mechanism: dict[str, list[str]] = {}
    mechanism_rows: list[dict[str, Any]] = []
    claim_rows: list[dict[str, Any]] = []
    graph_nodes: list[dict[str, str]] = []
    graph_edges: list[dict[str, str]] = []

    for mechanism in registry["mechanisms"]:
        capsule, uncertainties, missing = build_capsule(root, mechanism, commit_sha)
        capsules.append(capsule)
        all_uncertainties.extend(uncertainties)
        missing_by_mechanism[mechanism["mechanism_id"]] = missing
        write_json(capsules_dir / mechanism["mechanism_id"] / "CAPSULE.json", capsule)

        mechanism_rows.append(
            {
                "mechanism_id": mechanism["mechanism_id"],
                "class": mechanism["class"],
                "authority": mechanism["authority"],
                "execution_state": capsule["execution"]["state"],
                "located_artifacts": len(capsule["artifacts"]),
                "open_token_vazio": capsule["uncertainties"]["token_vazio_count"],
                "claim_allowed": "false",
            }
        )
        graph_nodes.append(
            {
                "id": mechanism["mechanism_id"],
                "type": "mechanism",
                "state": capsule["execution"]["state"],
            }
        )
        for artifact in capsule["artifacts"]:
            artifact_id = f"artifact:{artifact['path']}"
            graph_nodes.append(
                {"id": artifact_id, "type": "artifact", "state": artifact["state"]}
            )
            graph_edges.append(
                {
                    "source": mechanism["mechanism_id"],
                    "target": artifact_id,
                    "relation": artifact["role"],
                }
            )
        for state, claims in (("ALLOWED_LIMITED", mechanism["allowed_claims"]), ("BLOCKED", mechanism["blocked_claims"])):
            for claim in claims:
                claim_rows.append(
                    {
                        "mechanism_id": mechanism["mechanism_id"],
                        "state": state,
                        "claim": claim,
                        "claim_allowed": "false" if state == "BLOCKED" else "limited_only",
                    }
                )

    token_path = output / "TOKEN_VAZIO_LEDGER.jsonl"
    token_path.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
            for item in sorted(all_uncertainties, key=lambda item: item["token_vazio_id"])
        ),
        encoding="utf-8",
    )

    write_csv(
        output / "MECHANISM_MATRIX.csv",
        [
            "mechanism_id",
            "class",
            "authority",
            "execution_state",
            "located_artifacts",
            "open_token_vazio",
            "claim_allowed",
        ],
        mechanism_rows,
    )
    write_csv(
        output / "CLAIM_MATRIX.csv",
        ["mechanism_id", "state", "claim", "claim_allowed"],
        claim_rows,
    )
    write_json(
        output / "DEPENDENCY_GRAPH.json",
        {
            "schema": "rll.scientific_navigation_graph.v1",
            "nodes": graph_nodes,
            "edges": graph_edges,
        },
    )

    open_tokens = [item for item in all_uncertainties if item["state"] != "RESOLVED"]
    manifest = {
        "schema": "rll.scientific_navigation_bundle.v1",
        "generated_at_utc": generated_at,
        "commit_sha": commit_sha,
        "registry": str(registry_path.resolve().relative_to(root)),
        "claim_boundary": registry["claim_boundary"],
        "claim_allowed": False,
        "mechanism_count": len(capsules),
        "open_token_vazio_count": len(open_tokens),
        "capsules": [
            {
                "mechanism_id": capsule["mechanism_id"],
                "path": f"capsules/{capsule['mechanism_id']}/CAPSULE.json",
                "execution_state": capsule["execution"]["state"],
                "token_vazio_count": capsule["uncertainties"]["token_vazio_count"],
            }
            for capsule in capsules
        ],
        "missing_required_paths": missing_by_mechanism,
    }
    write_json(output / "NAVIGATION_MANIFEST.json", manifest)

    f_ok = [
        f"{len(capsules)} mechanisms inventoried",
        f"{sum(len(capsule['artifacts']) for capsule in capsules)} repository artifacts hashed",
        "one evidence capsule emitted per mechanism",
        "claim_allowed=false preserved globally",
    ]
    f_gap = [item["F_next"] for item in open_tokens]
    f_next = list(dict.fromkeys(f_gap))
    review_text = [
        "# F_ok / F_gap / F_next",
        "",
        "## F_ok",
        *[f"- {item}" for item in f_ok],
        "",
        "## F_gap",
        *[f"- {item}" for item in f_gap],
        "",
        "## F_next",
        *[f"- {item}" for item in f_next],
        "",
        "`claim_allowed=false`",
        "",
    ]
    (output / "F_OK_F_GAP_F_NEXT.md").write_text("\n".join(review_text), encoding="utf-8")

    index_lines = [
        "# RLL Scientific Navigation Bundle",
        "",
        f"- Commit: `{commit_sha}`",
        f"- Mechanisms: `{len(capsules)}`",
        f"- Open TOKEN_VAZIO: `{len(open_tokens)}`",
        "- Claim allowed: `false`",
        "",
        "## Review order",
        "",
        "1. `CHECKSUMS.sha256`",
        "2. `NAVIGATION_MANIFEST.json`",
        "3. `TOKEN_VAZIO_LEDGER.jsonl`",
        "4. `CLAIM_MATRIX.csv`",
        "5. `MECHANISM_MATRIX.csv`",
        "6. `DEPENDENCY_GRAPH.json`",
        "7. `capsules/*/CAPSULE.json`",
        "8. `F_OK_F_GAP_F_NEXT.md`",
        "",
        "## Boundary",
        "",
        registry["claim_boundary"],
        "",
    ]
    (output / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    receipt = {
        "schema": "rll.scientific_navigation_receipt.v1",
        "generated_at_utc": generated_at,
        "commit_sha": commit_sha,
        "builder": "tools/build_scientific_navigation_bundle.py",
        "registry_schema": registry["schema"],
        "mechanism_count": len(capsules),
        "open_token_vazio_count": len(open_tokens),
        "automatic_commit": False,
        "reviewed_pr_required": True,
        "claim_allowed": False,
    }
    write_json(output / "RECEIPT.json", receipt)
    write_checksums(output)
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/navigation/scientific_mechanisms.v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/rll-scientific-navigation"),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any registered required path is absent.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    registry = args.registry if args.registry.is_absolute() else root / args.registry
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        manifest = build_bundle(root, registry, output)
    except NavigationError as exc:
        print(f"navigation contract error: {exc}", file=sys.stderr)
        return 2

    missing = {
        mechanism_id: paths
        for mechanism_id, paths in manifest["missing_required_paths"].items()
        if paths
    }
    print(
        json.dumps(
            {
                "status": "TOKEN_VAZIO" if missing else "METADATA_READY",
                "mechanisms": manifest["mechanism_count"],
                "open_token_vazio": manifest["open_token_vazio_count"],
                "missing_required_paths": missing,
                "claim_allowed": False,
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    if args.strict and missing:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
