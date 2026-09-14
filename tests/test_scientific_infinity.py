from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from rll.scientific_infinity import (
    CycleDecision,
    EvolutionObservation,
    GuardPolicy,
    InfinityClass,
    assess_evolution,
    distinct_infinity_classes,
    evolution_score,
    stable_digest,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/scientific_infinity_cycle.schema.json").read_text())
EXAMPLE = json.loads((ROOT / "schemas/examples/scientific_infinity_cycle.example.json").read_text())


def observation(**overrides):
    data = {
        "iteration": 1,
        "state_digest": "state-1",
        "novelty": 0.4,
        "evidence_strength": 0.9,
        "duplication_ratio": 0.1,
        "unresolved_contradictions": 0,
        "elapsed_seconds": 1.0,
        "objective_value": 1.0,
    }
    data.update(overrides)
    return EvolutionObservation(**data)


def schema_errors(instance):
    return list(Draft202012Validator(SCHEMA).iter_errors(instance))


def test_infinity_classes_remain_distinct_and_ordered():
    result = distinct_infinity_classes(
        [
            InfinityClass.MATHEMATICAL,
            InfinityClass.PHYSICAL,
            InfinityClass.MATHEMATICAL,
            "TOKEN_VAZIO",
        ]
    )
    assert result == ("infinity_math", "infinity_physical", "TOKEN_VAZIO")


def test_stable_digest_is_key_order_independent():
    assert stable_digest({"a": 1, "b": 2}) == stable_digest({"b": 2, "a": 1})


def test_evolution_score_penalizes_duplication_and_contradiction():
    clean = evolution_score(0.8, 0.9, 0.95, 0.0, 0)
    noisy = evolution_score(0.8, 0.9, 0.95, 0.8, 2)
    assert 0.0 <= noisy < clean <= 1.0


def test_repeated_digest_is_cycle_not_evolution():
    prior = observation(iteration=0, state_digest="repeat")
    current = observation(iteration=1, state_digest="repeat")
    result = assess_evolution([prior], current, GuardPolicy())
    assert result.decision is CycleDecision.CYCLE_DETECTED
    assert result.claim_allowed is False


def test_weak_evidence_becomes_token_vazio():
    result = assess_evolution(
        [],
        observation(evidence_strength=0.1),
        GuardPolicy(evidence_floor=0.5),
    )
    assert result.decision is CycleDecision.TOKEN_VAZIO


def test_convergence_requires_stable_objective_and_low_novelty():
    prior = observation(iteration=0, state_digest="prior", objective_value=1.0)
    current = observation(
        iteration=1,
        state_digest="current",
        novelty=1.0e-5,
        objective_value=1.0 + 1.0e-8,
    )
    result = assess_evolution(
        [prior],
        current,
        GuardPolicy(convergence_tolerance=1.0e-6, novelty_floor=1.0e-3),
    )
    assert result.decision is CycleDecision.CONVERGED


def test_iteration_budget_is_finite():
    result = assess_evolution(
        [],
        observation(iteration=10),
        GuardPolicy(max_iterations=10),
    )
    assert result.decision is CycleDecision.BUDGET_EXHAUSTED


def test_invalid_unit_interval_is_rejected():
    with pytest.raises(ValueError):
        observation(novelty=1.1)


def test_schema_example_is_valid_and_claim_bounded():
    assert not schema_errors(EXAMPLE)
    assert EXAMPLE["claim_allowed"] is False
    assert EXAMPLE["execution_scope"]["mode"] == "finite_budgeted"


def test_schema_rejects_claim_promotion():
    changed = copy.deepcopy(EXAMPLE)
    changed["claim_allowed"] = True
    assert schema_errors(changed)


def test_schema_rejects_unbounded_execution_mode():
    changed = copy.deepcopy(EXAMPLE)
    changed["execution_scope"]["mode"] = "infinite"
    assert schema_errors(changed)


def test_schema_rejects_unknown_infinity_class():
    changed = copy.deepcopy(EXAMPLE)
    changed["infinity_classes"].append("infinity_magic")
    assert schema_errors(changed)
