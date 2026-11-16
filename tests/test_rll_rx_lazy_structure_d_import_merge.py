"""Non-regression: Rx Structure-D successor imports with stdlib-only Python.

This test checks the package import under -S (without third-party site packages)
and preserves the historical public names via lazy loading.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_structure_d_imports_without_numpy_or_pandas_installed() -> None:
    snippet = (
        "import json,sys;import data.pipelines.structure_d as s;"
        "names=('aic','bic','chi2','chi2_with_covariance','evaluate_model',"
        "'evaluate_posterior','is_physically_stable','load_csv',"
        "'log_likelihood','log_prior');"
        "assert all(x in s.__all__ for x in names);"
        "assert 'numpy' not in sys.modules and 'pandas' not in sys.modules;"
        "print(json.dumps({'status':'PASS_SCOPED_IMPORT_ONLY','legacy_symbols':len(names),"
        "'numpy_imported':False,'claim_allowed':False}))"
    )
    result = subprocess.run(
        [sys.executable, "-S", "-c", snippet],
        cwd=ROOT, capture_output=True, text=True, check=True
    )
    obj = json.loads(result.stdout)
    assert obj["status"] == "PASS_SCOPED_IMPORT_ONLY"
    assert obj["legacy_symbols"] == 10
    assert obj["numpy_imported"] is False
    assert obj["claim_allowed"] is False


def test_rx_operation_contracts_remain_fail_closed() -> None:
    for relative in (
        "validacao_real/rx_operation.json",
        "validacao_real/rx_multiprobe_operation.json",
    ):
        doc = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        assert doc["schema"] == "rll.development_operation.v1"
        assert doc["authority"]["human_required"] is True
        assert doc["authority"]["self_authorized"] is False
        assert doc["autonomy"]["goal_setting"] is False
        assert doc["autonomy"]["scope_expansion"] is False
        assert doc["claim_allowed"] is False
