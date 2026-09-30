import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("validate_scan_poc_coherence.py")
SPEC = importlib.util.spec_from_file_location("scan_poc", MODULE)
scan_poc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(scan_poc)


class ScanPocCoherenceTests(unittest.TestCase):
    def write(self, payload):
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(payload, handle)
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def valid(self):
        return {"schema": scan_poc.SCHEMA, "append_only": True, "claim_allowed": False, "records": [{
            "id": "RLL-SCAN-POC-TEST-001", "kind": "POC", "recorded_at": "2026-08-21T00:00:00Z",
            "scope": "bounded test", "epistemic_state": "EXECUTED", "claim_allowed": False,
            "source": {"repository": "instituto-Rafael/relativity-living-light", "git_sha": "0fe2fb410b17ba357ef0c251abac68b1b2af8288"},
            "evidence": [{"kind": "test", "reference": "unit"}],
            "poc": {"status": "EXECUTED", "command": "python3 -m unittest", "environment": "CI", "exit_code": 0, "output_sha256": "a" * 64},
            "next_gate": "review receipt"
        }]}

    def test_accepts_complete_executed_poc(self):
        self.assertEqual(scan_poc.validate_registry(self.write(self.valid()))["decision"], "PASS")

    def test_rejects_nonexecuted_poc_without_token_vazio(self):
        payload = self.valid()
        payload["records"][0]["poc"] = {"status": "NOT_RUN"}
        with self.assertRaises(ValueError):
            scan_poc.validate_registry(self.write(payload))

    def test_rejects_claim_promotion(self):
        payload = self.valid()
        payload["records"][0]["claim_allowed"] = True
        with self.assertRaises(ValueError):
            scan_poc.validate_registry(self.write(payload))


if __name__ == "__main__":
    unittest.main()
