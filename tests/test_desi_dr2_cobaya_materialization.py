import math
import subprocess
import sys
from pathlib import Path

import yaml


def test_committed_desi_dr2_cobaya_files_are_real_likelihood_shape():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data" / "real" / "cosmology" / "desi_bao_dr2_cobaya"
    mean = data_dir / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
    cov = data_dir / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
    manifest = data_dir / "MANIFEST.json"

    assert mean.exists()
    assert cov.exists()
    assert manifest.exists()

    rows = [line.split() for line in mean.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
    matrix = [[float(item) for item in line.split()] for line in cov.read_text(encoding="utf-8").splitlines() if line]

    assert len(rows) == 13
    assert len(matrix) == 13
    assert all(len(row) == 13 for row in matrix)
    assert rows[0] == ["0.29500000", "7.94167639", "DV_over_rs"]
    assert rows[-1] == ["2.33", "38.988973961958784", "DM_over_rs"]
    assert math.isclose(matrix[1][2], matrix[2][1])
    assert matrix[1][2] < 0


def test_validacao_real_fetch_uses_committed_desi_cobaya(tmp_path):
    root = Path(__file__).resolve().parents[1]
    fetched = root / "validacao_real" / "fetched"
    if fetched.exists():
        for path in fetched.iterdir():
            path.unlink()
    subprocess.run([sys.executable, "fetch_real_data.py"], cwd=root / "validacao_real", check=True)

    desi = yaml.safe_load((fetched / "desi_dr2_bao.yml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((fetched / "manifest.json").read_text(encoding="utf-8"))

    assert desi["meta"]["status"] == "real_committed_public_likelihood"
    assert len(desi["points"]) == 13
    assert desi["points"][0]["value"] == 7.94167639
    assert desi["points"][0]["sigma"] == math.sqrt(5.78998687e-03)
    assert any(source["used"] == "committed_public_desi_dr2_cobaya_likelihood" for source in manifest["sources"])
