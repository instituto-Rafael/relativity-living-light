from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "blake3_rll_falsifiability.py"


def load_target():
    spec = importlib.util.spec_from_file_location("blake3_rll_falsifiability", TARGET)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blake3_structural_counts_are_typed_not_conflated():
    mod = load_target()
    report = mod.build_report()
    b3 = report["blake3_observed_structure"]
    assert b3["tree_arity"] == 2
    assert b3["user_facing_modes"] == 3
    assert b3["g_parallel_width"] == 4
    assert b3["rounds"] == 7
    assert b3["internal_flags"] == 7
    assert b3["g_calls_per_round"] == 8
    assert b3["cv_words"] == 8
    assert b3["rotation_constants"] == [16, 12, 8, 7]
    assert b3["rotation_sum"] == 43
    assert b3["g_calls_across_7_rounds"] == 56


def test_counts_five_and_six_remain_token_vazio():
    mod = load_target()
    signatures = mod.build_report()["falsifiability"]["count_signatures_3_to_8"]
    assert signatures["3"]["state"] == "PASS_CANONICAL"
    assert signatures["4"]["state"] == "PASS_CANONICAL"
    assert signatures["5"]["state"] == "TOKEN_VAZIO_NO_CANONICAL_BINDING"
    assert signatures["6"]["state"] == "TOKEN_VAZIO_NO_CANONICAL_BINDING"
    assert signatures["7"]["state"] == "PASS_CANONICAL"
    assert signatures["8"]["state"] == "PASS_CANONICAL"


def test_depth_three_through_eight_is_input_dependent_not_tree_arity():
    mod = load_target()
    branch = mod.build_report()["falsifiability"]
    assert branch["tree_branching_factor_3_to_8"]["observed_tree_arity"] == 2
    examples = branch["input_dependent_depth_3_to_8"]["examples"]
    assert [row["depth"] for row in examples] == [3, 4, 5, 6, 7, 8]
    assert [row["chunks"] for row in examples] == [8, 16, 32, 64, 128, 256]
    assert [row["bytes"] for row in examples] == [
        8192,
        16384,
        32768,
        65536,
        131072,
        262144,
    ]


def test_current_rll_float_recurrence_falsifies_period_42():
    mod = load_target()
    result = mod.build_report()["falsifiability"]["rll_real_recurrence_period_42"]
    assert result["state"] == "FAIL_FALSIFIED"
    assert result["cycle_42_verified"] is False
    assert result["step_42_mod1"] == 0.106130777368
    assert result["step_43_mod1"] == 0.113410671216


def test_bitomega_blake3_link_fails_closed_without_generating_evidence():
    mod = load_target()
    result = mod.build_report()["falsifiability"]["bitomega_period_42_attributed_to_blake3_rmr"]
    assert result["state"] == "TOKEN_VAZIO_PROVENANCE_CONFLICT"
    assert result["claim_allowed"] is False


def test_global_claim_gate_stays_closed():
    mod = load_target()
    assert mod.build_report()["claim_allowed"] is False
