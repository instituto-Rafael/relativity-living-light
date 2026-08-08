from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "materialize_desi_dr2_bao_cobaya.py"


def load_module():
    spec = importlib.util.spec_from_file_location("desi_dr2_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_manifest_is_complete_and_fail_closed():
    m = load_module()
    manifest = m.load_manifest()
    assert manifest["claim_boundary"]["claim_allowed"] is False
    assert manifest["promotion"]["mode"] == "additive_safe_extraction_only"
    assert manifest["promotion"]["workflow_overwrite"] is False
    assert manifest["promotion"]["directory_moves"] is False
    assert manifest["promotion"]["deletions"] is False
    assert len(manifest["files"]) == 16
    assert len({entry["local_file"] for entry in manifest["files"]}) == 16
    assert {entry["subset"] for entry in manifest["files"]} == {
        "ALL",
        "BGS_BRIGHT-21.35",
        "LRG_z0.4-0.6",
        "LRG_z0.6-0.8",
        "LRG+ELG",
        "ELG_z1.1-1.6",
        "QSO",
        "Lya",
    }


def test_every_committed_file_matches_pinned_local_custody():
    m = load_module()
    manifest = m.load_manifest()
    receipts = [m.verify_local_entry(entry) for entry in manifest["files"]]
    assert all(row["ok"] for row in receipts), receipts


def test_subset_mean_and_covariance_dimensions_match():
    m = load_module()
    manifest = m.load_manifest()
    grouped = {}
    for entry in manifest["files"]:
        if entry["subset"] == "ALL":
            continue
        grouped.setdefault(entry["subset"], {})[entry["upstream_file"].rsplit("_", 1)[-1].split(".")[0]] = entry

    for subset, pair in grouped.items():
        mean_path = ROOT / pair["mean"]["local_file"]
        cov_path = ROOT / pair["cov"]["local_file"]
        mean_rows = [
            line.split()
            for line in mean_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        cov_rows = [
            [float(value) for value in line.split()]
            for line in cov_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        n = len(mean_rows)
        assert n in {1, 2}, subset
        assert len(cov_rows) == n, subset
        assert all(len(row) == n for row in cov_rows), subset


def test_verify_only_cli_is_offline_and_ready():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--verify-only", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    receipt = json.loads(proc.stdout)
    assert receipt["state"] == "READY_COMMITTED_SMALL_LIKELIHOOD"
    assert receipt["files_total"] == 16
    assert receipt["files_ok"] == 16
    assert receipt["files_failed"] == 0
    assert receipt["claim_allowed"] is False
