#!/usr/bin/env python3
"""NIBIGUIRI-12 self-critique/discovery engine for the RLL math research program.

The engine is intentionally conservative:
- it audits every research unit through all 12 lenses;
- it generates candidate research questions from configured discovery operators;
- it never promotes a candidate to theorem/hypothesis/thesis automatically;
- it preserves TOKEN_VAZIO when evidence is absent;
- hashes provide provenance, not proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml


ALLOWED_STATES = {
    "PASS",
    "FAIL",
    "TOKEN_VAZIO",
    "TOKEN_VAZIO_NOT_AUDITED",
    "NOT_APPLICABLE_WITH_REASON",
}


def canonical_json_bytes(payload: Any) -> bytes:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return unicodedata.normalize("NFC", text).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def merkle_root(hex_hashes: list[str]) -> str:
    if not hex_hashes:
        return hashlib.sha256(b"").hexdigest()
    level = [bytes.fromhex(h) for h in hex_hashes]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            hashlib.sha256(level[i] + level[i + 1]).digest()
            for i in range(0, len(level), 2)
        ]
    return level[0].hex()


def normalized_tokens(text: str) -> set[str]:
    text = unicodedata.normalize("NFKD", text).casefold()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return set(re.findall(r"[a-z0-9]+", text))


def jaccard(a: str, b: str) -> float:
    aa, bb = normalized_tokens(a), normalized_tokens(b)
    if not aa and not bb:
        return 1.0
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa | bb)


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("config root must be a mapping")
    return payload


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("registry root must be an object")
    return payload


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lenses = config.get("lenses", [])
    if len(lenses) != 12:
        errors.append(f"expected 12 lenses, got {len(lenses)}")
        return errors

    ids = [x.get("id") for x in lenses]
    angles = [x.get("angle_deg") for x in lenses]
    if ids != [f"N{i:02d}" for i in range(1, 13)]:
        errors.append("lens IDs must be N01..N12 in order")
    if sorted(angles) != list(range(0, 360, 30)):
        errors.append("angles must be exactly 0,30,...,330")

    by_id = {x["id"]: x for x in lenses if "id" in x}
    for lens in lenses:
        opp = by_id.get(lens.get("opposite"))
        if not opp:
            errors.append(f"{lens.get('id')}: missing opposite")
            continue
        if opp.get("opposite") != lens.get("id"):
            errors.append(f"{lens.get('id')}: opposite relation is not involutive")
        if (opp.get("angle_deg") - lens.get("angle_deg")) % 360 != 180:
            errors.append(f"{lens.get('id')}: opposite is not 180 degrees away")
        seed = lens.get("seed_candidate")
        if not isinstance(seed, dict):
            errors.append(f"{lens.get('id')}: missing seed_candidate")
        else:
            for key in ("id", "candidate_type", "title", "statement", "falsifier"):
                if not seed.get(key):
                    errors.append(f"{lens.get('id')}: seed_candidate missing {key}")

    states = set(config.get("states", []))
    if not ALLOWED_STATES.issubset(states):
        errors.append("config states do not include all mandatory audit states")
    if config.get("auto_promote_candidates") is not False:
        errors.append("auto_promote_candidates must remain false")
    return errors


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    units = registry.get("research_units", [])
    ids = [u.get("id") for u in units]
    if len(units) != 48:
        errors.append(f"expected 48 research units, got {len(units)}")
    if len(set(ids)) != len(ids):
        errors.append("duplicate research unit IDs")
    expected = [f"T{i:02d}" for i in range(1, 17)] + [f"H{i:02d}" for i in range(1, 33)]
    if ids != expected:
        errors.append("research unit IDs/order do not match T01..T16,H01..H32")
    return errors


def nearest_existing(title: str, units: list[dict[str, Any]]) -> dict[str, Any]:
    scored = sorted(
        ((jaccard(title, str(u.get("title", ""))), u) for u in units),
        key=lambda item: (-item[0], str(item[1].get("id", ""))),
    )
    score, unit = scored[0]
    return {"id": unit["id"], "title": unit["title"], "title_jaccard": round(score, 6)}


def build_audit_matrix(config: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for unit in registry["research_units"]:
        for lens in config["lenses"]:
            question = lens["probe_template"].format(unit_id=unit["id"], title=unit["title"])
            cells.append(
                {
                    "unit_id": unit["id"],
                    "unit_type": unit["type"],
                    "unit_title": unit["title"],
                    "lens_id": lens["id"],
                    "angle_deg": lens["angle_deg"],
                    "opposite": lens["opposite"],
                    "discovery_operator": lens["discovery_operator"],
                    "state": "TOKEN_VAZIO_NOT_AUDITED",
                    "question": question,
                    "evidence": [],
                    "negative_evidence": [],
                    "notes": "TOKEN_VAZIO",
                }
            )
    return cells


def build_seed_candidates(config: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, Any]]:
    units = registry["research_units"]
    out: list[dict[str, Any]] = []
    for lens in config["lenses"]:
        seed = dict(lens["seed_candidate"])
        nearest = nearest_existing(seed["title"], units)
        payload = {
            "schema": "raf.rll.nibiguiri_candidate.v1",
            "id": seed["id"],
            "source_lens": lens["id"],
            "source_angle_deg": lens["angle_deg"],
            "opposite_lens": lens["opposite"],
            "candidate_type": seed["candidate_type"],
            "title": seed["title"],
            "statement": seed["statement"],
            "falsifier": seed["falsifier"],
            "state": config["global_rules"]["candidate_state"],
            "novelty": config["global_rules"]["novelty_default"],
            "proof": config["global_rules"]["proof_default"],
            "counterexample_search": config["global_rules"]["counterexample_default"],
            "nearest_existing_unit": nearest,
            "possible_semantic_duplicate": nearest["title_jaccard"] >= 0.60,
            "promotion_allowed": False,
        }
        payload["sha256"] = sha256_payload({k: v for k, v in payload.items() if k != "sha256"})
        out.append(payload)
    return out


def build_pair_tensions(config: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {x["id"]: x for x in config["lenses"]}
    rows = []
    seen: set[str] = set()
    for lens in config["lenses"]:
        if lens["id"] in seen:
            continue
        opp = by_id[lens["opposite"]]
        seen.add(lens["id"])
        seen.add(opp["id"])
        rows.append(
            {
                "pair": [lens["id"], opp["id"]],
                "angles_deg": [lens["angle_deg"], opp["angle_deg"]],
                "tension": f"{lens['title']} <-> {opp['title']}",
                "question": (
                    f"Que informação é perdida ao otimizar simultaneamente "
                    f"'{lens['title']}' e '{opp['title']}'?"
                ),
                "state": "TOKEN_VAZIO_NOT_AUDITED",
            }
        )
    return rows


def build_report(config: dict[str, Any], registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    config_errors = validate_config(config)
    registry_errors = validate_registry(registry)
    cells = build_audit_matrix(config, registry)
    candidates = build_seed_candidates(config, registry)
    pair_tensions = build_pair_tensions(config)

    candidate_hashes = [c["sha256"] for c in candidates]
    candidate_root = merkle_root(candidate_hashes)
    matrix_hash = sha256_payload(cells)

    matrix_payload = {
        "schema": "raf.rll.nibiguiri_matrix_48x12.v1",
        "date": config["date"],
        "claim_allowed": False,
        "rows": 48,
        "columns": 12,
        "cells_count": len(cells),
        "initial_state": "TOKEN_VAZIO_NOT_AUDITED",
        "cells": cells,
        "sha256": matrix_hash,
    }

    candidate_payload = {
        "schema": "raf.rll.nibiguiri_candidate_registry.v1",
        "date": config["date"],
        "claim_allowed": False,
        "auto_promote": False,
        "count": len(candidates),
        "counts_by_type": {
            kind: sum(1 for c in candidates if c["candidate_type"] == kind)
            for kind in sorted({c["candidate_type"] for c in candidates})
        },
        "candidates": candidates,
        "candidate_merkle_root": candidate_root,
        "pair_tensions": pair_tensions,
        "method_self_critique": [
            {"question": q, "state": "TOKEN_VAZIO_NOT_AUDITED"}
            for q in config["self_critique_of_method"]["questions"]
        ],
    }

    structural_checks = {
        "config_valid": not config_errors,
        "registry_valid": not registry_errors,
        "matrix_576": len(cells) == 576,
        "candidate_count_12": len(candidates) == 12,
        "pair_count_6": len(pair_tensions) == 6,
        "all_candidates_unpromoted": all(not c["promotion_allowed"] for c in candidates),
        "all_candidates_have_falsifier": all(bool(c["falsifier"]) for c in candidates),
        "all_candidates_have_opposite_lens": all(bool(c["opposite_lens"]) for c in candidates),
        "all_matrix_cells_start_token_vazio": all(c["state"] == "TOKEN_VAZIO_NOT_AUDITED" for c in cells),
        "candidate_hashes_unique": len(set(candidate_hashes)) == 12,
    }

    receipt = {
        "schema": "raf.rll.nibiguiri_self_critique_receipt.v1",
        "date": config["date"],
        "claim_allowed": False,
        "structural_validation": "PASS" if all(structural_checks.values()) else "FAIL",
        "structural_checks": structural_checks,
        "errors": {"config": config_errors, "registry": registry_errors},
        "matrix_sha256": matrix_hash,
        "candidate_merkle_root": candidate_root,
        "semantic_audit": "TOKEN_VAZIO_NOT_EXECUTED_BY_SCRIPT",
        "prior_art": "TOKEN_VAZIO_PRIOR_ART",
        "proofs": "TOKEN_VAZIO_PER_CANDIDATE",
        "provider_ci": "TOKEN_VAZIO_NOT_OBSERVED",
        "boundaries": [
            "candidate count is not a quality metric",
            "candidate generation is not hypothesis promotion",
            "hash identity is not proof",
            "TOKEN_VAZIO is not numeric zero",
            "same number is not same semantic object",
            "opposite lens must be evaluated before promotion",
        ],
    }
    return matrix_payload, candidate_payload, receipt


def write_outputs(config_path: Path, registry_path: Path, out_dir: Path) -> int:
    config = load_yaml(config_path)
    registry = load_json(registry_path)
    matrix, candidates, receipt = build_report(config, registry)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "nibiguiri_self_critique_matrix_20260905.v1.json": matrix,
        "nibiguiri_self_critique_candidates_20260905.v1.json": candidates,
        "nibiguiri_self_critique_receipt_20260905.v1.json": receipt,
    }
    for name, payload in outputs.items():
        (out_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "structural_validation": receipt["structural_validation"],
        "matrix_cells": matrix["cells_count"],
        "candidate_count": candidates["count"],
        "counts_by_type": candidates["counts_by_type"],
        "candidate_merkle_root": candidates["candidate_merkle_root"],
        "matrix_sha256": matrix["sha256"],
        "output_dir": str(out_dir),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["structural_validation"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument(
        "--config",
        type=Path,
        default=here.parent / "nibiguiri_self_critique_engine_20260905.v1.yml",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=here.parent / "math_research_program_48_20260905.v1.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=here.parent / "generated",
    )
    args = parser.parse_args()
    return write_outputs(args.config, args.registry, args.out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
