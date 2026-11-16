import tempfile
import unittest
from pathlib import Path
from tools.ci.rll_workflow_dependency_preflight import validate, literal_paths


class StaticWorkflowPreflightTests(unittest.TestCase):
    def test_literal_run_python_and_pycompile(self):
        self.assertEqual(literal_paths("run: python tools/a.py"), ["tools/a.py"])
        self.assertEqual(literal_paths("run: python -m py_compile scripts/a.py rx/http.py"), ["scripts/a.py", "rx/http.py"])
        self.assertEqual(literal_paths("python - <<'PY'"), [])
        self.assertEqual(literal_paths("python -m pytest tests/foo.py"), [])

    def test_missing_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "w.yml").write_text("run: python tools/missing.py\n", encoding="utf-8")
            result = validate(root, ["w.yml"])
            self.assertEqual(result["status"], "STATIC_SCOPE_FAIL")
            self.assertEqual(result["missing_local_scripts"], ["tools/missing.py"])
            self.assertFalse(result["claim_allowed"])

    def test_no_third_party_imports_only_when_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tools").mkdir()
            (root / "tools" / "a.py").write_text("import json\nimport numpy\n", encoding="utf-8")
            (root / "w.yml").write_text("run: python tools/a.py\n", encoding="utf-8")
            self.assertEqual(validate(root, ["w.yml"])["status"], "STATIC_SCOPE_PASS")
            result = validate(root, ["w.yml"], stdlib_only=True)
            self.assertEqual(result["status"], "STATIC_SCOPE_FAIL")
            self.assertIn("tools/a.py:numpy", result["non_stdlib_imports"])

    def test_existing_local_script_passes_only_static_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()
            (root / "scripts" / "go.py").write_text("import json\n", encoding="utf-8")
            (root / "w.yml").write_text("run: python scripts/go.py\n", encoding="utf-8")
            result = validate(root, ["w.yml"], stdlib_only=True)
            self.assertEqual(result["status"], "STATIC_SCOPE_PASS")
            self.assertEqual(result["exact_head_ci"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
