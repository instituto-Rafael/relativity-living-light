import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rll_governance_audit", ROOT / "scripts" / "rll_governance_audit.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class GovernanceAuditTests(unittest.TestCase):
    def test_repository_contract_passes(self):
        audit, receipt, _ = MODULE.run(write_report=False)
        self.assertEqual([], audit.violations)
        self.assertEqual("PASS", receipt["status"])
        self.assertFalse(receipt["certification_claim"])
        self.assertFalse(receipt["conformity_claim"])

    def test_biomedical_contract_is_default_deny(self):
        path = ROOT / "governance" / "modules" / "life-sciences-ecosystem-engineering.v1.json"
        module = MODULE.load_json(path)
        data = module["data_governance"]
        self.assertEqual("PROHIBITED_BY_DEFAULT", data["personal_data"])
        self.assertEqual("PROHIBITED_BY_DEFAULT", data["sensitive_health_genetic_biometric_data"])
        self.assertEqual("ETHICS_REVIEW_REQUIRED", data["human_participants"])
        self.assertFalse(module["claim_allowed"])

    def test_claim_promotion_requires_receipt_and_tests(self):
        profile = MODULE.load_json(ROOT / "governance" / "rll-governance-profile.v1.json")
        module = MODULE.load_json(ROOT / "governance" / "modules" / "climate-multiphysics.v1.json")
        module["claim_allowed"] = True
        module["evidence"]["receipts"] = []
        audit = MODULE.Audit()
        MODULE.validate_module(module, ROOT / "governance" / "modules" / "test.json", profile, audit)
        self.assertTrue(any(f.code == "CLAIM_EVIDENCE" for f in audit.violations))

    def test_governance_workflow_uses_immutable_action_reference(self):
        workflow = (ROOT / ".github" / "workflows" / "rll-governance-quality-gate.yml").read_text(encoding="utf-8")
        refs = MODULE.USES_RE.findall(workflow)
        external = [ref for ref in refs if not ref.startswith("./")]
        self.assertTrue(external)
        for use in external:
            self.assertIn("@", use)
            self.assertRegex(use.rsplit("@", 1)[1], r"^[0-9a-f]{40}$")

    def test_duplicate_json_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaises(MODULE.DuplicateKeyError):
                MODULE.load_json(path)

    def test_receipt_is_deterministic_without_time_or_revision_environment(self):
        _, first, _ = MODULE.run(write_report=False)
        _, second, _ = MODULE.run(write_report=False)
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])


if __name__ == "__main__":
    unittest.main()
