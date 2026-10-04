from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools import rll_canonical_family_pipeline_v1 as pipeline


class RLLCanonicalFamilyPipelineV1Tests(unittest.TestCase):
    def test_cross_family_contract_connects_all_declared_layers(self) -> None:
        cross = pipeline.cross_family_receipt()
        self.assertEqual(cross["set_void"]["numeric_zero_vs_empty_set"], "DISTINCT_OR_NOT_COMPARABLE")
        self.assertEqual(cross["number_prime_base"]["repunit6"], 111111)
        self.assertEqual(tuple(cross["number_prime_base"]["repunit6_prime_factors"]), (3, 7, 11, 13, 37))
        self.assertTrue(cross["graphs"]["crt21_roundtrip"])
        self.assertTrue(cross["graphs"]["crt42_roundtrip"])
        self.assertTrue(cross["abscissa"]["zero_axis_is_occupied"])
        self.assertTrue(cross["graph_fluid"]["junction_balance_zero"])
        self.assertTrue(cross["graph_fluid"]["continuity_zero"])

    def test_physical_boundaries_are_expected_fail_closed_states(self) -> None:
        cross = pipeline.cross_family_receipt()
        fluid = cross["physical_boundaries"]["fluid_gate"]
        self.assertEqual(fluid["state"], "TOKEN_VAZIO_FLUID_BINDING")
        self.assertFalse(fluid["claim_allowed"])
        self.assertEqual(cross["physical_boundaries"]["cosmology_binding"], "TOKEN_VAZIO_COSMOLOGY_BINDING")

    def test_all_canonical_gates_pass_without_promoting_claim(self) -> None:
        source = pipeline.source_receipt()
        census_receipt = pipeline.json_safe(pipeline.census.receipt())
        family_receipt = pipeline.json_safe(pipeline.bridge.family_manifest())
        prime_receipt = pipeline.json_safe(pipeline.abscissa.base_prime_receipt())
        gates = pipeline.evaluate_gates(source, census_receipt, family_receipt, prime_receipt, pipeline.cross_family_receipt())
        self.assertEqual(len(gates), 12)
        self.assertEqual([g["state"] for g in gates], ["PASS"] * 12)
        self.assertFalse(census_receipt["claim_allowed"])
        self.assertFalse(family_receipt["claim_allowed"])
        self.assertFalse(prime_receipt["claim_allowed"])

    def test_pipeline_materializes_complete_receipt_chain_with_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            final = pipeline.build_pipeline(out, head_sha="abc123", run_id="unit-test")
            self.assertEqual(final["pipeline_state"], "PASS_FAIL_CLOSED")
            self.assertFalse(final["claim_allowed"])
            self.assertEqual(final["head_sha"], "abc123")
            self.assertEqual(final["run_id"], "unit-test")
            expected = set(pipeline.RECEIPT_FILENAMES) | {"07_final_receipt.json", "R3.md"}
            self.assertEqual({p.name for p in out.iterdir()}, expected)
            for name, meta in final["child_receipts"].items():
                payload = (out / name).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), meta["sha256"])
                self.assertEqual(len(payload), meta["bytes"])
                self.assertEqual(len(meta["sha256"]), 64)
            reloaded = json.loads((out / "07_final_receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(reloaded["pipeline_state"], "PASS_FAIL_CLOSED")
            self.assertEqual(len(reloaded["gates"]), 12)
            self.assertIn("No implementation gap", reloaded["r3"]["F_next"])

    def test_source_custody_is_complete(self) -> None:
        receipt = pipeline.source_receipt()
        self.assertEqual(receipt["missing"], [])
        self.assertEqual(len(receipt["sources"]), len(pipeline.SOURCE_PATHS))
        for row in receipt["sources"]:
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(row["bytes"], 0)


if __name__ == "__main__":
    unittest.main()
