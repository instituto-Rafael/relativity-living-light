#!/usr/bin/env python3
"""Compile the effective RLL route forest from historical base + overlay.

This is the canonical snapshot entry point. It delegates graph semantics and
artifact generation to ``build_rll_route_forest`` after materializing the
versioned overlay. It performs no model training and promotes no claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_rll_route_forest as compiler
from tools.rll_route_forest_snapshot import (
    BASE_BLUEPRINT,
    BASE_EVENTS,
    OVERLAY,
    OverlayError,
    load_effective_blueprint,
    load_effective_events,
)

ARTIFACT_DIR = ROOT / "artifacts/route-forest"


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blueprint", type=Path, default=BASE_BLUEPRINT)
    parser.add_argument("--events", type=Path, default=BASE_EVENTS)
    parser.add_argument("--overlay", type=Path, default=OVERLAY)
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    try:
        blueprint = load_effective_blueprint(args.blueprint, args.overlay)
        events = load_effective_events(args.events, args.overlay)
    except OverlayError as exc:
        summary = {
            "passed": False,
            "findings": [f"overlay: {exc}"],
            "forest_id": None,
            "state": None,
            "claim_allowed": False,
        }
        print(canonical(summary), end="")
        return 1 if args.strict else 0

    findings = compiler.schema_findings(
        blueprint, compiler.read_json(compiler.BLUEPRINT_SCHEMA), "blueprint"
    )
    for index, event in enumerate(events):
        findings += compiler.schema_findings(
            event, compiler.read_json(compiler.EVENT_SCHEMA), f"event[{index}]"
        )
    findings += compiler.semantic_findings(blueprint, events)

    forest = None
    if not findings:
        forest = compiler.compile_forest(blueprint, events)
        findings += compiler.schema_findings(
            forest, compiler.read_json(compiler.OUTPUT_SCHEMA), "forest"
        )
    if forest is not None and args.write_report:
        compiler.write_artifacts(forest, args.artifact_dir)

    summary = {
        "passed": not findings,
        "findings": findings,
        "forest_id": None if forest is None else forest["forest_id"],
        "state": None if forest is None else forest["state"],
        "regions": None if forest is None else forest["metrics"]["region_count"],
        "trees": None if forest is None else forest["metrics"]["tree_count"],
        "nodes": None if forest is None else forest["metrics"]["node_count"],
        "routes": None if forest is None else forest["metrics"]["route_count"],
        "events": None if forest is None else forest["metrics"]["event_count"],
        "claim_allowed": False,
    }
    print(canonical(summary), end="")
    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
