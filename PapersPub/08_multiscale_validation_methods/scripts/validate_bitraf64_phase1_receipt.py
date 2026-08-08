#!/usr/bin/env python3
"""Validate the cross-repository BITRAF64 Phase-1 implementation receipt fail-closed."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "results" / "bitraf64_phase1_implementation_receipt_20260808.json"


def main() -> int:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    findings = data["source_implementation_findings"]
    hotfix = data["hotfix"]
    exact = data["corrected_exact_values"]

    assert data["claim_allowed"] is False
    assert data["production_ready"] is False
    assert findings["manifest_v2_entry_bytes"] == 200
    assert findings["manifest_v2_reserved_bits"] == 32
    assert findings["declared_diagnostic_signature_bits"] == 33
    assert findings["declared_packed_metadata_bits"] == 48
    assert findings["silent_width_mismatch_present"] is True
    assert findings["phase1_ecc_is_full_33x33_matrix_implementation"] is False
    assert findings["phase1_single_error_correction_proven"] is False
    assert findings["phase1_projected_layer_is_real_package_dag_depth"] is False
    assert hotfix["manifest_v2_abi_changed"] is False
    assert hotfix["sidecar_added"] is True
    assert hotfix["claim_gate"] == "FAIL_CLOSED"
    assert exact["gcd_6000_2057"] == 1
    assert exact["gcd_42_60"] == 6
    assert abs(exact["r_corr_formula_value_approx"] - 0.1839415) < 1e-7
    assert abs(exact["redundancy_53_bits_per_1024_bytes"] - 0.0517578125) < 1e-15
    assert len(data["token_vazio"]) >= 8

    print("BITRAF64_PHASE1_RECEIPT_PASS")
    print("claim_allowed=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
