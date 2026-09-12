#!/usr/bin/env python3
"""Validate the bounded RLL rest-frame sound-speed comparator contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_PERTURBATION_SOUND_SPEED_CANDIDATE_V1.json"

REQUIRED_UNRESOLVED = {
    "GROWTH-QMU-001",
    "GROWTH-SIGMA-001",
    "GROWTH-GAUGE-001",
    "GROWTH-IC-001",
    "GROWTH-CONSERVATION-001",
}


def load() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    d = load()
    errors: list[str] = []
    candidate = d.get("candidate", {})
    semantics = d.get("semantics", {})

    if d.get("id") != "GROWTH-CS2-001":
        errors.append("wrong contract id")
    if d.get("state") != "CONFIGURED_CANDIDATE_NOT_EFFECTIVE":
        errors.append("state must remain CONFIGURED_CANDIDATE_NOT_EFFECTIVE")
    if d.get("claim_allowed") is not False or d.get("publication_ready") is not False:
        errors.append("claim/publication boundary must remain false")

    cs2 = candidate.get("rest_frame_cs2")
    if not isinstance(cs2, (int, float)) or not (0.0 <= float(cs2) <= 1.0):
        errors.append("rest_frame_cs2 must be numeric and causal in [0,1]")
    if float(cs2) != 1.0:
        errors.append("V1 comparator must pin rest_frame_cs2=1.0")
    if candidate.get("derived_from_rll_background") is not False:
        errors.append("candidate must not be represented as RLL-background-derived")
    if candidate.get("independent_of_ca2") is not True:
        errors.append("candidate must be independent of ca2")
    if candidate.get("role") != "comparator_only_not_RLL_derived":
        errors.append("candidate role boundary mismatch")

    if semantics.get("ca2_relation") != "DO_NOT_SET_CS2_EQUAL_CA2":
        errors.append("c_s^2=c_a^2 must remain forbidden for this candidate")
    if semantics.get("entropy_freedom_required_when_cs2_ne_ca2") is not True:
        errors.append("entropy freedom boundary missing")
    if semantics.get("effective_in_perturbation_solver") is not False:
        errors.append("configuration must not be marked effective")
    if semantics.get("gauge_pressure_mapping") != "TOKEN_VAZIO_GAUGE_POLICY":
        errors.append("gauge pressure mapping must remain TOKEN_VAZIO")

    unresolved = set(d.get("unresolved_dependencies", []))
    if unresolved != REQUIRED_UNRESOLVED:
        errors.append(
            f"unresolved dependency mismatch: {sorted(unresolved)} != {sorted(REQUIRED_UNRESOLVED)}"
        )

    refs = d.get("provenance", [])
    if len(refs) < 3:
        errors.append("insufficient provenance")
    if not any("astro-ph/9801234" in str(row) for row in refs):
        errors.append("Hu GDM primary literature provenance missing")
    if not any("astro-ph/0307104" in str(row) for row in refs):
        errors.append("Weller-Lewis primary literature provenance missing")

    return {
        "schema": "rll.perturbation_sound_speed_candidate_validation.v1",
        "pass": not errors,
        "errors": errors,
        "state": d.get("state"),
        "candidate_name": candidate.get("name"),
        "rest_frame_cs2": cs2,
        "configured": True,
        "effective": False,
        "claim_allowed": False,
        "publication_ready": False,
        "next_gap": "GROWTH-QMU-001",
        "status": (
            "SOUND_SPEED_CANDIDATE_CONFIG_VALID"
            if not errors
            else "SOUND_SPEED_CANDIDATE_CONFIG_BLOCKED"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        out = args.output if args.output.is_absolute() else ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
