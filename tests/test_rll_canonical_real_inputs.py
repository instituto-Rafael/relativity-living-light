from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "core/lowlevel_runtime/include"
COUPLING = ROOT / "core/lowlevel_runtime/c/rll_canonical_coupling.c"
REAL_INPUTS = ROOT / "core/lowlevel_runtime/c/rll_canonical_real_inputs.c"
REAL_MODELS = ROOT / "core/lowlevel_runtime/c/rll_canonical_real_models.c"
REAL_KERNEL = ROOT / "core/lowlevel_runtime/c/rll_canonical_real.c"
REAL_DATA = ROOT / "core/lowlevel_runtime/c/rll_canonical_real_data.c"
HZ_MODEL = ROOT / "core/lowlevel_runtime/c/rll_hz_freestanding.c"
HZ_DATA = ROOT / "core/lowlevel_runtime/c/rll_hz_moresco_2022_q16.c"
RUNNER = ROOT / "tests/c/rll_canonical_real_inputs_runner.c"

PRODUCTION_SOURCES = [
    COUPLING,
    REAL_INPUTS,
    REAL_MODELS,
    REAL_KERNEL,
    REAL_DATA,
    HZ_MODEL,
    HZ_DATA,
]
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
        *(str(source) for source in PRODUCTION_SOURCES),
        f"-I{INCLUDE}",
        "-o",
        str(output),
    )
    assert result.returncode == 0, result.stderr


def execute(executable: Path, mode: str) -> subprocess.CompletedProcess[str]:
    return run(str(executable), *(str(path) for path in DATA_PATHS), mode)


def chi2_from_output(output: str) -> int:
    match = re.search(r"chi2_q16=(-?\d+)", output)
    assert match is not None, output
    return int(match.group(1))


def test_combined_kernel_is_freestanding_and_self_contained(tmp_path: Path) -> None:
    objects: list[Path] = []
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
    for source in PRODUCTION_SOURCES:
        output = tmp_path / f"{source.stem}.o"
        compiled = run("gcc", *common, str(source), f"-I{INCLUDE}", "-o", str(output))
        assert compiled.returncode == 0, f"{source}: {compiled.stderr}"
        objects.append(output)

    combined = tmp_path / "rll-canonical-real-combined.o"
    linked = run("gcc", "-nostdlib", "-r", *(str(obj) for obj in objects), "-o", str(combined))
    assert linked.returncode == 0, linked.stderr
    undefined = run("nm", "-u", str(combined))
    assert undefined.returncode == 0, undefined.stderr
    assert undefined.stdout.strip() == ""


@pytest.mark.parametrize("target", ["armv7a-none-eabi", "aarch64-none-elf"])
def test_real_input_adapter_and_bridge_cross_compile(target: str, tmp_path: Path) -> None:
    clang = shutil.which("clang")
    if clang is None:
        pytest.skip("clang is not installed")
    for source in (REAL_INPUTS, REAL_MODELS, REAL_KERNEL):
        output = tmp_path / f"{source.stem}-{target}.o"
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
            str(source),
            f"-I{INCLUDE}",
            "-o",
            str(output),
        )
        assert result.returncode == 0, f"{source}: {result.stderr}"


def test_exact_committed_inputs_bind_65_observations(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    result = execute(executable, "identity")
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
    result = execute(executable, "none")
    assert result.returncode == 0, result.stderr or result.stdout
    assert "rows=65" in result.stdout
    assert "bound=0 token_vazio=65" in result.stdout
    assert "covariance=0" in result.stdout
    assert "total=65 evidence=0 blocked=65" in result.stdout
    assert "claim_allowed=0" in result.stdout


def test_lcdm_kernel_binds_real_hz_and_preserves_other_gaps(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    result = execute(executable, "lcdm")
    assert result.returncode == 0, result.stderr or result.stdout
    assert "bound=33 token_vazio=32" in result.stdout
    assert "total=65 evidence=33 blocked=32" in result.stdout
    assert "covariance=0" in result.stdout
    assert "chi2_q16=1491916" in result.stdout
    assert "claim_allowed=0" in result.stdout


def test_rll_kernel_binds_real_hz_and_preserves_other_gaps(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    result = execute(executable, "rll")
    assert result.returncode == 0, result.stderr or result.stdout
    assert "bound=33 token_vazio=32" in result.stdout
    assert "total=65 evidence=33 blocked=32" in result.stdout
    assert "covariance=0" in result.stdout
    assert "chi2_q16=1800068" in result.stdout
    assert "claim_allowed=0" in result.stdout


@pytest.mark.parametrize("mode", ["L", "R"])
def test_joint_fase18e_profiles_bind_all_real_observations(mode: str, tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    first = execute(executable, mode)
    second = execute(executable, mode)

    assert first.returncode == 0, first.stderr or first.stdout
    assert second.returncode == 0, second.stderr or second.stdout
    assert first.stdout == second.stdout
    assert "verified=15 rows=65 bound=65 token_vazio=0" in first.stdout
    assert "hz=33 bao=13 fs8=16 cmb=3 covariance=1" in first.stdout
    assert "total=65 evidence=65 blocked=0" in first.stdout
    assert chi2_from_output(first.stdout) > 0
    assert "claim_allowed=0" in first.stdout


def test_joint_profiles_are_numerically_distinct(tmp_path: Path) -> None:
    executable = tmp_path / "rll-real-inputs"
    compile_host_runner(executable)
    lcdm = execute(executable, "L")
    rll = execute(executable, "R")
    assert lcdm.returncode == 0, lcdm.stderr or lcdm.stdout
    assert rll.returncode == 0, rll.stderr or rll.stdout
    assert chi2_from_output(lcdm.stdout) != chi2_from_output(rll.stdout)


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
