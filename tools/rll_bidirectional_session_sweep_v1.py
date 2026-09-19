#!/usr/bin/env python3
"""Bidirectional recurrent sweep over the RLL session fragment ledger.

This is a discovery/routing heuristic. It never promotes scientific claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_OPERATORS = (
    "DIRECT",
    "DERIVATIVE",
    "ANTIDERIVATIVE",
    "INVERSE",
    "REVERSE",
    "RECURSIVE",
    "LOG",
    "LATENT_RELATION_PROBE",
)


@dataclass(frozen=True)
class Fragment:
    id: str
    name: str
    layer: str
    impact: float
    uncertainty_reduction: float
    effort: float
    undercoverage: float
    recurrence: float
    testability: float
    novelty: float
    provenance: float
    claim_gate: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Fragment":
        return cls(
            id=str(row["id"]),
            name=str(row["name"]),
            layer=str(row["layer"]),
            impact=float(row["impact"]),
            uncertainty_reduction=float(row["uncertainty_reduction"]),
            effort=float(row["effort"]),
            undercoverage=float(row["undercoverage"]),
            recurrence=float(row["recurrence"]),
            testability=float(row["testability"]),
            novelty=float(row["novelty"]),
            provenance=float(row["provenance"]),
            claim_gate=str(row["claim_gate"]),
        )


def stable_hash(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def priority(f: Fragment) -> float:
    if min(f.impact, f.uncertainty_reduction, f.effort) <= 0:
        raise ValueError(f"non-positive priority factor: {f.id}")
    return (
        math.log2(f.impact)
        + math.log2(f.uncertainty_reduction)
        - math.log2(f.effort)
        + f.undercoverage
        + f.recurrence
        + f.testability
        + 0.75 * f.novelty
        + 1.25 * f.provenance
    )


def weighted_jump(
    rng: random.Random,
    fragments: list[Fragment],
    anchor: Fragment,
    excluded: set[str],
) -> Fragment | None:
    pool = [
        f for f in fragments
        if f.id not in excluded and f.id != anchor.id and f.layer != anchor.layer
    ]
    if not pool:
        return None
    weights = [max(priority(f), 1e-9) for f in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


def relation_probe(
    a: Fragment,
    b: Fragment,
    *,
    direction: str,
    cycle: int,
    representation_hash: str,
) -> dict[str, Any]:
    pair_key = stable_hash("PAIR", *sorted((a.id, b.id)))
    directional_key = stable_hash("DIR", a.id, b.id, direction)
    return {
        "type": "RELATION_PROBE",
        "pair_id": pair_key,
        "directional_id": directional_key,
        "from": a.id,
        "to": b.id,
        "from_layer": a.layer,
        "to_layer": b.layer,
        "direction": direction,
        "cycle": cycle,
        "representation_parent": representation_hash,
        "operators": list(DEFAULT_OPERATORS),
        "dilog_enabled": False,
        "claim_allowed": False,
        "question": (
            f"Test whether {a.id} constrains, mediates, predicts, reconstructs, "
            f"or falsifies {b.id} under explicit layer/time/unit/compartment rules."
        ),
    }


def structural_gaps(f: Fragment, raw: dict[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    empirical_exempt = {"METHOD", "METHOD_RULE", "INVARIANT", "NEGATIVE_BOUNDARY"}
    if f.claim_gate not in empirical_exempt:
        for key in ("falsifier", "source_refs"):
            if key not in raw:
                gaps.append({
                    "gap_id": stable_hash("META", f.id, key),
                    "fragment": f.id,
                    "kind": f"TOKEN_VAZIO_{key.upper()}",
                    "claim_allowed": False,
                })
    if f.layer in {
        "physical_chemistry", "bioenergetics", "metabolomics", "interstitium",
        "amino_acid_flux", "thermogenesis", "body_composition", "endocrine",
        "purinergic_signaling", "phase_partition", "replication",
    }:
        for key in ("units", "time_axis"):
            if key not in raw:
                gaps.append({
                    "gap_id": stable_hash("META", f.id, key),
                    "fragment": f.id,
                    "kind": f"TOKEN_VAZIO_{key.upper()}",
                    "claim_allowed": False,
                })
    if f.layer in {
        "physical_chemistry", "bioenergetics", "metabolomics", "interstitium",
        "amino_acid_flux", "purinergic_signaling", "phase_partition",
    } and "compartment" not in raw:
        gaps.append({
            "gap_id": stable_hash("META", f.id, "compartment"),
            "fragment": f.id,
            "kind": "TOKEN_VAZIO_COMPARTMENT",
            "claim_allowed": False,
        })
    return gaps


def select_targets(
    ordered: list[Fragment],
    idx: int,
    all_fragments: list[Fragment],
    rng: random.Random,
    *,
    fanout: int,
) -> list[Fragment]:
    anchor = ordered[idx]
    selected: list[Fragment] = []
    seen = {anchor.id}

    # local traversal neighbors preserve chronology/proximity
    for j in (idx + 1, idx + 2):
        if j < len(ordered):
            f = ordered[j]
            if f.id not in seen:
                selected.append(f)
                seen.add(f.id)
            if len(selected) >= fanout:
                return selected

    # one deterministic high-priority cross-layer target
    cross = [f for f in all_fragments if f.layer != anchor.layer and f.id not in seen]
    if cross and len(selected) < fanout:
        cross.sort(key=lambda x: (-priority(x), x.id))
        selected.append(cross[0])
        seen.add(cross[0].id)

    # representation-dependent weighted jumps
    while len(selected) < fanout:
        nxt = weighted_jump(rng, all_fragments, anchor, seen)
        if nxt is None:
            break
        selected.append(nxt)
        seen.add(nxt.id)

    return selected


def second_order_probes(
    first_order: list[dict[str, Any]],
    *,
    cycle: int,
    representation_hash: str,
    budget: int,
) -> list[dict[str, Any]]:
    # Compose only probes sharing a fragment; bounded by budget.
    out: list[dict[str, Any]] = []
    for i, a in enumerate(first_order):
        aset = {a["from"], a["to"]}
        for b in first_order[i + 1:]:
            if not aset.intersection({b["from"], b["to"]}):
                continue
            rid = stable_hash("R2", *sorted((a["directional_id"], b["directional_id"])))
            out.append({
                "type": "RELATION_OF_RELATIONS_PROBE",
                "probe_id": rid,
                "parents": sorted((a["directional_id"], b["directional_id"])),
                "cycle": cycle,
                "representation_parent": representation_hash,
                "operator": "RECOMBINE",
                "claim_allowed": False,
            })
            if len(out) >= budget:
                return out
    return out


def run(
    ledger: dict[str, Any],
    *,
    seed: int = 42,
    max_cycles: int = 6,
    fanout: int = 4,
    second_order_budget: int = 32,
    epsilon: float = 0.02,
    patience_cycles: int = 2,
) -> dict[str, Any]:
    raw_rows = list(ledger["fragments"])
    fragments = [Fragment.from_dict(x) for x in raw_rows]
    raw_by_id = {str(x["id"]): x for x in raw_rows}

    known_pairs = {
        stable_hash("PAIR", *sorted(tuple(x.get("fragments", []))))
        for x in ledger.get("candidate_crosslinks", [])
        if len(x.get("fragments", [])) == 2
    }
    discovered: set[str] = set()
    relation_seen: set[str] = set(known_pairs)
    meta_seen: set[str] = set()
    representation_hash = stable_hash("REP0", ledger.get("schema", "unknown"))
    cycles: list[dict[str, Any]] = []
    stale_cycles = 0

    # Structural metadata gaps are stable and counted once.
    structural: list[dict[str, Any]] = []
    for f in fragments:
        structural.extend(structural_gaps(f, raw_by_id[f.id]))
    for g in structural:
        meta_seen.add(g["gap_id"])
        discovered.add(g["gap_id"])

    for cycle in range(max_cycles):
        cycle_seed = int(stable_hash(str(seed), str(cycle), representation_hash)[:16], 16)
        rng = random.Random(cycle_seed)
        new_ids: set[str] = set()
        first_order: list[dict[str, Any]] = []
        direction_counts: dict[str, int] = {}

        for direction, ordered in (
            ("FORWARD", fragments),
            ("REVERSE", list(reversed(fragments))),
        ):
            count = 0
            for idx, anchor in enumerate(ordered):
                targets = select_targets(
                    ordered, idx, fragments, rng, fanout=fanout
                )
                for target in targets:
                    probe = relation_probe(
                        anchor, target,
                        direction=direction,
                        cycle=cycle,
                        representation_hash=representation_hash,
                    )
                    first_order.append(probe)
                    count += 1
                    pid = probe["pair_id"]
                    if pid not in relation_seen:
                        relation_seen.add(pid)
                        new_ids.add(pid)
            direction_counts[direction] = count

        r2 = second_order_probes(
            first_order,
            cycle=cycle,
            representation_hash=representation_hash,
            budget=second_order_budget,
        )
        for probe in r2:
            pid = probe["probe_id"]
            if pid not in discovered:
                new_ids.add(pid)

        inspected = len(first_order) + len(r2)
        ratio = len(new_ids) / max(1, inspected)
        discovered.update(new_ids)

        new_representation_hash = stable_hash(
            "REP",
            representation_hash,
            *sorted(new_ids),
            *sorted(relation_seen),
        )

        cycles.append({
            "cycle": cycle,
            "cycle_seed": cycle_seed,
            "representation_in": representation_hash,
            "representation_out": new_representation_hash,
            "direction_counts": direction_counts,
            "first_order_probes": len(first_order),
            "second_order_probes": len(r2),
            "new_gap_or_probe_ids": len(new_ids),
            "marginal_new_ratio": round(ratio, 8),
        })

        if ratio < epsilon:
            stale_cycles += 1
        else:
            stale_cycles = 0

        representation_hash = new_representation_hash
        if stale_cycles >= patience_cycles:
            break

    stop_reason = (
        "SATURATED_UNDER_CURRENT_RULER"
        if stale_cycles >= patience_cycles
        else "MAX_CYCLES_REACHED"
    )
    return {
        "schema": "rll.bidirectional_session_sweep.v1",
        "source_schema": ledger.get("schema"),
        "claim_allowed": False,
        "complete": False,
        "terminal_state": stop_reason,
        "verbatim_transcript_bound": False,
        "structural_metadata_gaps": structural,
        "cycles": cycles,
        "final_representation_hash": representation_hash,
        "unique_discovered_ids": len(discovered),
        "known_or_discovered_pair_ids": len(relation_seen),
        "rule": "SATURATED_UNDER_CURRENT_RULER != COMPLETE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--output")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-cycles", type=int, default=6)
    ap.add_argument("--fanout", type=int, default=4)
    ap.add_argument("--second-order-budget", type=int, default=32)
    ap.add_argument("--epsilon", type=float, default=0.02)
    ap.add_argument("--patience-cycles", type=int, default=2)
    args = ap.parse_args()

    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    result = run(
        ledger,
        seed=args.seed,
        max_cycles=args.max_cycles,
        fanout=args.fanout,
        second_order_budget=args.second_order_budget,
        epsilon=args.epsilon,
        patience_cycles=args.patience_cycles,
    )
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
