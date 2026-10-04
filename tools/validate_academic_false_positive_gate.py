#!/usr/bin/env python3
"""Fail closed on positive real-data claims without confirmatory controls.

This validator treats favorable AIC/BIC/chi2 output as screening, not as a
scientific claim. A positive claim requires an explicit confirmatory_evidence
mapping that passes the academic_false_positive_gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rll.academic_false_positive_gate import academic_false_positive_gate

POSITIVE_LABELS = {"rll_preferred_tentative", "rll_preferred_strong"}
SCAN_ROOTS = (ROOT / "results", ROOT / "data" / "results")


def iter_json_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            files.extend(path for path in root.rglob("*.json") if path.is_file())
    return sorted(set(files))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_real_result(mapping: dict[str, Any]) -> bool:
    return mapping.get("dataset_type") == "real_observational"


def walk_real_results(value: Any, location: str = "$") -> Iterator[tuple[dict[str, Any], str]]:
    """Yield every explicitly real-observational mapping, including nested ones."""
    if isinstance(value, dict):
        if _is_real_result(value):
            yield value, location
        for key, child in value.items():
            yield from walk_real_results(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_real_results(child, f"{location}[{index}]")


def validate_real_result(path: Path, mapping: dict[str, Any], location: str = "$") -> list[str]:
    errors: list[str] = []
    if not _is_real_result(mapping):
        return errors

    label = str(mapping.get("interpretation_label", ""))
    top_claim = mapping.get("claim_allowed") is True
    policy = mapping.get("claim_policy")
    policy_claim = isinstance(policy, dict) and policy.get("claim_allowed") is True
    positive_screen = label in POSITIVE_LABELS or top_claim or policy_claim

    gate = academic_false_positive_gate(positive_screen, mapping.get("confirmatory_evidence"))
    identity = f"{path.relative_to(ROOT)}::{location}"

    if (top_claim or policy_claim) and not gate["confirmatory_ready"]:
        errors.append(
            f"{identity} promotes claim_allowed=true without confirmatory evidence: "
            f"{gate['missing_or_failed']}"
        )

    if label in POSITIVE_LABELS and not gate["confirmatory_ready"] and top_claim:
        errors.append(f"{identity} treats a favorable screening label as a confirmed claim")

    return errors


def main() -> int:
    errors: list[str] = []
    checked = 0
    for path in iter_json_files():
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        for mapping, location in walk_real_results(payload):
            checked += 1
            errors.extend(validate_real_result(path, mapping, location))

    if errors:
        print("ACADEMIC_FALSE_POSITIVE_GATE=FAIL")
        for error in errors:
            print(f"- {error}")
        return 2

    print(f"ACADEMIC_FALSE_POSITIVE_GATE=PASS checked_real_results={checked}")
    print("boundary=screening_positive != confirmatory_ready != scientific_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
