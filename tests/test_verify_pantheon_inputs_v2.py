from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_pantheon_inputs.py"
CANONICAL_DIR = (
    ROOT
    / "data/real/cosmology/pantheon_plus"
    / "Pantheon+_Data/4_DISTANCES_AND_COVAR"
)
CATALOG = CANONICAL_DIR / "Pantheon+SH0ES.dat"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_pantheon_inputs", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def copy_catalog(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CATALOG, destination / "Pantheon+SH0ES.dat")


def test_canonical_repository_state_is_diagonal_only_and_fail_closed() -> None:
    module = load_module()
    report = module._build_report(CANONICAL_DIR)

    assert report["schema"] == "rll_pantheon_input_readiness_v2"
    assert report["route_state"] == "TOKEN_VAZIO_FULL_COVARIANCE"
    assert report["all_required_present"] is True
    assert report["all_present"] is False
    assert report["all_verified"] is False
    assert report["diagonal_diagnostic_ready"] is True
    assert report["full_covariance_likelihood_ready"] is False
    assert report["catalog_rows"] == 1701
    assert report["catalog_calibrator_rows"] == 77
    assert report["catalog_cosmology_rows"] == 1624
    assert report["claim_allowed"] is False

    statuses = {entry["file"]: entry["status"] for entry in report["files"]}
    assert statuses["Pantheon+SH0ES.dat"] == "READY_DIAGONAL_DIAGNOSTIC"
    assert statuses["Pantheon+SH0ES_STAT+SYS.cov"] == "TOKEN_VAZIO_FULL_COVARIANCE"
    assert statuses["Pantheon+SH0ES_STATONLY.cov"] == "TOKEN_VAZIO_STAT_ONLY_COVARIANCE"


def test_cli_json_reports_current_boundary() -> None:
    result = run_cli("--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["route_state"] == "TOKEN_VAZIO_FULL_COVARIANCE"
    assert report["diagonal_diagnostic_ready"] is True
    assert report["full_covariance_likelihood_ready"] is False
    assert report["claim_allowed"] is False


def test_require_full_covariance_fails_on_current_repository() -> None:
    result = run_cli("--require-full-covariance")
    assert result.returncode == 3
    assert "route_state=TOKEN_VAZIO_FULL_COVARIANCE" in result.stdout
    assert "full_covariance_likelihood_ready=false" in result.stdout


def test_require_diagonal_diagnostic_passes_on_exact_catalog() -> None:
    result = run_cli("--require-diagonal-diagnostic")
    assert result.returncode == 0, result.stderr
    assert "diagonal_diagnostic_ready=true" in result.stdout
    assert "claim_allowed=false" in result.stdout


def test_single_byte_catalog_tamper_is_blocked(tmp_path: Path) -> None:
    copy_catalog(tmp_path)
    target = tmp_path / "Pantheon+SH0ES.dat"
    payload = bytearray(target.read_bytes())
    payload[len(payload) // 2] ^= 0x01
    target.write_bytes(payload)

    module = load_module()
    report = module._build_report(tmp_path)
    assert report["route_state"] == "BLOCKED_CATALOG"
    assert report["diagonal_diagnostic_ready"] is False
    assert report["full_covariance_likelihood_ready"] is False
    assert report["files"][0]["status"] == "BLOCKED_CATALOG_SHA256"
    assert report["claim_allowed"] is False


def test_covariance_bytes_without_pinned_hash_remain_token_vazio(tmp_path: Path) -> None:
    copy_catalog(tmp_path)
    covariance = tmp_path / "Pantheon+SH0ES_STAT+SYS.cov"
    covariance.write_text("2\n1 0 0 1\n", encoding="utf-8")

    module = load_module()
    report = module._build_report(tmp_path)
    stat_sys = report["files"][1]
    assert stat_sys["status"] == "TOKEN_VAZIO_COVARIANCE_SHA256_POLICY"
    assert stat_sys["checksum_verified"] is False
    assert report["full_covariance_likelihood_ready"] is False


def test_hash_verified_but_wrong_shape_covariance_is_blocked(tmp_path: Path) -> None:
    copy_catalog(tmp_path)
    covariance = tmp_path / "Pantheon+SH0ES_STAT+SYS.cov"
    covariance.write_text("2\n1 0 0 1\n", encoding="utf-8")
    digest = hashlib.sha256(covariance.read_bytes()).hexdigest()
    covariance.with_name(covariance.name + ".sha256").write_text(
        f"{digest}  {covariance.name}\n", encoding="utf-8"
    )

    module = load_module()
    report = module._build_report(tmp_path)
    stat_sys = report["files"][1]
    assert stat_sys["checksum_verified"] is True
    assert stat_sys["matrix_dimension"] == 2
    assert stat_sys["matrix_values"] == 4
    assert stat_sys["status"] == "BLOCKED_COVARIANCE_DIMENSION"
    assert report["full_covariance_likelihood_ready"] is False
    assert report["claim_allowed"] is False
