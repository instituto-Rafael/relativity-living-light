#!/usr/bin/env python3
"""BLAKE3 ↔ RLL falsifiability gate.

This module does not claim a causal bridge between BLAKE3 and RLL.
It records a small set of canonical BLAKE3 structural facts observed in the
upstream specification and in rafaelmeloreisnovo/BLAKE3, then applies explicit
falsifiers to the current RLL 42-cycle recurrence claim.

PV: SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
Unknown/unbound relations remain TOKEN_VAZIO.
"""
from __future__ import annotations

import json
import math
from typing import Any

BLAKE3_SOURCE = {
    "fork": "rafaelmeloreisnovo/BLAKE3",
    "impl_h_blob": "facd5997435736a9f15491f490805ceff6c0453f",
    "portable_c_blob": "062dd1b47fb6424f4d3db4c6edd2f90efcb92973",
    "blake3_c_blob": "00f91f444922df7c8e7b5ff69343852cbbf4c613",
    "lib_rs_blob": "6f652071de0ad06626c427e40354e7ee4872be76",
}

RLL_SOURCE = {
    "iml_pipeline_blob": "9b71f4deacb431c25a8ca0b88a7ef5c0da208f93",
    "mathraf_blob": "6faeae4f24eb80b98b974cdf9c7e908440e35192",
    "master_doc_blob": "269b44417d9bb289388b0e766f9447835b99a59b",
}

BLAKE3 = {
    "tree_arity": 2,
    "user_facing_modes": 3,
    "g_parallel_width": 4,
    "rounds": 7,
    "internal_flags": 7,
    "g_calls_per_round": 8,
    "cv_words": 8,
    "message_words": 16,
    "block_bytes": 64,
    "chunk_bytes": 1024,
    "rotation_constants": [16, 12, 8, 7],
}


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def complete_binary_tree_depth(chunks: int) -> int:
    """Depth for a complete BLAKE3 tree with a power-of-two chunk count."""
    if not is_power_of_two(chunks):
        raise ValueError("chunks must be a positive power of two")
    return chunks.bit_length() - 1


def rll_float_recurrence(steps: int = 84, x0: float = 0.314159) -> list[float]:
    """Reproduce the recurrence used by tools/iml/iml_pipeline.py."""
    x = x0
    seq: list[float] = []
    for _ in range(steps):
        x = (math.sqrt(3.0) / 2.0) * x - math.pi * math.sin(math.radians(279.0))
        seq.append(round(x % 1.0, 12))
    return seq


def count_signature_3_to_8() -> dict[str, dict[str, Any]]:
    """Test only semantically named counts; do not fill gaps by numerology."""
    return {
        "3": {
            "state": "PASS_CANONICAL",
            "binding": "three domain-separated user-facing modes",
        },
        "4": {
            "state": "PASS_CANONICAL",
            "binding": "four G operations in each parallel column/diagonal phase",
        },
        "5": {
            "state": "TOKEN_VAZIO_NO_CANONICAL_BINDING",
            "binding": None,
        },
        "6": {
            "state": "TOKEN_VAZIO_NO_CANONICAL_BINDING",
            "binding": None,
        },
        "7": {
            "state": "PASS_CANONICAL",
            "binding": "seven compression rounds; seven internal flag bits",
        },
        "8": {
            "state": "PASS_CANONICAL",
            "binding": "eight G calls per round; eight chaining-value words",
        },
    }


def build_report() -> dict[str, Any]:
    seq = rll_float_recurrence()
    depth_examples = [
        {
            "chunks": 2**depth,
            "bytes": (2**depth) * BLAKE3["chunk_bytes"],
            "depth": depth,
        }
        for depth in range(3, 9)
    ]
    cycle42 = seq[:42] == seq[42:84]

    return {
        "schema": "rll.blake3_falsifiability.v1",
        "source": {"blake3": BLAKE3_SOURCE, "rll": RLL_SOURCE},
        "invariants": {
            "source_artifact_execution_evidence_claim_distinct": True,
            "token_vazio_is_not_zero": True,
        },
        "blake3_observed_structure": {
            **BLAKE3,
            "rotation_sum": sum(BLAKE3["rotation_constants"]),
            "g_calls_across_7_rounds": BLAKE3["rounds"] * BLAKE3["g_calls_per_round"],
        },
        "falsifiability": {
            "tree_branching_factor_3_to_8": {
                "state": "FAIL_IF_INTERPRETED_AS_CHILD_ARITY",
                "observed_tree_arity": BLAKE3["tree_arity"],
                "falsifier": "one canonical parent node with more or fewer than two child CVs",
            },
            "input_dependent_depth_3_to_8": {
                "state": "PASS_CONDITIONAL",
                "examples": depth_examples,
                "boundary": "depth is not child arity",
            },
            "count_signatures_3_to_8": count_signature_3_to_8(),
            "intrinsic_42_in_blake3_core": {
                "state": "TOKEN_VAZIO_NO_CANONICAL_BINDING",
                "notes": [
                    "no 42-specific BLAKE3 core invariant is asserted by this gate",
                    "rotation constants sum to 43, not 42",
                    "7 rounds x 8 G calls = 56, not 42",
                ],
                "promotion_gate": "provide a canonical BLAKE3 definition or derivation that binds 42",
            },
            "rll_real_recurrence_period_42": {
                "state": "FAIL_FALSIFIED",
                "cycle_42_verified": cycle42,
                "step_42_mod1": seq[41],
                "step_43_mod1": seq[42],
                "falsifier": "seq[0:42] != seq[42:84]",
            },
            "bitomega_period_42_attributed_to_blake3_rmr": {
                "state": "TOKEN_VAZIO_PROVENANCE_CONFLICT",
                "reason": (
                    "RLL master documentation asserts the link, while the examined "
                    "BLAKE3 core sources do not define BitOmega; a raw generating "
                    "program/log plus exact source commit is required."
                ),
                "claim_allowed": False,
            },
        },
        "claim_allowed": False,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
