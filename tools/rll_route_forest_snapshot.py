#!/usr/bin/env python3
"""Materialize an effective RLL route-forest snapshot from base + overlay.

The base blueprint and append-only event file remain historical inputs. The
overlay records the exact migration, route patches, route additions and path
normalizations required for one coherent window. No scientific claim is
promoted by this transformation.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_BLUEPRINT = ROOT / "data/knowledge_forest/rll_route_forest_blueprint.json"
BASE_EVENTS = ROOT / "data/knowledge_forest/rll_route_flow_events.jsonl"
OVERLAY = ROOT / "data/knowledge_forest/rll_route_forest_overlay_20260731.json"


class OverlayError(RuntimeError):
    """Raised when an overlay cannot be applied without ambiguity."""


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise OverlayError(f"{path}: root must be an object")
    return value


def read_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise OverlayError(f"{path}:{number}: event must be an object")
        events.append(value)
    return events


def _normalize_refs(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, list):
        return [_normalize_refs(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_refs(item, replacements) for key, item in value.items()}
    if isinstance(value, str):
        return replacements.get(value, value)
    return value


def _validated_overlay(overlay: dict[str, Any]) -> dict[str, Any]:
    if overlay.get("schema") != "rll.route_forest_overlay.v1":
        raise OverlayError("unsupported overlay schema")
    if overlay.get("claim_allowed") is not False:
        raise OverlayError("overlay claim_allowed must remain false")
    replacements = overlay.get("path_normalizations", {})
    if not isinstance(replacements, dict):
        raise OverlayError("path_normalizations must be an object")
    return overlay


def apply_overlay(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    overlay = _validated_overlay(overlay)
    if base.get("forest_id") != overlay.get("base_forest_id"):
        raise OverlayError(
            f"overlay base mismatch: {overlay.get('base_forest_id')} != {base.get('forest_id')}"
        )

    result = copy.deepcopy(base)
    result["forest_id"] = overlay["target_forest_id"]
    result["generated_at"] = overlay["generated_at"]
    result["frequency_semantics"]["window_id"] = overlay["window_id"]

    routes = result["routes"]
    for route_id, patch in overlay.get("route_patches", {}).items():
        if route_id not in routes:
            raise OverlayError(f"route patch references unknown route: {route_id}")
        routes[route_id].update(copy.deepcopy(patch))

    for route_id, route in overlay.get("route_additions", {}).items():
        if route_id in routes:
            raise OverlayError(f"route addition collides with existing route: {route_id}")
        routes[route_id] = copy.deepcopy(route)

    result = _normalize_refs(result, overlay["path_normalizations"])

    source_ref = overlay.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref:
        raise OverlayError("overlay source_ref is required")
    if source_ref not in result["source_refs"]:
        result["source_refs"].append(source_ref)
    result["next_gate"] = (
        result["next_gate"]
        + " Snapshot overlay 20260731 reconciles real-data and methodology routes; "
        + "scientific claims remain blocked by their original gates."
    )
    return result


def apply_event_overlay(
    events: list[dict[str, Any]], overlay: dict[str, Any]
) -> list[dict[str, Any]]:
    overlay = _validated_overlay(overlay)
    result = _normalize_refs(copy.deepcopy(events), overlay["path_normalizations"])
    target_window = overlay["window_id"]
    for event in result:
        if event.get("window_id") != target_window:
            raise OverlayError(
                f"event {event.get('event_id')} belongs to {event.get('window_id')}, expected {target_window}"
            )
    return result


def load_effective_blueprint(
    base_path: Path = BASE_BLUEPRINT,
    overlay_path: Path = OVERLAY,
) -> dict[str, Any]:
    return apply_overlay(read_object(base_path), read_object(overlay_path))


def load_effective_events(
    events_path: Path = BASE_EVENTS,
    overlay_path: Path = OVERLAY,
) -> list[dict[str, Any]]:
    return apply_event_overlay(read_events(events_path), read_object(overlay_path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE_BLUEPRINT)
    parser.add_argument("--events", type=Path, default=BASE_EVENTS)
    parser.add_argument("--overlay", type=Path, default=OVERLAY)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events-output", type=Path)
    args = parser.parse_args()
    try:
        overlay = read_object(args.overlay)
        base = read_object(args.base)
        effective = apply_overlay(base, overlay)
        events = apply_event_overlay(read_events(args.events), overlay)
    except OverlayError as exc:
        print(f"ROUTE_FOREST_OVERLAY_ERROR: {exc}")
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(effective, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if args.events_output is not None:
        args.events_output.parent.mkdir(parents=True, exist_ok=True)
        args.events_output.write_text(
            "".join(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n" for event in events),
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "base_forest_id": base["forest_id"],
                "effective_forest_id": effective["forest_id"],
                "window_id": effective["frequency_semantics"]["window_id"],
                "route_count": len(effective["routes"]),
                "event_count": len(events),
                "claim_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
