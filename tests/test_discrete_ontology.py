import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from rll.discrete_ontology import (
    ClaimState,
    DiscreteWord,
    FractionPresentation,
    TypedClass,
    disjoint_union_cardinality,
    evaluate_factor11_gate,
    observable_is_representation_invariant,
    same_rational_value,
)


def test_typed_empty_classes_share_cardinality_but_not_identity() -> None:
    empty_events = TypedClass.from_members("event", [])
    empty_particles = TypedClass.from_members("particle", [])

    assert empty_events.cardinality == 0
    assert empty_particles.cardinality == 0
    assert empty_events != empty_particles


def test_two_unit_classes_have_disjoint_union_cardinality_two() -> None:
    left = TypedClass.from_members("unit", ["u"])
    right = TypedClass.from_members("unit", ["u"])

    assert left.cardinality == right.cardinality == 1
    assert disjoint_union_cardinality(left, right) == 2


def test_word_11_is_not_arithmetic_eleven_or_cardinality_two() -> None:
    word = DiscreteWord.from_text("11")

    assert word.text() == "11"
    assert word.length == 2
    assert word.multiplicity("1") == 2
    assert int(word.text()) == 11
    assert word.length != int(word.text())


def test_fraction_presentation_preserves_factor_11_provenance() -> None:
    scaled = FractionPresentation(77, 33)

    assert scaled.value == Fraction(7, 3)
    assert scaled.reduced_pair == (7, 3)
    assert scaled.common_scale == 11
    assert scaled.provenance_record() == {
        "presentation": [77, 33],
        "reduced_pair": [7, 3],
        "rational_value": "7/3",
        "common_scale": 11,
    }


def test_fraction_denominator_zero_is_rejected() -> None:
    with pytest.raises(ZeroDivisionError):
        FractionPresentation(1, 0)


def test_rational_observable_is_invariant_to_factor_11() -> None:
    scaled = FractionPresentation(77, 33)
    reduced = FractionPresentation(7, 3)

    assert same_rational_value(scaled, reduced)
    assert observable_is_representation_invariant(lambda item: item.value, scaled, reduced)


def test_default_factor11_gate_preserves_token_vazio() -> None:
    report = evaluate_factor11_gate()

    assert report.same_rational_value is True
    assert report.recovered_common_scale == 11
    assert report.mathematical_state is ClaimState.PASS_EXACT
    assert report.physical_coupling_state is ClaimState.TOKEN_VAZIO
    assert report.claim_allowed is False
    assert "units" in report.next_gate


def test_invariant_observable_blocks_physical_promotion() -> None:
    report = evaluate_factor11_gate(physical_observable=lambda item: item.value)

    assert report.physical_coupling_state is ClaimState.CLAIM_BLOCKED
    assert report.claim_allowed is False


def test_scale_sensitive_observable_creates_hypothesis_not_evidence() -> None:
    report = evaluate_factor11_gate(physical_observable=lambda item: item.common_scale)

    assert report.physical_coupling_state is ClaimState.HYPOTHESIS
    assert report.claim_allowed is False
    assert "falsifier" in report.next_gate


def test_wrong_scaled_presentation_is_a_contradiction() -> None:
    report = evaluate_factor11_gate(scaled=FractionPresentation(14, 6))

    assert report.same_rational_value is True
    assert report.recovered_common_scale == 2
    assert report.mathematical_state is ClaimState.CONTRADICTION
    assert report.claim_allowed is False


def test_validator_cli_runs_without_pythonpath() -> None:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, "tools/validate_discrete_ontology_claim.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    report = json.loads(completed.stdout)

    assert report["status"] == "PASS"
    assert report["checks_total"] == 15
    assert report["claim_allowed"] is False
    assert report["state"] == "TOKEN_VAZIO"
