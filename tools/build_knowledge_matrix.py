#!/usr/bin/env python3
"""
FASE 30 — RLL Knowledge Matrix Builder
Mines all source artifacts and constructs the multi-dimensional Knowledge Matrix.
claim_allowed=false globally; training_allowed=false.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

CLAIM_BOUNDARY = "claim_allowed=false; training_allowed=false"
GENERATED_AT = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Hash utilities
# ---------------------------------------------------------------------------

def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_blake3(content: str) -> str:
    try:
        import blake3
        return blake3.blake3(content.encode("utf-8")).hexdigest()
    except ImportError:
        # Fallback: double SHA256 tagged so tests can detect absence of blake3
        tagged = "blake3-fallback:" + content
        return hashlib.sha256(tagged.encode("utf-8")).hexdigest()


def item_id(kind: str, content: str) -> str:
    digest = compute_sha256(kind + "\n" + content)
    return f"KMIT-{digest[:12].upper()}"


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

_MATURITY_MAP = {
    # explicit status strings from source files
    "VERIFIED": "verified",
    "VERIFIED_EMPIRICAL": "verified",
    "VERIFIED_FORMAL": "verified",
    "PARTIAL": "partial",
    "READY_FOR_TEST": "partial",
    "LATENT_SEED": "seed",
    "PRIORITY_TEST_ROUTE": "seed",
    "LATENT_ACTIVE": "latent",
    "LATENT": "latent",
    "TOKEN_VAZIO": "void",
    "BLOCKED": "void",
    "open": "void",
    "closed": "verified",
    # omega7 conditions
    "URGENT": "latent",
    "CRITICAL": "void",
}


def classify_maturity(status: str | None) -> str:
    if status is None:
        return "latent"
    key = str(status).upper().strip()
    return _MATURITY_MAP.get(key, _MATURITY_MAP.get(status, "latent"))


def classify_velocity(maturity: str) -> str:
    if maturity in ("immortal_verified", "verified"):
        return "medusa"
    if maturity in ("partial", "candidate"):
        return "equilibrado"
    return "tartaruga"


def ecosystem_role(kind: str, maturity: str) -> str:
    if kind == "validation":
        return "apex_validator"
    if kind == "formula":
        return "encoder"
    if kind == "concept":
        return "base_concept"
    if kind == "gap":
        return "buffer"
    if kind in ("result", "observation"):
        return "accumulator"
    if kind == "bridge":
        return "propagator"
    if kind == "thesis":
        return "catalyst"
    return "base_concept"


def queue_state(kind: str, maturity: str, raw_status: str | None) -> str:
    if raw_status and str(raw_status).lower() in ("closed", "verified", "verified_empirical"):
        return "executed"
    if kind == "formula":
        return "executed"
    if maturity == "void":
        return "void"
    if maturity in ("seed", "latent"):
        return "latent"
    if maturity in ("partial", "candidate"):
        return "in_queue"
    return "executed"


def d_vector(kind: str, maturity: str) -> list[float]:
    """7-dimensional direction vector — derived from kind and maturity."""
    kind_weights = {
        "formula": [1.0, 0.5, 0.2, 0.1, 0.1, 0.5, 0.8],
        "concept":  [0.7, 0.8, 0.3, 0.2, 0.4, 0.6, 0.5],
        "thesis":   [0.3, 0.4, 0.8, 0.7, 0.6, 0.3, 0.2],
        "gap":      [0.1, 0.2, 0.5, 0.9, 0.7, 0.2, 0.1],
        "observation": [0.6, 0.5, 0.4, 0.3, 0.5, 0.7, 0.6],
        "validation":  [0.9, 0.3, 0.2, 0.1, 0.8, 0.9, 0.7],
        "result":      [0.8, 0.4, 0.3, 0.2, 0.6, 0.8, 0.9],
        "bridge":      [0.5, 0.7, 0.6, 0.4, 0.5, 0.5, 0.4],
    }
    maturity_scale = {
        "immortal_verified": 1.0,
        "verified": 0.9,
        "partial": 0.6,
        "candidate": 0.5,
        "seed": 0.3,
        "latent": 0.2,
        "void": 0.0,
    }
    base = kind_weights.get(kind, [0.5] * 7)
    scale = maturity_scale.get(maturity, 0.5)
    return [round(v * scale, 4) for v in base]


# ---------------------------------------------------------------------------
# Item factory
# ---------------------------------------------------------------------------

def make_item(
    kind: str,
    label: str,
    source: str,
    raw_status: str | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    content = f"{source}|{label}"
    iid = item_id(kind, content)
    canonical = json.dumps({"kind": kind, "label": label, "source": source},
                           ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    sha = compute_sha256(canonical)
    b3 = compute_blake3(canonical)
    mat = classify_maturity(raw_status)
    vel = classify_velocity(mat)
    role = ecosystem_role(kind, mat)
    qstate = queue_state(kind, mat, raw_status)
    dv = d_vector(kind, mat)

    item: dict[str, Any] = {
        "item_id": iid,
        "kind": kind,
        "label": label,
        "source": source,
        "maturity_class": mat,
        "velocidade": vel,
        "D_vector": dv,
        "ecosystem_role": role,
        "queue_state": qstate,
        "sha256": sha,
        "blake3": b3,
        "academic_timestamp": GENERATED_AT,
        "retroalimentacao": {"feeds_into": [], "fed_by": []},
        "claim_allowed": False,
    }
    if raw_status:
        item["raw_status"] = raw_status
    if extra:
        item.update(extra)
    return item


# ---------------------------------------------------------------------------
# Source miners
# ---------------------------------------------------------------------------

def mine_formulas(root: Path) -> list[dict]:
    path = root / "artifacts" / "formulas" / "formulas.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    items = []
    for formula in data:
        label = formula.get("expression", formula.get("label", "unknown"))[:120]
        source = formula.get("source", "formulas.json")
        fi = formula.get("formula_id", "")
        items.append(make_item("formula", label, source,
                               raw_status="VERIFIED",
                               extra={"formula_id": fi,
                                      "category": formula.get("category", "")}))
    return items


def mine_route_forest(root: Path) -> list[dict]:
    path = root / "data" / "knowledge_forest" / "rll_route_forest_blueprint.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    nodes = data.get("nodes", {})
    items = []
    if isinstance(nodes, dict):
        for nid, node in nodes.items():
            label = node.get("label", nid)
            status = node.get("status", "LATENT_ACTIVE")
            scores = node.get("scores", {})
            items.append(make_item("concept", label, "rll_route_forest_blueprint.json",
                                   raw_status=status,
                                   extra={"node_id": nid,
                                          "tree": node.get("tree", ""),
                                          "scores": scores}))
    return items


def mine_epistemic_void(root: Path) -> list[dict]:
    path = root / "data" / "epistemic_void" / "rll_epistemic_void.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    records = data.get("records", [])
    items = []
    for rec in records:
        rid = rec.get("id", "?")
        state = rec.get("state", "TOKEN_VAZIO")
        # Main gap record
        items.append(make_item("gap", rec.get("question", rid),
                               "rll_epistemic_void.json",
                               raw_status=state,
                               extra={"epistemic_id": rid,
                                      "priority": rec.get("priority", "P2"),
                                      "epistemic_class": rec.get("epistemic_class", "")}))
        # Possibilities become thesis items
        for pos in rec.get("possibilities", []):
            if isinstance(pos, dict):
                plabel = pos.get("description", pos.get("label", str(pos)))
                pclass = pos.get("class", "H")
                mat = "candidate" if pclass == "H" else "seed"
                items.append(make_item("thesis", plabel[:120],
                                       f"rll_epistemic_void.json#{rid}",
                                       raw_status=mat.upper(),
                                       extra={"origin_gap": rid, "epistemic_class": pclass}))
            elif isinstance(pos, str):
                items.append(make_item("thesis", pos[:120],
                                       f"rll_epistemic_void.json#{rid}",
                                       raw_status="LATENT_SEED",
                                       extra={"origin_gap": rid}))
    return items


def mine_omega7(root: Path) -> list[dict]:
    path = root / "data" / "omega_operational" / "rll_omega7_operational.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    conditions = data.get("urgent_conditions", [])
    items = []
    for cond in conditions:
        cid = cond.get("condition_id", "?")
        stmt = cond.get("statement", cid)[:120]
        status = cond.get("status", "URGENT")
        priority = cond.get("priority", "P1")
        items.append(make_item("gap", stmt, "rll_omega7_operational.json",
                               raw_status=status,
                               extra={"condition_id": cid,
                                      "priority": priority,
                                      "direction_id": cond.get("direction_id", "")}))
    return items


def mine_latent_theses(root: Path) -> list[dict]:
    path = root / "data" / "real_sources" / "rll_latent_theses_registry.yml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text())
    theses = data.get("theses", [])
    items = []
    for thesis in theses:
        tid = thesis.get("id", "?")
        title = thesis.get("title", tid)
        state = thesis.get("state", "LATENT_ACTIVE")
        maturity = thesis.get("maturity", state)
        items.append(make_item("thesis", title,
                               "rll_latent_theses_registry.yml",
                               raw_status=maturity,
                               extra={"thesis_id": tid,
                                      "route": thesis.get("route", "")}))
    return items


def mine_dense_features(root: Path) -> list[dict]:
    path = root / "data" / "results" / "bootstrap" / "dense_behavior_features.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    feature_items = data.get("items", [])
    items = []
    for feat in feature_items:
        label = feat.get("label", feat.get("name", str(feat)[:80]))
        value = feat.get("value", "")
        items.append(make_item("observation", f"{label}: {str(value)[:60]}",
                               "dense_behavior_features.json",
                               raw_status="VERIFIED",
                               extra={"feature_label": label,
                                      "feature_value": value}))
    return items


def mine_falsifier_bundle(root: Path) -> list[dict]:
    path = root / "data" / "contracts" / "rll_falsifier_bundle.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    items = []
    for fal in data.get("falsifiers", []):
        fid = fal.get("id", "?")
        name = fal.get("name", fid)
        status = fal.get("status", "TOKEN_VAZIO")
        # Map falsifier status to maturity
        if status in ("PASS", "PASS [E]"):
            mat_status = "VERIFIED"
        elif status in ("FAIL", "FAIL [E]"):
            mat_status = "VERIFIED"  # empirically resolved, not void
        else:
            mat_status = "TOKEN_VAZIO"
        items.append(make_item("validation", name,
                               "rll_falsifier_bundle.json",
                               raw_status=mat_status,
                               extra={"falsifier_id": fid,
                                      "falsifier_status": status,
                                      "threshold": fal.get("threshold_value", ""),
                                      "result": fal.get("result", {})}))
    for gap in data.get("gaps", []):
        gid = gap.get("id", "?")
        label = gap.get("description", gid)[:120]
        items.append(make_item("gap", label,
                               "rll_falsifier_bundle.json",
                               raw_status=gap.get("status", "LATENT_ACTIVE"),
                               extra={"gap_id": gid}))
    return items


def mine_bridge_contracts(root: Path) -> list[dict]:
    contracts_dir = root / "data" / "contracts"
    if not contracts_dir.exists():
        return []
    items = []
    for path in sorted(contracts_dir.glob("*.v1.json")):
        if path.name in ("rll_falsifier_bundle.json", "fase29_integrity_lenses.v1.json"):
            continue
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        contract_id = data.get("contract_id", data.get("id", path.stem))
        title = data.get("title", data.get("name", contract_id))[:120]
        items.append(make_item("bridge", title, path.name,
                               raw_status=data.get("status", "PARTIAL"),
                               extra={"contract_id": contract_id}))
    return items


# ---------------------------------------------------------------------------
# Hypothesis generator
# ---------------------------------------------------------------------------

def generate_hypotheses(gaps: list[dict]) -> list[dict]:
    """Generate seed thesis items from void gaps."""
    hypotheses = []
    for gap in gaps:
        if gap.get("queue_state") != "void":
            continue
        gid = gap.get("condition_id") or gap.get("epistemic_id") or gap.get("gap_id") or gap["item_id"]
        label = f"Hipótese derivada de {gid}: {gap.get('label', '')[:60]}"
        content = f"hypothesis|{gid}|{label}"
        iid = f"KMHYP-{compute_sha256(content)[:12].upper()}"
        canonical = json.dumps({"kind": "thesis", "label": label, "source": gid},
                               ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        sha = compute_sha256(canonical)
        b3 = compute_blake3(canonical)
        hyp: dict[str, Any] = {
            "item_id": iid,
            "kind": "thesis",
            "label": label,
            "source": gap.get("source", "generated"),
            "maturity_class": "seed",
            "velocidade": "tartaruga",
            "D_vector": d_vector("thesis", "seed"),
            "ecosystem_role": "catalyst",
            "queue_state": "in_queue",
            "sha256": sha,
            "blake3": b3,
            "academic_timestamp": GENERATED_AT,
            "retroalimentacao": {"feeds_into": [], "fed_by": [gap["item_id"]]},
            "claim_allowed": False,
            "origin_gap": gid,
            "title": label,
            "predicted_observation": gap.get("exit_criteria", ""),
            "falsifier": gap.get("exit_criteria", ""),
        }
        hypotheses.append(hyp)
    return hypotheses


# ---------------------------------------------------------------------------
# Retroalimentação graph builder
# ---------------------------------------------------------------------------

def build_retroalimentacao(items: list[dict]) -> None:
    """Wire feeds_into/fed_by between items based on kind relationships."""
    id_map = {it["item_id"]: it for it in items}

    # Theses with origin_gap → fed_by gap
    for item in items:
        if item.get("origin_gap"):
            gap_iid = item["origin_gap"]
            # Find the gap by condition_id/epistemic_id
            for other in items:
                oid = (other.get("condition_id") or other.get("epistemic_id")
                       or other.get("gap_id") or "")
                if oid == gap_iid and other["item_id"] != item["item_id"]:
                    if other["item_id"] not in item["retroalimentacao"]["fed_by"]:
                        item["retroalimentacao"]["fed_by"].append(other["item_id"])
                    if item["item_id"] not in other["retroalimentacao"]["feeds_into"]:
                        other["retroalimentacao"]["feeds_into"].append(item["item_id"])
                    break

    # Validations (falsifiers) ← fed_by formulas (encoder)
    formula_ids = [it["item_id"] for it in items if it["kind"] == "formula"][:5]
    for item in items:
        if item["kind"] == "validation":
            item["retroalimentacao"]["fed_by"].extend(
                [fid for fid in formula_ids if fid not in item["retroalimentacao"]["fed_by"]]
            )

    # Bridges → feed_into concepts
    concept_ids = [it["item_id"] for it in items if it["kind"] == "concept"][:3]
    for item in items:
        if item["kind"] == "bridge":
            item["retroalimentacao"]["feeds_into"].extend(
                [cid for cid in concept_ids if cid not in item["retroalimentacao"]["feeds_into"]]
            )


# ---------------------------------------------------------------------------
# Academic timestamp chain
# ---------------------------------------------------------------------------

def build_matrix_chain(items: list[dict], previous_sha256: str = "GENESIS") -> dict:
    matrix_id = f"KM-RLL-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    content_digest = compute_sha256(
        json.dumps([it["item_id"] for it in items], sort_keys=True, separators=(",", ":"))
    )
    return {
        "matrix_id": matrix_id,
        "generated_at": GENERATED_AT,
        "previous_matrix_sha256": previous_sha256,
        "matrix_sha256": content_digest,
        "claim_boundary": CLAIM_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_outputs(items: list[dict], hypotheses: list[dict],
                  outdir: Path, chain: dict) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    # Master artifact
    master = {
        "schema": "rll_knowledge_matrix.schema.json",
        "claim_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "chain": chain,
        "item_count": len(items),
        "items": items,
    }
    master_path = outdir / "rll_knowledge_matrix.json"
    master_path.write_text(json.dumps(master, ensure_ascii=False, indent=2))

    # Summary
    by_kind: dict[str, int] = {}
    by_maturity: dict[str, int] = {}
    by_queue: dict[str, int] = {}
    for it in items:
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
        by_maturity[it["maturity_class"]] = by_maturity.get(it["maturity_class"], 0) + 1
        by_queue[it["queue_state"]] = by_queue.get(it["queue_state"], 0) + 1

    summary = {
        "total_items": len(items),
        "by_kind": by_kind,
        "by_maturity": by_maturity,
        "by_queue_state": by_queue,
        "hypothesis_count": len(hypotheses),
        "claim_allowed": False,
        "generated_at": GENERATED_AT,
    }
    (outdir / "knowledge_matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )

    # Hypotheses JSONL
    hyp_path = outdir / "knowledge_matrix_hypotheses.jsonl"
    with hyp_path.open("w", encoding="utf-8") as f:
        for hyp in hypotheses:
            f.write(json.dumps(hyp, ensure_ascii=False, separators=(",", ":")) + "\n")

    # CHECKSUMS
    checksums_lines = []
    for fpath in sorted(list(outdir.glob("*.json")) + list(outdir.glob("*.jsonl"))):
        content = fpath.read_text(encoding="utf-8")
        digest = compute_sha256(content)
        checksums_lines.append(f"{digest}  {fpath.name}")
    (outdir / "CHECKSUMS.sha256").write_text("\n".join(checksums_lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build RLL Knowledge Matrix — FASE 30")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--outdir", default="artifacts/knowledge-matrix",
                        help="Output directory")
    parser.add_argument("--previous-sha256", default="GENESIS",
                        help="Previous matrix SHA256 for chain")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    outdir = Path(args.outdir) if Path(args.outdir).is_absolute() else root / args.outdir

    print(f"[KM] Building Knowledge Matrix from {root}")
    print(f"[KM] Output: {outdir}")

    all_items: list[dict] = []

    miners = [
        ("formulas",         mine_formulas),
        ("route_forest",     mine_route_forest),
        ("epistemic_void",   mine_epistemic_void),
        ("omega7",           mine_omega7),
        ("latent_theses",    mine_latent_theses),
        ("dense_features",   mine_dense_features),
        ("falsifier_bundle", mine_falsifier_bundle),
        ("bridge_contracts", mine_bridge_contracts),
    ]

    for name, miner in miners:
        try:
            mined = miner(root)
            print(f"[KM]   {name}: {len(mined)} items")
            all_items.extend(mined)
        except Exception as exc:
            print(f"[KM]   {name}: ERROR — {exc}", file=sys.stderr)

    print(f"[KM] Total items before hypotheses: {len(all_items)}")

    # Generate hypotheses from void gaps
    gaps = [it for it in all_items if it["kind"] == "gap"]
    hypotheses = generate_hypotheses(gaps)
    print(f"[KM] Hypotheses generated: {len(hypotheses)}")

    # All items including hypotheses
    all_items.extend(hypotheses)

    # Wire retroalimentação
    build_retroalimentacao(all_items)

    # Build chain
    chain = build_matrix_chain(all_items, args.previous_sha256)

    write_outputs(all_items, hypotheses, outdir, chain)

    print(f"[KM] Done. {len(all_items)} total items written to {outdir}")
    print(f"[KM] Matrix SHA256: {chain['matrix_sha256']}")
    print(f"[KM] claim_allowed=false ✓")


if __name__ == "__main__":
    main()
