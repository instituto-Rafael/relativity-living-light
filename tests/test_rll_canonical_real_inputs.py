from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "core/lowlevel_runtime/include"
COUPLING = ROOT / "core/lowlevel_runtime/c/rll_canonical_coupling.c"
REAL_INPUTS = ROOT / "core/lowlevel_runtime/c/rll_canonical_real_inputs.c"
RUNNER = ROOT / "tests/c/rll_canonical_real_inputs_runner.c"

DATA_PATHS = [
    ROOT / "data/real/Hz_data_real.csv",
    ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv",
    ROOT / "data/real/cosmology/fsigma8_growth_real.csv",
    ROOT / "data/real/CMB_shift_real.json",
]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def compile_host_runner(output: Path) -> None:
    result = run(
        "gcc",
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        str(RUNNER),
        str(COUPLING),
        str(REAL_INPUTS),
        f"-I{INCLUDE}",
        "-o",
        str(output),
    )
    assert result.returncode == 0, result.stderr


def test_combined_kernel_is_freestanding_and_self_contained(tmp_path: Path) -> None:
    coupling_obj = tmp_path / "coupling.o"
    inputs_obj = tmp_path / "real_inputs.o"
    combined_obj = tmp_path / "combined.o"
    common = [
        "-std=c11",
        "-O2",
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
    ]
    first = run("gcc", *common, str(COUPLING), f"-I{INCLUDE}", "-o", str(coupling_obj))
    assert first.returncode == 0, first.stderr
    second = run("gcc", *common, str(REAL_INPUTS), f"-I{INCLUDE}", "-o", str(inputs_obj))
    assert second.returncode == 0, second.stderr
    linked = run("gcc", "-nostdlib", "-r", str(coupling_obj), str(inputs_obj), "-o", str(combined_obj))
    assert linked.returncode == 0, linked.stderr
    undefined = run("nm", "-u", str(combined_obj))
    assert undefined.returncode == 0, undefined.stderr
    assert undefined.stdout.strip() == ""


@pytest.mark.parametrize("target", ["armv7a-none-eabi", "aarch64-none-elf"])
def test_real_input_adapter_cross_compiles(target: str, tmp_path: Path) -> None:
    clang = shutil.which("clang")
    if clang is None:
        pytest.skip("clang is not installed")
    output = tmp_path / f"real_inputs-{target}.o"
    result = run(
        clang,
        f"--target={target}",
        "-std=c11",
        "-Oz",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-nostdlib",
        "-c",
        str(REAL_INPUTS),
        f"-I{INCLUDE}",
        "-o",
        str(output),
    )
    assert result.returncode == 0, result.stderr


def test_exact_committed_inputs_bind_65_observations(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    result = run(str(executable), *(str(path) for path in DATA_PATHS), "identity")
    assert result.returncode == 0, result.stderr or result.stdout
    assert "verified=15" in result.stdout
    assert "rows=65" in result.stdout
    assert "bound=65" in result.stdout
    assert "hz=33 bao=13 fs8=16 cmb=3" in result.stdout
    assert "covariance=1" in result.stdout
    assert "total=65 evidence=65 blocked=0" in result.stdout
    assert "chi2_q16=0" in result.stdout
    assert "claim_allowed=0" in result.stdout


def test_missing_model_stays_fail_closed(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    result = run(str(executable), *(str(path) for path in DATA_PATHS), "none")
    assert result.returncode == 0, result.stderr or result.stdout
    assert "rows=65" in result.stdout
    assert "bound=0 token_vazio=65" in result.stdout
    assert "covariance=0" in result.stdout
    assert "total=65 evidence=0 blocked=65" in result.stdout
    assert "claim_allowed=0" in result.stdout


def test_single_byte_tamper_is_rejected_before_parsing(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    tampered = tmp_path / "desi-tampered.csv"
    payload = bytearray(DATA_PATHS[1].read_bytes())
    payload[-2] ^= 0x01
    tampered.write_bytes(payload)
    paths = [DATA_PATHS[0], tampered, DATA_PATHS[2], DATA_PATHS[3]]
    result = run(str(executable), *(str(path) for path in paths), "identity")
    assert result.returncode != 0
    assert "status=-2" in result.stdout
    assert "rows=0" in result.stdout
