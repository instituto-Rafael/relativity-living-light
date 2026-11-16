"""Adversarial tests for the bounded stdlib technology-watch migration."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rx.schema_subset import RxSchemaSubsetError
from rx.yaml_subset import RxYamlSubsetError
from scripts.validate_watch_config import load_config, validate_config


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "rll_inovacao_tecnologica_watch.yml"
CANONICAL = ROOT / "rll_inovacao_tecnologica_watch.json"
SCHEMA = ROOT / "schemas/rll_watch.schema.json"


class WatchConfigStdlibTests(unittest.TestCase):
    def test_existing_yaml_matches_versioned_json_exactly(self):
        self.assertEqual(load_config(LEGACY), load_config(CANONICAL))
        validate_config(LEGACY, SCHEMA)
        validate_config(CANONICAL, SCHEMA)

    def test_rootless_script_entrypoint_keeps_working(self):
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        p = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_watch_config.py"),
             "--config", str(LEGACY), "--schema", str(SCHEMA)],
            cwd=ROOT, env=env, capture_output=True, text=True,
            check=False, timeout=30,
        )
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_unsupported_formats_and_yaml_features_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "watch.yaml"
            path.write_text("source:\n  name: &anchor illegal\n", encoding="utf-8")
            with self.assertRaises(RxYamlSubsetError):
                load_config(path)
            unsupported = Path(tmp) / "watch.txt"
            unsupported.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(unsupported)

    def test_bad_schema_values_and_missing_fields_are_rejected(self):
        source = load_config(CANONICAL)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            for change in ("missing_name", "bad_enum", "bad_date"):
                payload = json.loads(json.dumps(source))
                if change == "missing_name":
                    del payload["source"]["name"]
                elif change == "bad_enum":
                    payload["source"]["academic_weight"] = "unsupported_weight"
                else:
                    payload["source"]["last_reviewed"] = "2026-99-99"
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.subTest(change=change):
                    with self.assertRaises(RxSchemaSubsetError):
                        validate_config(path, SCHEMA)

    def test_no_third_party_yaml_or_jsonschema_import(self):
        tree = ast.parse((ROOT / "scripts/validate_watch_config.py").read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertFalse(imports.intersection({"yaml", "jsonschema"}))


if __name__ == "__main__":
    unittest.main()
