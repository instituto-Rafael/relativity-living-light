import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.validate_rll_repository_pat_assurance import runtime_probe, static_validate

ROOT = Path(__file__).resolve().parents[1]


class RepositoryPatAssuranceTests(unittest.TestCase):
    def test_current_contract_is_static_pass(self):
        self.assertEqual([], static_validate(ROOT))

    def test_missing_secret_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            receipt = runtime_probe("instituto-Rafael/relativity-living-light")
        self.assertEqual("TOKEN_VAZIO_SECRET_BINDING", receipt["decision"])
        self.assertFalse(receipt["secret_binding_present"])
        self.assertFalse(receipt["secret_value_observed"])
        self.assertFalse(receipt["secret_value_hashed"])

    def test_static_validator_rejects_mutating_workflow(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data/governance").mkdir(parents=True)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "data/governance/RLL_REPOSITORY_PAT_ASSURANCE_EXCEPTION_V1.json").write_text(
                (ROOT / "data/governance/RLL_REPOSITORY_PAT_ASSURANCE_EXCEPTION_V1.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / ".github/workflows/rll-repository-pat-assurance.yml").write_text(
                """name: bad\non:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n  assurance:\n    if: github.event_name == 'workflow_dispatch'\n    runs-on: ubuntu-latest\n    steps:\n      - env:\n          GITPAT: ${{ secrets.GITPAT }}\n        run: curl -X DELETE https://api.github.com/repos/o/r\n""",
                encoding="utf-8",
            )
            errors = static_validate(root)
            self.assertTrue(any(item.startswith("FORBIDDEN_PATTERN:") for item in errors))


if __name__ == "__main__":
    unittest.main()
