#!/usr/bin/env python3
"""Synthetic, finite-domain assurance gate. No cosmology or private corpus data.
SPDX-License-Identifier: MIT
"""
import argparse
import hashlib
import itertools
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

DOMAIN = (0, 1)
KNOWN = "Known"
UNKNOWN = ("Unknown",)
ABSENT = ("Absent",)
NULL = ("Null",)
INVALID = ("Invalid",)


def known(x):
    return (KNOWN, x)


def concretize(value, domain=DOMAIN):
    if value == UNKNOWN:
        return tuple(domain)
    if len(value) == 2 and value[0] == KNOWN and value[1] in domain:
        return (value[1],)
    return None


def lift(mapping, value, domain=DOMAIN):
    possibilities = concretize(value, domain)
    if possibilities is None:
        return ("BLOCKED_TYPED_POLICY",)
    if not domain or any(x not in mapping for x in domain):
        return ("BLOCKED_DOMAIN",)
    outputs = set(mapping[x] for x in possibilities)
    if len(outputs) == 1:
        return known(next(iter(outputs)))
    return UNKNOWN


def merge(left, right, same_variable, domain=DOMAIN):
    if not same_variable:
        return ("BLOCKED_CONTEXT",)
    a, b = concretize(left, domain), concretize(right, domain)
    if a is None or b is None:
        return ("BLOCKED_TYPED_POLICY",)
    overlap = set(a) & set(b)
    if not overlap:
        return ("Conflict",)
    return known(next(iter(overlap))) if len(overlap) == 1 else UNKNOWN


class Assurance(unittest.TestCase):
    def test_tags_distinct(self):
        self.assertEqual(len({known(0), UNKNOWN, ABSENT, NULL, INVALID}), 5)

    def test_constant_unknown_can_be_known(self):
        self.assertEqual(lift({0: 0, 1: 0}, UNKNOWN), known(0))

    def test_identity_unknown_remains_unknown(self):
        self.assertEqual(lift({0: 0, 1: 1}, UNKNOWN), UNKNOWN)

    def test_known_zero_is_not_missing(self):
        self.assertEqual(lift({0: 0, 1: 1}, known(0)), known(0))

    def test_all_binary_maps_are_sound(self):
        for outputs in itertools.product(DOMAIN, repeat=2):
            mapping = dict(zip(DOMAIN, outputs))
            for value in (known(0), known(1), UNKNOWN):
                result = lift(mapping, value)
                possible = {mapping[x] for x in concretize(value)}
                if result[0] == KNOWN:
                    self.assertEqual(possible, {result[1]})
                else:
                    self.assertEqual(result, UNKNOWN)
                    self.assertGreater(len(possible), 1)

    def test_refinement_never_contradicts_known(self):
        for outputs in itertools.product(DOMAIN, repeat=2):
            mapping = dict(zip(DOMAIN, outputs))
            broad = lift(mapping, UNKNOWN)
            for x in DOMAIN:
                precise = lift(mapping, known(x))
                if broad[0] == KNOWN:
                    self.assertEqual(broad, precise)

    def test_conflicting_known_values(self):
        self.assertEqual(merge(known(0), known(1), True), ("Conflict",))

    def test_unknown_meets_known(self):
        self.assertEqual(merge(UNKNOWN, known(1), True), known(1))

    def test_merge_requires_shared_variable_context(self):
        self.assertEqual(merge(known(0), known(1), False), ("BLOCKED_CONTEXT",))

    def test_null_requires_policy(self):
        self.assertEqual(lift({0: 0, 1: 0}, NULL), ("BLOCKED_TYPED_POLICY",))

    def test_absent_requires_policy(self):
        self.assertEqual(lift({0: 0, 1: 0}, ABSENT), ("BLOCKED_TYPED_POLICY",))

    def test_invalid_requires_policy(self):
        self.assertEqual(lift({0: 0, 1: 0}, INVALID), ("BLOCKED_TYPED_POLICY",))

    def test_partial_function_blocked(self):
        self.assertEqual(lift({1: 1}, UNKNOWN), ("BLOCKED_DOMAIN",))


def main():
    parser = argparse.ArgumentParser(description="RLL typed-unknown synthetic assurance")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Assurance)
    result = unittest.TestResult()
    suite.run(result)
    source = Path(__file__).read_bytes()
    record = {
        "schema": "rll.rafaelos400.typed_unknown.assurance_receipt.v1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "finite-domain synthetic T={0,1}, standard-library, local Python",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "tests_executed": result.testsRun,
        "tests_passed": result.testsRun - len(result.failures) - len(result.errors),
        "tests_failed": len(result.failures) + len(result.errors),
        "status": "PASS_SCOPED_LOCAL_SYNTHETIC" if result.wasSuccessful() else "FAIL_SCOPED",
        "evidence_state": "VERIFIED_LIMITED" if result.wasSuccessful() else "CONTRADICTION",
        "assurance_scope": "implementation behavior of this finite synthetic fixture only",
        "source_message_fidelity": "NOT_RUN",
        "all_400_formulas_proved": False,
        "cosmology_validated": False,
        "independent_review": "NOT_RUN",
        "ci_status": "NOT_RUN",
        "claim_allowed": False,
        "limitations": ["not a formal proof assistant", "does not access 400 private formulas", "no real observational data", "no claim of new mathematics"],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record, sort_keys=True, ensure_ascii=False))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
