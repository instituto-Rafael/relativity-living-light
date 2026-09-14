from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PantheonLegacyRouteContractTests(unittest.TestCase):
    def _load_loader(self):
        path = ROOT / "scripts/pantheon/load_pantheon.py"
        spec = importlib.util.spec_from_file_location("rll_load_pantheon_test", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def test_explicit_materialized_path_has_priority(self) -> None:
        loader = self._load_loader()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Pantheon+SH0ES.dat"
            path.write_text("zHD MU_SH0ES MU_SH0ES_ERR_DIAG IS_CALIBRATOR\n")
            self.assertEqual(loader.resolve_pantheon_path(path), path.resolve())

    def test_missing_bytes_are_typed_token_vazio(self) -> None:
        loader = self._load_loader()
        old = os.environ.pop("RLL_PANTHEON_PATH", None)
        try:
            with self.assertRaisesRegex(FileNotFoundError, "TOKEN_VAZIO_SOURCE_BYTES"):
                loader.resolve_pantheon_path("/definitely/absent/rll-pantheon.dat")
        finally:
            if old is not None:
                os.environ["RLL_PANTHEON_PATH"] = old

    def test_runner_uses_real_module_name_and_no_claude_output_path(self) -> None:
        source = (ROOT / "scripts/pantheon/run_rll_vs_pantheon.py").read_text()
        self.assertIn("from models_pantheon import fit_model", source)
        self.assertNotIn("/home/claude/rll_pantheon/RESULTADO_REAL.txt", source)
        self.assertIn('"evidence_class": "C"', source)


if __name__ == "__main__":
    unittest.main()
