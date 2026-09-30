from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
VERIFIER=ROOT/"tools"/"verify_triangle_simplex_embedding.py"

def test_triangle_simplex_embedding():
    ns=runpy.run_path(str(VERIFIER),run_name="triangle_simplex_embedding_test")
    payload=ns["run"]()
    assert payload["summary"]["fail"] == 0
    assert payload["summary"]["pass"] == payload["summary"]["total"]
