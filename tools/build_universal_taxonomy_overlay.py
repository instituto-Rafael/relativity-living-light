#!/usr/bin/env python3
"""Build the additive RLL Universal Taxonomy 416 overlay.

The manifest and four lossless source shards preserve 30 baseline macrothemes
plus 386 user-supplied modules. The overlay is independently addressable and
never asserts novelty, truth, implementation, patentability, or solution of an
open problem.

claim_allowed=false
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

SOURCE_TIMESTAMP = "2026-07-28T00:00:00Z"
CLAIM_BOUNDARY = (
    "claim_allowed=false; taxonomy entry != scientific validation; "
    "analogy != mechanism; open problem != solved problem"
)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def blake3_or_tagged_sha256(text: str) -> str:
    try:
        import blake3  # type: ignore

        return blake3.blake3(text.encode("utf-8")).hexdigest()
    except ImportError:
        return sha256("blake3-fallback:" + text)


def item_id(kind: str, content: str) -> str:
    return f"KMIT-{sha256(kind + chr(10) + content)[:12].upper()}"


def load_registry(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    encoded = "".join(
        (manifest_path.parent / filename).read_text(encoding="ascii").strip()
        for filename in manifest["module_blob_parts"]
    )
    compressed = base64.b64decode(encoded, validate=True)
    modules = json.loads(gzip.decompress(compressed).decode("utf-8"))
    return manifest, modules


def state_projection(module: dict[str, Any]) -> tuple[str, str, str, list[float]]:
    cluster = module["cluster_id"]
    if cluster in {"V", "VIII"}:
        return "gap", "void", "buffer", [0.0] * 7
    if cluster in {"VI", "VII"}:
        return (
            "concept",
            "seed",
            "base_concept",
            [0.21, 0.24, 0.18, 0.12, 0.18, 0.15, 0.15],
        )
    return (
        "concept",
        "latent",
        "base_concept",
        [0.14, 0.16, 0.06, 0.04, 0.08, 0.12, 0.10],
    )


def build_item(module: dict[str, Any], source_path: str) -> dict[str, Any]:
    kind, maturity, role, d_vector = state_projection(module)
    label = module["label"]
    content = f"{source_path}|{module['module_id']}|{label}"
    canonical = json.dumps(
        {
            "kind": kind,
            "label": label,
            "source": source_path,
            "taxonomy_id": module["module_id"],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    item = {
        "item_id": item_id(kind, content),
        "kind": kind,
        "label": label,
        "source": source_path,
        "maturity_class": maturity,
        "velocidade": "tartaruga",
        "D_vector": d_vector,
        "ecosystem_role": role,
        "queue_state": "void" if maturity == "void" else "latent",
        "sha256": sha256(canonical),
        "blake3": blake3_or_tagged_sha256(canonical),
        "academic_timestamp": SOURCE_TIMESTAMP,
        "retroalimentacao": {"feeds_into": [], "fed_by": []},
        "claim_allowed": False,
        "taxonomy_id": module["module_id"],
        "source_index": module["source_index"],
        "cluster_id": module["cluster_id"],
        "cluster_position": module["cluster_position"],
        "epistemic_state": module["epistemic_state"],
        "completion_profile": module["completion_profile"],
        "completion_state": module["completion_state"],
    }
    if module.get("flags"):
        item["flags"] = module["flags"]
    if module.get("relations"):
        item["taxonomy_relations"] = module["relations"]
    return item


def build(manifest_path: Path) -> dict[str, Any]:
    manifest, modules = load_registry(manifest_path)
    source_path = str(manifest_path.as_posix())
    items = [build_item(module, source_path) for module in modules]
    ids = {item["taxonomy_id"]: item["item_id"] for item in items}
    for item in items:
        for relation in item.get("taxonomy_relations", []):
            if (
                relation.get("type") == "DUPLICATE_OF"
                and relation.get("target") in ids
            ):
                item["retroalimentacao"]["fed_by"].append(
                    ids[relation["target"]]
                )
    digest = sha256(
        json.dumps([item["item_id"] for item in items], separators=(",", ":"))
    )
    return {
        "schema": "rll_knowledge_matrix.schema.json",
        "overlay_id": "RLL-UNIVERSAL-TAXONOMY-416-OVERLAY-V1",
        "claim_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "baseline_macrothemes": manifest["source_provenance"][
            "baseline_macrothemes"
        ],
        "taxonomy_module_count": len(items),
        "taxonomy_total": manifest["source_provenance"]["baseline_macrothemes"]
        + len(items),
        "knowledge_matrix_count_semantics": "independent_overlay_not_main_matrix_total",
        "source_registry": source_path,
        "matrix_sha256": digest,
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        default="data/knowledge_taxonomy/rll_universal_taxonomy_416.v1.json",
    )
    parser.add_argument(
        "--output",
        default="artifacts/knowledge-matrix/rll_universal_taxonomy_416_overlay.json",
    )
    args = parser.parse_args()
    overlay = build(Path(args.registry))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(overlay, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[UT416] modules={overlay['taxonomy_module_count']}")
    print(f"[UT416] taxonomy_total={overlay['taxonomy_total']}")
    print(f"[UT416] sha256={overlay['matrix_sha256']}")
    print("[UT416] claim_allowed=false")


if __name__ == "__main__":
    main()
