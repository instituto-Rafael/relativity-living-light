import json
import pathlib
import unittest

from jsonschema import Draft202012Validator


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "rll-experiment-manifest.v1.schema.json"
HTML_PATH = ROOT / "studio" / "index.html"
CSS_PATH = ROOT / "studio" / "styles.css"
JS_PATH = ROOT / "studio" / "app.js"


class RllStudioContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema)
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.css = CSS_PATH.read_text(encoding="utf-8")
        cls.js = JS_PATH.read_text(encoding="utf-8")

    def minimal_manifest(self):
        return {
            "schema_version": "rll-experiment-manifest/1.0.0",
            "manifest_id": "TEST-001",
            "manifest_state": "NOT_MEASURED",
            "experiment": {
                "id": "test",
                "name": "Contract test",
                "model": "RLL",
                "dataset": {"name": "fixture"},
                "parameters": {},
            },
            "execution": {"state": "NOT_MEASURED"},
            "claim": {
                "allowed": False,
                "state": "BLOCKED",
                "reason": "No evidence yet",
            },
            "evidence": [
                {
                    "id": "run",
                    "title": "Execution",
                    "state": "NOT_MEASURED",
                    "summary": "Not run",
                    "limitation": "No execution evidence",
                    "next_gate": "Run governed pipeline",
                }
            ],
        }

    def test_minimal_fail_closed_manifest_is_valid(self):
        self.assertEqual([], list(self.validator.iter_errors(self.minimal_manifest())))

    def test_claim_true_cannot_be_blocked(self):
        manifest = self.minimal_manifest()
        manifest["claim"]["allowed"] = True
        errors = list(self.validator.iter_errors(manifest))
        self.assertTrue(errors, "claim.allowed=true with BLOCKED must fail schema validation")

    def test_token_vazio_is_first_class_state(self):
        states = self.schema["$defs"]["state"]["enum"]
        self.assertIn("TOKEN_VAZIO", states)
        self.assertIn("BLOCKED", states)
        self.assertIn("OBSERVED_LIMITED", states)

    def test_five_primary_views_exist(self):
        for view in ("home", "experiment", "results", "evidence", "library"):
            self.assertIn(f'data-view-panel="{view}"', self.html)

    def test_accessibility_baseline_exists(self):
        self.assertIn('class="skip-link"', self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn(":focus-visible", self.css)

    def test_ui_does_not_auto_promote_claim(self):
        self.assertIn('candidate?.claim?.allowed === true && candidate?.claim?.state !== "PASS"', self.js)
        self.assertIn('claim: { allowed: false, state: "BLOCKED"', self.js)

    def test_frontend_is_dependency_free(self):
        self.assertNotIn("https://cdn", self.html)
        self.assertNotIn("unpkg.com", self.html)
        self.assertNotIn("jsdelivr.net", self.html)


if __name__ == "__main__":
    unittest.main()
