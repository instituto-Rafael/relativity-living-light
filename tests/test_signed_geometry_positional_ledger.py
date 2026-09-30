from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
VERIFIER=ROOT/"tools"/"verify_signed_geometry_positional_ledger.py"

def test_signed_geometry_positional_ledger():
    ns=runpy.run_path(str(VERIFIER),run_name="signed_geometry_positional_ledger_test")
    payload=ns["run"]()
    assert payload["summary"]["fail"] == 0
    assert payload["summary"]["pass"] == payload["summary"]["total"]
