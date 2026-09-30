#!/usr/bin/env python3
"""RLL full methodological coverage engine.

Successor to NIBIGUIRI-12:
- 8 macro-families x 12 antagonistic directions = 96 lenses
- 5 A-E heuristic operators = 120 order permutations
- 12 Relation Calculus operators
- 34 semantic dimension slots (names remain TOKEN_VAZIO until source-bound)
- 48 research units

The engine materializes 12,576 staged audit obligations and provides a
random-access index over the 225,607,680-cell full Cartesian cross without
pretending that combinatorial size itself is evidence or quality.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import unicodedata
from pathlib import Path
from typing import Any, Iterator

import yaml

TOKEN = "TOKEN_VAZIO_NOT_AUDITED"


def canonical_bytes(obj: Any) -> bytes:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return unicodedata.normalize("NFC", s).encode("utf-8")


def sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("config root must be mapping")
    return obj


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("registry root must be object")
    return obj


def ae_permutations(config: dict[str, Any]) -> list[str]:
    ids = [x["id"] for x in config["heuristic_AE"]["operators"]]
    return ["".join(p) for p in itertools.permutations(ids)]


def build_96_lenses(config: dict[str, Any]) -> list[dict[str, Any]]:
    lenses = []
    for fam in config["macro_families"]:
        for direction in config["antagonistic_directions"]:
            idx = int(direction["id"][1:])
            focus = fam["focus"][(idx - 1) % len(fam["focus"])]
            lenses.append({
                "id": f"{fam['id']}{direction['id']}",
                "family_id": fam["id"],
                "family_title": fam["title"],
                "direction_id": direction["id"],
                "angle_deg": direction["angle_deg"],
                "opposite_direction": direction["opposite"],
                "verb": direction["verb"],
                "focus": focus,
                "question_template": (
                    f"[{fam['id']}:{fam['title']} × {direction['id']}:{direction['verb']}] "
                    "{unit_id} — {unit_title}: "
                    f"{fam['question']} Foco específico: {focus}. "
                    "Qual evidência, contraevidência, perda, inversa ou exceção altera o estado?"
                ),
            })
    return lenses


def validate(config: dict[str, Any], registry: dict[str, Any]) -> dict[str, bool]:
    fams = config["macro_families"]
    dirs = config["antagonistic_directions"]
    perms = ae_permutations(config)
    rels = config["relation_calculus"]["operators"]
    dims = config["semantic_dimensions"]["slots"]
    units = registry["research_units"]
    by_dir = {x["id"]: x for x in dirs}
    return {
        "eight_families": len(fams) == 8 and len({x["id"] for x in fams}) == 8,
        "twelve_directions": len(dirs) == 12 and len({x["id"] for x in dirs}) == 12,
        "isogonic_angles": sorted(x["angle_deg"] for x in dirs) == list(range(0, 360, 30)),
        "opposites_involutive": all(
            by_dir[x["opposite"]]["opposite"] == x["id"] and
            (by_dir[x["opposite"]]["angle_deg"] - x["angle_deg"]) % 360 == 180
            for x in dirs
        ),
        "ninety_six_lenses": len(build_96_lenses(config)) == 96,
        "five_AE_operators": len(config["heuristic_AE"]["operators"]) == 5,
        "one_hundred_twenty_permutations": len(perms) == 120 and len(set(perms)) == 120,
        "twelve_relation_operators": len(rels) == 12 and len(set(rels)) == 12,
        "thirty_four_slots": len(dims) == 34 and len({x["id"] for x in dims}) == 34,
        "no_invented_34D_names": all(x["canonical_name"].startswith("TOKEN_VAZIO") for x in dims),
        "forty_eight_units": len(units) == 48 and len({x["id"] for x in units}) == 48,
        "base_cells_4608": len(units) * 8 * 12 == 4608,
        "AE_cells_5760": len(units) * 120 == 5760,
        "relation_cells_576": len(units) * 12 == 576,
        "semantic_cells_1632": len(units) * 34 == 1632,
        "staged_total_12576": len(units) * (96 + 120 + 12 + 34) == 12576,
        "full_cross_225607680": len(units) * 96 * 120 * 12 * 34 == 225607680,
        "no_auto_promotion": config.get("auto_promote") is False,
        "method_self_audit_present": len(config["method_self_critique"]["questions"]) >= 12,
    }


def build_obligations(config: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    lenses = build_96_lenses(config)
    perms = ae_permutations(config)
    rels = config["relation_calculus"]["operators"]
    dims = [x["id"] for x in config["semantic_dimensions"]["slots"]]
    units_out = {}
    for unit in registry["research_units"]:
        uid = unit["id"]
        units_out[uid] = {
            "title": unit["title"],
            "type": unit["type"],
            "base_96": {lens["id"]: TOKEN for lens in lenses},
            "AE_120": {p: TOKEN for p in perms},
            "relation_12": {r: TOKEN for r in rels},
            "semantic_34": {d: TOKEN for d in dims},
        }
    payload = {
        "schema": "raf.rll.full_method_obligations_12576.v2",
        "date": config["date"],
        "claim_allowed": False,
        "initial_state": TOKEN,
        "counts": {
            "research_units": len(registry["research_units"]),
            "families": 8,
            "directions": 12,
            "lenses": len(lenses),
            "AE_permutations": len(perms),
            "relation_operators": len(rels),
            "semantic_slots": len(dims),
            "base_cells": len(registry["research_units"]) * len(lenses),
            "AE_cells": len(registry["research_units"]) * len(perms),
            "relation_cells": len(registry["research_units"]) * len(rels),
            "semantic_cells": len(registry["research_units"]) * len(dims),
            "staged_total": len(registry["research_units"]) * (len(lenses) + len(perms) + len(rels) + len(dims)),
            "full_cross": len(registry["research_units"]) * len(lenses) * len(perms) * len(rels) * len(dims),
        },
        "lenses_96": lenses,
        "AE_permutations_120": perms,
        "relation_operators_12": rels,
        "semantic_slots_34": dims,
        "units": units_out,
    }
    payload["sha256"] = sha256({k: v for k, v in payload.items() if k != "sha256"})
    return payload


def dimensions(config: dict[str, Any], registry: dict[str, Any]) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    units = [u["id"] for u in registry["research_units"]]
    lenses = [x["id"] for x in build_96_lenses(config)]
    perms = ae_permutations(config)
    rels = list(config["relation_calculus"]["operators"])
    dims = [x["id"] for x in config["semantic_dimensions"]["slots"]]
    return units, lenses, perms, rels, dims


def full_cross_size(config: dict[str, Any], registry: dict[str, Any]) -> int:
    return math.prod(len(x) for x in dimensions(config, registry))


def decode_full_index(index: int, config: dict[str, Any], registry: dict[str, Any]) -> dict[str, str]:
    axes = dimensions(config, registry)
    size = math.prod(len(a) for a in axes)
    if index < 0 or index >= size:
        raise IndexError(index)
    values = [None] * len(axes)
    n = index
    for pos in range(len(axes) - 1, -1, -1):
        axis = axes[pos]
        n, rem = divmod(n, len(axis))
        values[pos] = axis[rem]
    return dict(zip(("unit_id", "lens_id", "AE_order", "relation_operator", "semantic_axis"), values))


def encode_full_index(point: dict[str, str], config: dict[str, Any], registry: dict[str, Any]) -> int:
    axes = dimensions(config, registry)
    names = ("unit_id", "lens_id", "AE_order", "relation_operator", "semantic_axis")
    idx = 0
    for name, axis in zip(names, axes):
        idx = idx * len(axis) + axis.index(point[name])
    return idx


def iter_full_shard(start: int, count: int, config: dict[str, Any], registry: dict[str, Any]) -> Iterator[dict[str, Any]]:
    size = full_cross_size(config, registry)
    stop = min(size, start + count)
    for i in range(start, stop):
        row = decode_full_index(i, config, registry)
        row["index"] = i
        row["state"] = TOKEN
        yield row


def build_receipt(config: dict[str, Any], registry: dict[str, Any], obligations: dict[str, Any]) -> dict[str, Any]:
    checks = validate(config, registry)
    return {
        "schema": "raf.rll.full_method_receipt.v2",
        "date": config["date"],
        "claim_allowed": False,
        "structural_validation": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "obligations_sha256": obligations["sha256"],
        "method_state": "TOKEN_VAZIO_METHOD_VALIDATION",
        "semantic_34D_axes": "TOKEN_VAZIO_CANONICAL_AXES",
        "prior_art": "TOKEN_VAZIO_PER_RESEARCH_UNIT",
        "proofs": "TOKEN_VAZIO_PER_HYPOTHESIS",
        "provider_ci": "TOKEN_VAZIO_NOT_OBSERVED_FOR_V2_HEAD",
        "boundaries": [
            "96 lenses are coverage structure, not 96 proofs",
            "120 permutations are order probes, not 120 independent discoveries",
            "34 slots are not named axes until source-bound",
            "225607680 full-cross points are an index space, not a quality metric",
            "hash is provenance, not proof",
            "TOKEN_VAZIO is not numeric zero",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    ap.add_argument("--config", type=Path, default=here.parent / "nibiguiri_full_method_8x12_20260905.v2.yml")
    ap.add_argument("--registry", type=Path, default=here.parent / "math_research_program_48_20260905.v1.json")
    ap.add_argument("--out-dir", type=Path, default=here.parent / "generated")
    ap.add_argument("--shard-start", type=int)
    ap.add_argument("--shard-count", type=int, default=0)
    args = ap.parse_args()
    config = load_yaml(args.config)
    registry = load_json(args.registry)
    obligations = build_obligations(config, registry)
    receipt = build_receipt(config, registry, obligations)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "nibiguiri_full_obligations_12576_20260905.v2.json").write_text(json.dumps(obligations, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "nibiguiri_full_method_receipt_20260905.v2.json").write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.shard_start is not None and args.shard_count:
        p = args.out_dir / f"full_cross_{args.shard_start}_{args.shard_count}.jsonl"
        with p.open("w", encoding="utf-8") as f:
            for row in iter_full_shard(args.shard_start, args.shard_count, config, registry):
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({
        "validation": receipt["structural_validation"],
        "lenses": 96,
        "staged_obligations": 12576,
        "full_cross": full_cross_size(config, registry),
        "obligations_sha256": obligations["sha256"],
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if receipt["structural_validation"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
