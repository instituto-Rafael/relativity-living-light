from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load_module(
    "validate_rll_noaa_trinity_governance",
    ROOT / "scripts" / "validate_rll_noaa_trinity_governance.py",
)


class NoaaTrinityGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "data/contracts/rll_noaa_trinity_633.v1.json").read_text(encoding="utf-8"))
        self.governance = json.loads((ROOT / "data/governance/rll_noaa_trinity633_data_governance.v1.json").read_text(encoding="utf-8"))
        self.registry = json.loads((ROOT / "data/climate/rll_climate_source_registry.v1.json").read_text(encoding="utf-8"))
        self.workflow = (ROOT / ".github/workflows/rll-real-data-orchestrator.yml").read_text(encoding="utf-8")

    def test_repository_contract_passes_zero_trust_privacy_gate(self):
        receipt = validator.validate(self.contract, self.governance, self.registry, self.workflow)
        self.assertEqual(receipt["status"], "PASS", receipt["errors"])
        self.assertFalse(receipt["claim_allowed"])
        self.assertFalse(receipt["compliance_claim"])

    def test_query_parameter_is_fail_closed(self):
        registry = json.loads(json.dumps(self.registry))
        source = next(item for item in registry["sources"] if item["id"] == "noaa_swpc_kp")
        source["sample_url"] += "?user=123"
        receipt = validator.validate(self.contract, self.governance, registry, self.workflow)
        self.assertEqual(receipt["status"], "FAIL")
        self.assertTrue(any("query parameters forbidden" in item for item in receipt["errors"]))

    def test_write_permission_is_fail_closed(self):
        workflow = self.workflow.replace("permissions:\n  contents: read", "permissions:\n  contents: write", 1)
        receipt = validator.validate(self.contract, self.governance, self.registry, workflow)
        self.assertEqual(receipt["status"], "FAIL")
        self.assertTrue(any("write permissions" in item for item in receipt["errors"]))

    def test_non_public_source_is_fail_closed(self):
        registry = json.loads(json.dumps(self.registry))
        source = next(item for item in registry["sources"] if item["id"] == "noaa_swpc_f107")
        source["access"] = "PUBLIC_GET_TEMPLATE_REQUIRES_LOCATION"
        receipt = validator.validate(self.contract, self.governance, registry, self.workflow)
        self.assertEqual(receipt["status"], "FAIL")
        self.assertTrue(any("PUBLIC_GET" in item for item in receipt["errors"]))


if __name__ == "__main__":
    unittest.main()
