#!/usr/bin/env python3
"""Build/check the current-state overlay for the historical FASE17-20 graph.

The FASE17-20 graph is a frozen historical snapshot. FASE22 later quantified G4.
This overlay preserves both truths without rewriting the original phase chronology.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "session_grafo_fase17_20" / "current_state_overlay.json"


def build_overlay() -> dict[str, Any]:
    return {
        "schema": "rll.session_graph.current_state_overlay.v1",
        "snapshot": {
            "session_id": "SESSION_FASE17_20_2026-07-14_15",
            "through_phase": 20,
            "generated_utc": "2026-07-16T00:00:00Z",
            "gap_states": {
                "G1": "FECHADO",
                "G2": "FECHADO",
                "G3": "FECHADO",
                "G4": "TOKEN_VAZIO",
            },
        },
        "current_state": {
            "through_phase": 22,
            "as_of_utc": "2026-07-16T21:00:00Z",
            "gap_states": {
                "G1": "FECHADO",
                "G2": "FECHADO",
                "G3": "FECHADO",
                "G4": "VERIFIED_LIMITED",
            },
            "gap_lifecycle": {
                "G4": "CLOSED_AS_QUANTIFIED_SYSTEMATIC",
            },
            "all_original_gaps_closed": True,
            "claim_allowed": False,
        },
        "transitions": [
            {
                "gap_id": "G4",
                "from_state": "TOKEN_VAZIO",
                "to_state": "VERIFIED_LIMITED",
                "lifecycle": "CLOSED_AS_QUANTIFIED_SYSTEMATIC",
                "closed_in_phase": 22,
                "closed_by_pr": "#556",
                "script": "scripts/rll_fase22_g4_eh_bias_grid.py",
                "artifact": "results/rll_fase22_g4_eh_bias_grid.json",
                "audit_document": (
                    "docs/cronologia-auditoria/21_FASE22_G4_EH_BIAS_GRID.md"
                ),
                "result": {
                    "grid": "10x10",
                    "posterior_systematic_mpc": 0.7214,
                    "estimated_delta_ln_b10": "0.1 to 1.0",
                    "qualitative_model_comparison_changed": False,
                },
                "residual_limitation": {
                    "description": (
                        "Recompute rd with CAMB/RECFAST at each MCMC point "
                        "for precision analysis."
                    ),
                    "status": "TOKEN_VAZIO",
                    "priority": "P1",
                },
            }
        ],
        "boundary": (
            "The overlay synchronizes historical and current repository state. "
            "It does not rewrite the FASE17-20 snapshot, eliminate the residual "
            "precision limitation, allow a superiority claim, or replace "
            "independent review."
        ),
    }


def canonical_text() -> str:
    return json.dumps(build_overlay(), ensure_ascii=False, indent=2) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected = canonical_text()
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
        print(f"WROTE: {args.output}")
        return 0

    if not args.output.exists():
        raise SystemExit(f"missing overlay: {args.output}")
    actual = args.output.read_text(encoding="utf-8")
    if actual != expected:
        raise SystemExit(
            "current-state overlay is stale; run "
            "python scripts/build_session_grafo_current_state_overlay.py --write"
        )
    print("OK: FASE17-20 historical snapshot and FASE22 current state are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
