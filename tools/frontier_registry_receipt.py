#!/usr/bin/env python3
"""Emit a deterministic, non-promotional receipt for the shadow model registry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from data.pipelines.structure_d.model_family_shadow import load_contract, load_model_specs

SCHEMA = "rll.frontier_model_registry_receipt.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_receipt(contract_path: Path) -> dict:
    contract = load_contract(contract_path)
    specs = load_model_specs(contract)
    model_ids = list(specs)
    return {
        "schema": SCHEMA,
        "contract": contract_path.as_posix(),
        "contract_sha256": sha256_file(contract_path),
        "model_count": len(model_ids),
        "model_ids": model_ids,
        "core_model_count": sum(spec.kind == "core" for spec in specs.values()),
        "composition_model_count": sum(spec.kind == "composition" for spec in specs.values()),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "canonical_outputs_modified": False,
        "decision": "REGISTRY_DRY_LOAD_PASS",
        "residuals": [
            "TOKEN_VAZIO_ROBUST_MULTI_SEED_RECEIPT",
            "TOKEN_VAZIO_PERTURBATION_BACKEND",
            "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
        ],
    }


def render_text(payload: dict) -> str:
    lines = [
        f"schema={payload['schema']}",
        f"contract_sha256={payload['contract_sha256']}",
        f"models={payload['model_count']}",
        f"core_models={payload['core_model_count']}",
        f"composition_models={payload['composition_model_count']}",
        "claim_allowed=false",
        "publication_effect=NONE",
        "canonical_outputs_modified=false",
        f"decision={payload['decision']}",
        "model_ids=" + ",".join(payload["model_ids"]),
    ]
    lines.extend(f"residual={value}" for value in payload["residuals"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("data/contracts/cosmology_model_family_shadow.v1.json"),
    )
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--text-out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_receipt(args.contract)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.text_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    text = render_text(payload)
    args.text_out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
