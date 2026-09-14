import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/validate_drive_formula_graph_patch.py"

spec = importlib.util.spec_from_file_location("drive_formula_patch_validator", VALIDATOR)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

def test_drive_formula_graph_patch_batch1():
    receipt = module.validate()
    assert receipt["status"] == "PASS"
    assert receipt["claim_allowed"] is False
    assert receipt["original_gap"] == 122
    assert receipt["reconstructed_exact_literal"] == 18
    assert receipt["remaining_gap"] == 104
