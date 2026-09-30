from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "fetch_dovekie_inputs.py"
spec = importlib.util.spec_from_file_location("fetch_dovekie_inputs", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _write_hd(path: Path, n: int) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# synthetic Dovekie fixture\n")
        handle.write("VARNAMES: CID IDSURVEY zHD zHEL MU MUERR MUERR_VPEC MUERR_SYS PROBIA_BEAMS\n")
        for index in range(n):
            z = 0.02 + index * 1.0e-4
            handle.write(
                f"SN: SN{index:04d} 150 {z:.6f} {z + 0.0001:.6f} "
                "35.0 0.1 0.02 0.03 1.0\n"
            )


def _write_precision(path: Path, n: int, matrix: np.ndarray | None = None) -> None:
    precision = np.eye(n) if matrix is None else np.asarray(matrix, dtype=float)
    packed = precision[np.triu_indices(n)]
    np.savez(path, n=np.array([n], dtype=int), inv_cov=packed)


def test_expected_packed_count_matches_1820_release() -> None:
    assert module.EXPECTED_PACKED_VALUES == 1_657_110


def test_hd_parser_uses_snana_varnames_and_hd_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "EXPECTED_N", 3)
    path = tmp_path / "HD.csv"
    _write_hd(path, 3)
    result = module.inspect_hd(path)
    assert result["rows"] == 3
    assert "zHD" in result["columns"]
    assert "MUST follow this HD file" in result["ordering_semantics"]


def test_precision_npz_is_reconstructed_as_inverse_covariance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "EXPECTED_N", 3)
    monkeypatch.setattr(module, "EXPECTED_PACKED_VALUES", 6)
    path = tmp_path / "STAT+SYS.npz"
    matrix = np.array([[4.0, 0.2, 0.1], [0.2, 3.0, 0.3], [0.1, 0.3, 2.0]])
    _write_precision(path, 3, matrix)
    precision, diagnostics = module.load_precision(path)
    np.testing.assert_allclose(precision, matrix)
    assert diagnostics["matrix_semantics"] == "inverse_covariance_precision"
    assert diagnostics["storage_semantics"] == "packed_upper_triangle"
    assert diagnostics["positive_definite"] is True


def test_wrong_packed_count_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "EXPECTED_N", 3)
    monkeypatch.setattr(module, "EXPECTED_PACKED_VALUES", 6)
    path = tmp_path / "STAT+SYS.npz"
    np.savez(path, n=np.array([3]), inv_cov=np.array([1.0, 2.0]))
    with pytest.raises(ValueError, match="packed count mismatch"):
        module.load_precision(path)


def test_non_positive_definite_precision_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "EXPECTED_N", 2)
    monkeypatch.setattr(module, "EXPECTED_PACKED_VALUES", 3)
    path = tmp_path / "STAT+SYS.npz"
    matrix = np.array([[1.0, 2.0], [2.0, 1.0]])
    _write_precision(path, 2, matrix)
    with pytest.raises(ValueError, match="not positive definite"):
        module.load_precision(path)


def test_receipt_policy_never_relabels_precision_as_covariance() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert '"precision_is_covariance": False' in source
    assert '"precision_is_inverse_covariance": True' in source
    assert '"claim_allowed": False' in source
