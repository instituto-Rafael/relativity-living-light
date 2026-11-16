"""Direct-script import regression for the legacy materialization route."""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LegacyRealDataDirectImportTests(unittest.TestCase):
    def test_legacy_fetcher_is_importable_in_isolated_script_context(self):
        """Regression for START_MANUAL_HERE.yml and direct pipeline callers."""
        script = ROOT / "validacao_real" / "fetch_real_data.py"
        code = (
            "import importlib.util, pathlib, sys; "
            "p = pathlib.Path(sys.argv[1]); "
            "s = importlib.util.spec_from_file_location('legacy_fetcher', p); "
            "m = importlib.util.module_from_spec(s); "
            "s.loader.exec_module(m); "
            "assert m.ROOT == p.resolve().parents[1]; "
            "assert 'does not validate RLL' in m.CLAIM_BOUNDARY"
        )
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env["RLL_LEGACY_NETWORK_PROBE"] = "0"
        result = subprocess.run(
            [sys.executable, "-I", "-c", code, str(script)],
            cwd=ROOT / "validacao_real",
            env=env, capture_output=True, text=True,
            timeout=25, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
