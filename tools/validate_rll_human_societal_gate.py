#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/governance/RLL_HUMAN_SOCIETAL_SCIENCE_GATE_V1.json"
DOC = ROOT / "docs/governance/RLL_HUMAN_SOCIETAL_SCIENCE_GATE_V1.md"


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def main():
    p = json.loads(POLICY.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    require(p["claim_allowed"] is False, "policy must not self-promote")
    inv = set(p["invariants"])
    for item in (
        "MATHEMATICAL_MODEL != PHYSICAL_VALIDATION",
        "PHYSICAL_HYPOTHESIS != CLINICAL_AUTHORITY",
        "COSMOLOGICAL_MODEL != HUMAN_WORTH_MODEL",
        "SCIENTIFIC_NOVELTY != SOCIAL_PERMISSION",
        "CULTURAL_ANALOGY != EMPIRICAL_PROOF",
        "TOKEN_VAZIO != PASS",
        "UNKNOWN_RISK != SAFE",
        "FIT_QUALITY != CAUSAL_TRUTH",
    ):
        require(item in inv, f"invariant missing: {item}")

    health = p["hard_boundaries"]["health_or_medical_use"]
    require(health["rll_model_alone_may_authorize"] is False, "RLL model allowed to self-authorize health use")
    require(health["independent_domain_review_required"] is True, "health domain review removed")

    children = p["hard_boundaries"]["children_or_education"]
    require(children["exclusive_algorithmic_high_impact_decision_allowed"] is False, "exclusive algorithmic child decision enabled")
    require(children["child_best_interest_required_when_applicable"] is True, "child best-interest gate removed")

    culture = p["hard_boundaries"]["culture_belief_identity"]
    require(culture["personal_worth_ranking_allowed"] is False, "personal worth ranking enabled")
    require(culture["metaphor_must_be_separated_from_empirical_claim"] is True, "metaphor/evidence boundary removed")

    policy = p["hard_boundaries"]["public_policy_or_essential_resources"]
    require(policy["single_model_output_may_be_final_authority"] is False, "single model output allowed as final authority")
    require(policy["plural_review_required_when_high_impact"] is True, "plural review removed")
    require(policy["appeal_or_contestation_path_required"] is True, "appeal path removed")

    anti = p["anti_regression"]
    require(anti["latest_wins"] is False, "latest-wins regression")
    require(anti["scientific_claim_may_not_be_upgraded_without_stronger_evidence"] is True, "scientific evidence ratchet weakened")
    require(anti["human_protection_may_not_be_weakened_by_performance_gain"] is True, "performance may override human protection")

    for phrase in (
        "MATHEMATICAL_MODEL != PHYSICAL_VALIDATION",
        "PHYSICAL_HYPOTHESIS != CLINICAL_AUTHORITY",
        "BEST_INTEREST_OF_CHILD = HARD_CONSTRAINT",
        "CULTURAL_ANALOGY != EMPIRICAL_PROOF",
        "MAPA_GOVERNANCE != RAFGITTOOLS_TRANSPORT != RLL_SCIENTIFIC_TRUTH",
    ):
        require(phrase in doc, f"documentation invariant missing: {phrase}")

    print("PASS: RLL human/societal/science gate v1")


if __name__ == "__main__":
    main()
