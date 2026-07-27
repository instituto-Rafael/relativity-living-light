from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "core/lowlevel_runtime/c/rll_canonical_region.c"
INC = ROOT / "core/lowlevel_runtime/include"
RUNNER = ROOT / "tests/canonical_region_host_runner.c"

REAL_INPUTS = {
    ROOT / "data/real/Hz_data_real.csv": "1194fe2066dc3d92b4870cfb03d2cdbe2a316deae2e1355943f7f2ccca6d52b6",
    ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv": "5ab328705937c69cedb662bbb35888df20c6cabf3810ec3c5e7376d69ccb0a69",
    ROOT / "data/real/cosmology/fsigma8_growth_real.csv": "3781a2fa7bce9ea600060f9feb6e74ba49f4baa4ce2e7344803295c912318211",
    ROOT / "data/real/CMB_shift_real.json": "e86d996131cf4b3758f4fe0319b6c7da752a38ab2f141abaa81bec66d8e6d979",
}


def run(*cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)


def test_canonical_region_compiles_as_freestanding_object(tmp_path: Path) -> None:
    obj = tmp_path / "rll_canonical_region.o"
    cp = run(
        "gcc",
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-asynchronous-unwind-tables",
        "-nostdlib",
        "-c",
        str(SRC),
        f"-I{INC}",
        "-o",
        str(obj),
    )
    assert cp.returncode == 0, cp.stderr
    nm = run("nm", "-u", str(obj))
    assert nm.returncode == 0, nm.stderr
    assert nm.stdout.strip() == ""


def test_committed_real_inputs_match_pinned_sha256() -> None:
    for path, expected in REAL_INPUTS.items():
        assert path.is_file(), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_canonical_region_consumes_all_committed_real_blocks(tmp_path: Path) -> None:
    exe = tmp_path / "rll_canonical_region_runner"
    cp = run(
        "gcc",
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        str(RUNNER),
        str(SRC),
        f"-I{INC}",
        "-o",
        str(exe),
    )
    assert cp.returncode == 0, cp.stderr
    ordered_paths = [str(path) for path in REAL_INPUTS]
    execution = run(str(exe), *ordered_paths)
    assert execution.returncode == 0, execution.stderr or execution.stdout
    assert "RLL_CANONICAL_REGION_V1 PASS" in execution.stdout
    assert "accepted=65" in execution.stdout
    assert "claim_allowed=0" in execution.stdout
