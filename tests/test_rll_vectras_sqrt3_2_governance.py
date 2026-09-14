"""Validate structural integrity of the RLL-Vectras-sqrt3_2 governance matrix.

This test checks that the governance document contains the required sections,
markers, and separation-of-responsibility declarations. It does NOT validate
scientific claims or production integration.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "governance" / "RLL_VECTRAS_SQRT3_2_GOVERNANCE_MATRIX.md"


def _read() -> str:
    return MATRIX.read_text(encoding="utf-8")


def test_governance_matrix_file_exists() -> None:
    assert MATRIX.exists(), f"governance matrix not found: {MATRIX}"


def test_governance_matrix_required_status_marker() -> None:
    text = _read()
    assert "governance_record / friction_map / claim_boundary / no_claim_promotion" in text


def test_governance_matrix_no_claim_promotion_marker() -> None:
    text = _read()
    assert "no_claim_promotion" in text


def test_governance_matrix_contains_rll_responsibilities() -> None:
    text = _read()
    assert "### RLL" in text
    assert "a_h = sqrt(3)/2" in text
    assert "z_h" in text
    assert "delta_chi2" in text


def test_governance_matrix_contains_vectras_responsibilities() -> None:
    text = _read()
    assert "### Vectras" in text
    assert "Q16.16" in text
    assert "branchless" in text or "freestanding" in text


def test_governance_matrix_compatibility_table_present() -> None:
    text = _read()
    assert "| Elemento |" in text or "| h=sqrt(3)/2 |" in text


def test_governance_matrix_epistemological_guards_present() -> None:
    text = _read()
    assert "Guardas epistemológicas" in text or "guardas" in text.lower()
    assert "TOKEN_VAZIO" in text
    assert "operador" in text.lower() or "Operador" in text


def test_governance_matrix_cosmology_pivot_decision_present() -> None:
    text = _read()
    assert "cosmology_pivot" in text or "cosmology pivot" in text.lower()
    assert "fica no RLL" in text or "Fica em RLL" in text or "RLL documenta" in text


def test_governance_matrix_pr_decision_criteria_present() -> None:
    text = _read()
    assert "Critérios de decisão" in text
    assert "regressão" in text


def test_governance_matrix_cross_references_present() -> None:
    text = _read()
    assert "docs/invariants/sqrt3_2_kernel.md" in text
    assert "docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md" in text
