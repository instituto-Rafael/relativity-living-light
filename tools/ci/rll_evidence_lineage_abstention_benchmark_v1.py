#!/usr/bin/env python3
"""Preregistered synthetic provenance/abstention experiment, no private corpus.
SPDX-License-Identifier: MIT. No network, dependencies, cosmology, or deployment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

LEVELS = (1, 2, 4, 8)
# Each fixed tuple is (case_id, ground_truth, source_rows).
# Each source row is (independent_origin, type, value, repeats_when_multiplier).
# These fixtures are authored synthetics, NOT observations or random samples.
TEMPLATES = (
    ("consensus_true", 1, (("a", "Known", 1, False), ("b", "Known", 1, False))),
    ("consensus_false", 0, (("a", "Known", 0, False), ("b", "Known", 0, False))),
    ("single_true", 1, (("a", "Known", 1, False),)),
    ("single_false", 0, (("a", "Known", 0, False),)),
    ("copied_wrong_true", 0, (("dup", "Known", 1, True), ("a", "Known", 0, False), ("b", "Known", 0, False))),
    ("copied_wrong_false", 1, (("dup", "Known", 0, True), ("a", "Known", 1, False), ("b", "Known", 1, False))),
    ("copied_right_true", 1, (("dup", "Known", 1, True), ("a", "Known", 0, False))),
    ("copied_right_false", 0, (("dup", "Known", 0, True), ("a", "Known", 1, False))),
    ("wrong_consensus_true", 0, (("a", "Known", 1, False), ("b", "Known", 1, False))),
    ("wrong_consensus_false", 1, (("a", "Known", 0, False), ("b", "Known", 0, False))),
    ("good_with_unknown", 1, (("a", "Known", 1, False), ("b", "Known", 1, False), ("c", "Unknown", None, False))),
    ("conflicting_roots", 1, (("a", "Known", 1, False), ("b", "Known", 0, False))),
    ("null_only", None, (("a", "Null", None, False), ("b", "Absent", None, False))),
    ("unknown_only", None, (("a", "Unknown", None, True),)),
    ("empty", None, ()),
    ("one_root_copied", 1, (("dup", "Known", 1, True),)),
)


def fixture(template, multiplier):
    ident, truth, rows = template
    records = []
    for root, kind, value, duplicate in rows:
        for _ in range(multiplier if duplicate else 1):
            records.append((root, kind, value))
    return {"id": ident, "truth": truth, "multiplier": multiplier, "records": records}


def vote_records(case):
    votes = Counter(v for _, kind, v in case["records"] if kind == "Known" and v in (0, 1))
    if votes[0] == votes[1]:
        return None
    return int(votes[1] > votes[0])


def root_votes(case):
    roots = {}
    for root, kind, value in case["records"]:
        if kind == "Known" and value in (0, 1):
            roots.setdefault(root, set()).add(value)
    return roots


def dedup_vote(case):
    roots = root_votes(case)
    votes = Counter(next(iter(vals)) for vals in roots.values() if len(vals) == 1)
    if votes[0] == votes[1]:
        return None
    return int(votes[1] > votes[0])


def lineage_conflict_guard(case):
    roots = root_votes(case)
    if any(len(vals) != 1 for vals in roots.values()):
        return None
    unique = [next(iter(v)) for v in roots.values()]
    if len(unique) < 2 or len(set(unique)) != 1:
        return None
    return unique[0]


METHODS = {
    "record_majority": vote_records,
    "independent_root_majority": dedup_vote,
    "typed_lineage_conflict_guard": lineage_conflict_guard,
    "always_abstain": lambda case: None,
}


def evaluate(cases, method):
    observations = [(case, method(case)) for case in cases]
    answered = [(case, ans) for case, ans in observations if ans is not None]
    wrong = sum(ans != case["truth"] for case, ans in answered)
    correct = len(answered) - wrong
    unsafe = sum(
        (ans is not None) and
        (len(root_votes(case)) < 2 or any(len(x) != 1 for x in root_votes(case).values())
         or len({next(iter(x)) for x in root_votes(case).values() if len(x) == 1}) > 1)
        for case, ans in observations
    )
    return {
        "cases": len(cases), "answered": len(answered), "correct": correct,
        "wrong": wrong, "abstained": len(cases) - len(answered),
        "coverage": len(answered) / len(cases),
        "selective_risk": wrong / len(answered) if answered else None,
        "error_per_case": wrong / len(cases),
        "unsupported_answer_contract_violations": unsafe,
    }


def experiment():
    cases = [fixture(t, level) for level in LEVELS for t in TEMPLATES]
    rows = {name: evaluate(cases, f) for name, f in METHODS.items()}
    strata = {
        str(m): {name: evaluate([fixture(t, m) for t in TEMPLATES], f)
                 for name, f in METHODS.items()} for m in LEVELS
    }
    return cases, rows, strata


class ExperimentChecks(unittest.TestCase):
    def test_preregistered_fixture_count(self):
        cases, _, _ = experiment()
        self.assertEqual((len(TEMPLATES), len(cases)), (16, 64))

    def test_duplicates_do_not_change_guard_decision(self):
        for template in TEMPLATES:
            answers = [lineage_conflict_guard(fixture(template, m)) for m in LEVELS]
            self.assertEqual(answers, [answers[0]] * len(LEVELS))

    def test_copying_one_source_never_creates_independent_support(self):
        for m in LEVELS:
            self.assertIsNone(lineage_conflict_guard(fixture(TEMPLATES[-1], m)))

    def test_contradictory_origins_abstain(self):
        for name in ("copied_wrong_true", "copied_wrong_false", "conflicting_roots"):
            template = next(t for t in TEMPLATES if t[0] == name)
            self.assertTrue(all(lineage_conflict_guard(fixture(template, m)) is None for m in LEVELS))

    def test_two_wrong_independent_sources_can_still_fool_guard(self):
        a = fixture(next(t for t in TEMPLATES if t[0] == "wrong_consensus_true"), 1)
        self.assertEqual((a["truth"], lineage_conflict_guard(a)), (0, 1))

    def test_tagged_missing_values_not_turned_into_votes(self):
        for name in ("null_only", "unknown_only", "empty"):
            case = fixture(next(t for t in TEMPLATES if t[0] == name), 8)
            self.assertTrue(all(f(case) is None for f in METHODS.values()))

    def test_ablation_guard_no_more_wrong_than_record_majority_on_fixture(self):
        _, results, _ = experiment()
        self.assertLessEqual(results["typed_lineage_conflict_guard"]["wrong"],
                             results["record_majority"]["wrong"])

    def test_unconditional_abstain_cannot_claim_accuracy(self):
        _, result, _ = experiment()
        self.assertEqual(result["always_abstain"]["selective_risk"], None)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExperimentChecks)
    result = unittest.TestResult()
    suite.run(result)
    cases, rows, strata = experiment()
    content = Path(__file__).read_bytes()
    record = {
        "schema": "rll.evidence_lineage_abstention.synthetic_experiment.v1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(content).hexdigest(),
        "fixture_design": "hand-authored deterministic 16 templates x four duplication multipliers",
        "hypotheses": {
            "H1": "lineage guard invariant to replicated document copies sharing root ID",
            "H2": "lineage guard fewer wrong assertions than record-majority on THESE synthetics",
            "H0": "no reduction in wrong assertions; unobserved for independent datasets",
            "H3": "conflicting independent sources cause abstention",
        },
        "ground_truth_type": "AUTHOR_SYNTHETIC_NOT_OBSERVED",
        "methods": list(METHODS),
        "metrics": rows, "duplication_strata": strata,
        "test_methods": result.testsRun, "test_failures": len(result.failures) + len(result.errors),
        "status": "PASS_SCOPED_SYNTHETIC" if result.wasSuccessful() else "FAIL_SCOPED",
        "safety_note": "At least one deliberately wrong independent consensus must remain a false positive.",
        "limitations": [
            "Not random, blinded, independent or representative samples",
            "64 cases include repeated copies of only 16 templates; no confidence intervals",
            "No natural language model, LLM benchmark, real evidence or cosmology used",
            "Root IDs assumed correct; dependence discovery is NOT implemented",
            "No casewise proofs of 400 equations, no originality or generalization claim",
        ],
        "ci_status": "NOT_RUN", "independent_replication": "NOT_RUN",
        "claim_allowed": False,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
