"""Three-way inventory convergence: main parity check + newer lab metadata workflow."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/repo-real-inventory.yml"
YML = ROOT / "tools/inventory_config.yml"
JSON_PATH = ROOT / "tools/inventory_config.json"
OUT = ROOT / "results/inventory_config_serialization_parity.json"


def test_main_json_mirror_agrees_with_lab_yaml_source() -> None:
    old = yaml.safe_load(YML.read_text(encoding="utf-8"))
    new = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert old == new
    assert old["outputs"]["machine_summary"] == "data/results/repo_inventory_summary.json"
    assert old["claim_boundary"].startswith("No synthetic claim")


def test_migrated_main_parity_probe_executes_fail_closed_scoped() -> None:
    result = subprocess.run(
        ["python3", "tools/validate_inventory_config_parity.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    evidence = json.loads(result.stdout)
    persisted = json.loads(OUT.read_text(encoding="utf-8"))
    assert evidence == persisted
    assert evidence["schema"] == "rll.inventory_config.serialization_parity.v1"
    assert evidence["pass"] is True
    assert evidence["claim_allowed"] is False
    assert evidence["third_party_python_dependencies"] == []


def test_main_probe_and_lab_action_are_both_preserved() -> None:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps = data["jobs"]["inventory"]["steps"]
    by_name = {step["name"]: step for step in steps}
    assert "Validate inventory config YAML-to-JSON parity" in by_name
    assert "Generate real inventory from canonical tool" in by_name
    upload = by_name["Upload generated inventory artifact without committing"]
    assert upload["uses"] == "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9"
    assert "results/inventory_config_serialization_parity.json" in upload["with"]["path"]
    assert "data/results/repo_inventory.json" in upload["with"]["path"]
    assert "commit inventory updates through a reviewed pull request" in by_name[
        "Build inventory checksums and commit policy note"
    ]["run"].lower()
