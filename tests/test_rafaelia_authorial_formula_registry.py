from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/formulas/RAFAELIA_168_FORMULAS_AUTORAIS_2026-09-12.md"
MANIFEST = ROOT / "data/formulas/RAFAELIA_AUTHORIAL_FORMULA_REGISTRY_V1.json"


def test_authorial_formula_registry_count() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    assert text.count("**AFR-") == 168


def test_authorial_formula_registry_bounds() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    assert "**AFR-001" in text
    assert "**AFR-168" in text
    assert "**AFR-169" not in text


def test_authorial_formula_registry_manifest() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["formula_count"] == 168
    assert data["family_count"] == 12
    assert data["claim_allowed"] is False
    assert data["state"] == "CANDIDATE_REGISTRY_NOT_PEER_REVIEWED"
    assert "PROJECT_DEFINED_FORMULA != PHYSICAL_LAW" in data["invariants"]
