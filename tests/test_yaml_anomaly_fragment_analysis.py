from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import yaml_anomaly_fragment_analysis as mod


def finding(code: str, path: str = ".github/workflows/example.yml") -> dict:
    return {
        "severity": "HIGH",
        "code": code,
        "path": path,
        "job": "job",
        "step": "step",
        "message": f"message for {code}",
    }


class YamlAnomalyFragmentAnalysisTests(unittest.TestCase):
    def source(self) -> dict:
        return {
            "schema": "rll.yaml_deep_audit.v1",
            "commit_sha": "a" * 40,
            "decision": "REVIEW_REQUIRED",
            "residuals": [
                finding("YAML_PARSE_FAILURE"),
                finding("CHECKOUT_CREDENTIALS_PERSIST"),
                finding("CONCURRENCY_MISSING"),
                finding(
                    "VERSIONED_INVENTORY_STALE",
                    "data/results/repo_inventory_summary.json",
                ),
                finding("SCIENTIFIC_RESULT_OR_PARAMETER_EMBEDDED"),
                finding("CRLF_LINE_ENDINGS"),
                finding("SOMETHING_NEW"),
            ],
        }

    def test_every_finding_is_routed_to_one_lens(self) -> None:
        routed = []
        for lens in mod.LENSES:
            payload = mod.build_fragment_payload(self.source(), lens)
            routed.extend(item["code"] for item in payload["fragments"])
        self.assertCountEqual(
            routed,
            [item["code"] for item in self.source()["residuals"]],
        )

    def test_zero_job_compatible_signature_is_not_promoted_to_cause(self) -> None:
        payload = mod.build_fragment_payload(self.source(), "startup_preflight")
        self.assertEqual(1, payload["zero_job_compatible_observation_count"])
        self.assertEqual(
            "ZERO_JOB_COMPATIBLE_STATIC_SIGNATURE",
            payload["explanatory_status"],
        )
        self.assertFalse(payload["causal_claim_allowed"])
        self.assertFalse(payload["claim_allowed"])

    def test_fragment_id_is_stable(self) -> None:
        item = finding("YAML_PARSE_FAILURE")
        self.assertEqual(mod.fragment_id(item), mod.fragment_id(dict(item)))

    def test_aggregate_requires_all_lenses_and_keeps_causality_empty(self) -> None:
        payloads = [
            mod.build_fragment_payload(self.source(), lens)
            for lens in mod.LENSES
        ]
        aggregate = mod.aggregate_payload(payloads)
        self.assertEqual([], aggregate["missing_lenses"])
        self.assertEqual(
            "TOKEN_VAZIO_CAUSAL_LINK_NOT_ESTABLISHED",
            aggregate["causal_conclusion"],
        )
        self.assertEqual(1, aggregate["zero_job_compatible_fragment_count"])
        self.assertFalse(aggregate["causal_claim_allowed"])

    def test_files_are_emitted_for_fragment_and_aggregate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "deep_yaml_audit.json"
            source.write_text(json.dumps(self.source()), encoding="utf-8")
            fragments = root / "fragments"
            for lens in mod.LENSES:
                mod.write_fragment(source, lens, fragments)
            out = root / "aggregate"
            json_path, aggregate = mod.aggregate_dir(fragments, out)
            self.assertTrue(json_path.exists())
            self.assertTrue(
                (out / "YAML_ANOMALY_EXPLANATORY_AGGREGATE.md").exists()
            )
            self.assertEqual([], aggregate["missing_lenses"])


if __name__ == "__main__":
    unittest.main()
