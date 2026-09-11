import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_rll_climate_engine_live_probe.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "rll-climate-engine-trial-live.yml"
REGISTRY_PATH = ROOT / "data" / "governance" / "RLL_RUNTIME_SECRET_PROBES_V1.json"

spec = importlib.util.spec_from_file_location("rll_live_probe", RUNNER_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ClimateEngineLiveProbeTests(unittest.TestCase):
    def test_runtime_registry_keeps_credentials_separate(self):
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertFalse(data["claim_allowed"])
        self.assertTrue(data["cross_credential_invariants"]["same_job_consumption_forbidden"])
        self.assertEqual(
            data["probes"]["climate_engine_trial"]["actions_secret_name"],
            "RLL_CLIMATE_ENGINE_TRIAL_TOKEN",
        )
        self.assertEqual(data["probes"]["github_repository_pat"]["actions_secret_name"], "GITPAT")

    def test_workflow_is_manual_for_live_secret_consumption(self):
        text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("if: github.event_name == 'workflow_dispatch'", text)
        self.assertIn("CLIMATE_ENGINE_API_KEY: ${{ secrets.RLL_CLIMATE_ENGINE_TRIAL_TOKEN }}", text)
        self.assertNotIn("pull_request_target:", text)
        self.assertIn("permissions:\n  contents: read", text)
        self.assertIn("persist-credentials: false", text)

    def test_runner_avoids_shell_and_secret_metadata(self):
        text = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("shell=True", text)
        self.assertNotIn("len(secret)", text)
        self.assertNotIn("sha256(secret", text)
        self.assertIn("subprocess.run(argv", text)
        self.assertIn("secret_binding_present_boolean", text)

    def test_forbidden_receipt_keys_are_explicit(self):
        self.assertEqual(
            module.RECEIPT_FORBIDDEN_KEYS,
            {"secret_value", "secret_length", "secret_hash", "authorization_header"},
        )


if __name__ == "__main__":
    unittest.main()
