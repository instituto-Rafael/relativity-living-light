#!/usr/bin/env python3
"""Generate discipline-oriented work packets from the canonical RLL closure registry."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from rx.kernel import dump_json, load_json
from tools.rll_closure_queue import build as build_queue

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance/RLL_CLOSURE_WORKSTREAM_REGISTRY_V1.json"
OUT_JSON = ROOT / "results/rll_closure_work_packets.json"
OUT_MD = ROOT / "results/rll_closure_work_packets.md"


def build():
    registry = load_json(REGISTRY)
    queue = build_queue()
    effective = {row["id"]: row["effective_state"] for row in queue["queue"]}
    packets = defaultdict(list)

    for row in registry.get("workstreams", []):
        for discipline in row.get("discipline", []):
            packets[str(discipline)].append({
                "workstream": row["id"],
                "priority": row.get("priority"),
                "name": row.get("name"),
                "effective_state": effective.get(row["id"], "TOKEN_VAZIO"),
                "dependencies": row.get("dependencies", []),
                "objective": row.get("objective"),
                "first_task": (row.get("tasks") or ["TOKEN_VAZIO"])[0],
                "all_tasks": row.get("tasks", []),
                "required_outputs": row.get("required_outputs", []),
                "falsifier": row.get("falsifier"),
                "closes_tokens": row.get("closes_tokens", []),
                "claim_allowed": False,
            })

    ordered = {}
    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
    for discipline in sorted(packets):
        ordered[discipline] = sorted(
            packets[discipline],
            key=lambda item: (
                priority_rank.get(str(item["priority"]), 9),
                item["workstream"],
            ),
        )

    ready_assignments = []
    for discipline, rows in ordered.items():
        for row in rows:
            if row["effective_state"] == "READY":
                ready_assignments.append({
                    "discipline": discipline,
                    "workstream": row["workstream"],
                    "priority": row["priority"],
                    "first_task": row["first_task"],
                    "required_outputs": row["required_outputs"],
                })

    return {
        "schema": "rll.closure_work_packets.v1",
        "workstream_count": queue["workstream_count"],
        "discipline_count": len(ordered),
        "packets": ordered,
        "ready_assignments": ready_assignments,
        "claim_allowed": False,
        "boundary": "Assignment readiness follows declared dependencies and evidence states; it does not imply scientific correctness or authorize a claim.",
    }


def write(payload):
    dump_json(OUT_JSON, payload)
    lines = [
        "# RLL Closure Work Packets",
        "",
        "Claim allowed: **false**.",
        "",
        "## Ready assignments",
        "",
        "| discipline | WS | priority | first task |",
        "|---|---|---|---|",
    ]
    for row in payload["ready_assignments"]:
        lines.append("| %s | %s | %s | %s |" % (
            row["discipline"],
            row["workstream"],
            row["priority"],
            str(row["first_task"]).replace("|", "/"),
        ))
    for discipline, rows in payload["packets"].items():
        lines += ["", "## " + discipline, ""]
        for row in rows:
            lines.append(
                "- **%s / %s / %s** — %s" % (
                    row["workstream"],
                    row["priority"],
                    row["effective_state"],
                    row["name"],
                )
            )
            lines.append("  - next: " + str(row["first_task"]))
            lines.append("  - output: " + ", ".join(row["required_outputs"] or ["TOKEN_VAZIO"]))
            lines.append("  - falsifier: " + str(row["falsifier"]))
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        write(payload)
    print(json.dumps({
        "workstream_count": payload["workstream_count"],
        "discipline_count": payload["discipline_count"],
        "ready_assignment_count": len(payload["ready_assignments"]),
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", OUT_JSON.relative_to(ROOT))
        print("wrote", OUT_MD.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
