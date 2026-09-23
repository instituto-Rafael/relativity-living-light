from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_triangle_crown_torus_840_bridge.py"

def test_triangle_crown_torus_840_bridge():
    ns = runpy.run_path(str(VERIFIER), run_name="rll_triangle_crown_torus_test")
    payload = ns["run"]()
    assert payload["summary"]["fail"] == 0
    assert payload["summary"]["pass"] == payload["summary"]["total"]
