import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.validate_rll_credential_authority import (
    CLIMATE_SECRET,
    DEFAULT_POLICY,
    GITHUB_ASSURANCE_WORKFLOW,
    GITHUB_SECRET,
    audit,
    _payload,
)


ROOT = Path(__file__).resolve().parents[1]


class CredentialAuthorityTests(unittest.TestCase):
    def test_current_repository_contract_is_static_pass(self):
        findings, payload = audit(ROOT, DEFAULT_POLICY)
        errors = [item for item in findings if item.severity == "ERROR"]
        self.assertEqual([], errors)
        self.assertEqual("PASS", payload["decision"])
        self.assertEqual([GITHUB_SECRET, CLIMATE_SECRET], payload["canonical_repository_secrets"])
        self.assertFalse(payload["claim_allowed"])
        self.assertFalse(payload["secret_value_observed"])

    def _repo(self, workflow: str, path: str = ".github/workflows/test.yml") -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ".github/workflows").mkdir(parents=True)
        (root / "data/governance").mkdir(parents=True)
        policy = json.loads((ROOT / DEFAULT_POLICY).read_text(encoding="utf-8"))
        (root / DEFAULT_POLICY).write_text(
            json.dumps(policy, indent=2) + "\n", encoding="utf-8"
        )
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(workflow, encoding="utf-8")
        return root

    def test_legacy_github_pat_name_is_forbidden_in_actions(self):
        root = self._repo("""name: x
'on':
  workflow_dispatch:
permissions:
  contents: read
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
        env:
          TOKEN: ${{ secrets.RLL_GITHUB_PAT }}
""")
        findings, _ = audit(root)
        self.assertIn("GITHUB_PAT_IN_ACTIONS_FORBIDDEN", {item.code for item in findings})

    def test_gitpat_is_forbidden_outside_reviewed_assurance_workflow(self):
        root = self._repo("""name: x
'on':
  workflow_dispatch:
permissions:
  contents: read
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      GITPAT: ${{ secrets.GITPAT }}
    steps:
      - run: echo safe
""")
        findings, _ = audit(root)
        self.assertIn("GITPAT_OUTSIDE_ASSURANCE_WORKFLOW", {item.code for item in findings})

    def test_reviewed_gitpat_assurance_shape_is_allowed(self):
        root = self._repo("""name: x
'on':
  workflow_dispatch:
permissions:
  contents: read
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      GITPAT: ${{ secrets.GITPAT }}
    steps:
      - run: python tools/read_only_probe.py
""", GITHUB_ASSURANCE_WORKFLOW)
        findings, _ = audit(root)
        codes = {item.code for item in findings}
        self.assertNotIn("GITPAT_OUTSIDE_ASSURANCE_WORKFLOW", codes)
        self.assertNotIn("GITPAT_NON_MANUAL", codes)

    def test_climate_trial_requires_manual_job_guard(self):
        root = self._repo("""name: x
'on':
  push:
permissions:
  contents: read
jobs:
  x:
    runs-on: ubuntu-latest
    env:
      RLL_CLIMATE_ENGINE_TRIAL_TOKEN: ${{ secrets.RLL_CLIMATE_ENGINE_TRIAL_TOKEN }}
    steps:
      - run: echo safe
""")
        findings, _ = audit(root)
        self.assertIn("CLIMATE_TRIAL_NON_MANUAL", {item.code for item in findings})

    def test_destructive_operation_is_rejected_with_trial_secret(self):
        root = self._repo("""name: x
'on':
  workflow_dispatch:
permissions:
  contents: read
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      RLL_CLIMATE_ENGINE_TRIAL_TOKEN: ${{ secrets.RLL_CLIMATE_ENGINE_TRIAL_TOKEN }}
    steps:
      - run: curl -X DELETE https://example.invalid/resource
""")
        findings, _ = audit(root)
        self.assertIn("DESTRUCTIVE_OPERATION_WITH_SECRET", {item.code for item in findings})

    def test_cross_credential_same_workflow_is_rejected(self):
        root = self._repo("""name: x
'on':
  workflow_dispatch:
permissions:
  contents: read
jobs:
  x:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    env:
      GITPAT: ${{ secrets.GITPAT }}
      CLIMATE: ${{ secrets.RLL_CLIMATE_ENGINE_TRIAL_TOKEN }}
    steps:
      - run: echo safe
""", GITHUB_ASSURANCE_WORKFLOW)
        findings, _ = audit(root)
        self.assertIn("CROSS_CREDENTIAL_SAME_WORKFLOW", {item.code for item in findings})

    def test_runtime_receipt_never_contains_secret_material(self):
        secret = "opaque-test-secret-never-persist"
        with patch.dict(os.environ, {CLIMATE_SECRET: secret}, clear=False):
            present = bool(os.environ.get(CLIMATE_SECRET))
            payload = _payload([], True, present, [])
        encoded = json.dumps(payload)
        self.assertTrue(payload["climate_actions_secret_present"])
        self.assertNotIn(secret, encoded)
        self.assertFalse(payload["secret_value_observed"])
        self.assertFalse(payload["secret_value_hashed"])


if __name__ == "__main__":
    unittest.main()
