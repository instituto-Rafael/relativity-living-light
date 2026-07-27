from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = "core/lowlevel_runtime/c/rll_canonical_coupling.c"
INCLUDE = "core/lowlevel_runtime/include"
HARNESS = "tests/c/rll_canonical_coupling_vectors.c"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)


def test_canonical_coupling_builds_freestanding_without_undefined_symbols() -> None:
    obj = Path("/tmp/rll_canonical_coupling.o")
    cp = _run([
        "gcc",
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-nostdlib",
        "-c",
        C_SOURCE,
        f"-I{INCLUDE}",
        "-o",
        str(obj),
    ])
    assert cp.returncode == 0, cp.stderr

    nm = _run(["nm", "-u", str(obj)])
    assert nm.returncode == 0, nm.stderr
    assert nm.stdout.strip() == ""


def test_canonical_coupling_vectors_and_claim_boundary() -> None:
    exe = Path("/tmp/rll_canonical_coupling_vectors")
    cp = _run([
        "gcc",
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        HARNESS,
        C_SOURCE,
        f"-I{INCLUDE}",
        "-o",
        str(exe),
    ])
    assert cp.returncode == 0, cp.stderr
    run = _run([str(exe)])
    assert run.returncode == 0, f"vector failure code={run.returncode}: {run.stderr}"


def test_canonical_coupling_cross_compiles_armv7_and_aarch64() -> None:
    targets = {
        "armv7a-none-eabi": "/tmp/rll_canonical_coupling_armv7.o",
        "aarch64-none-elf": "/tmp/rll_canonical_coupling_aarch64.o",
    }
    for target, output in targets.items():
        cp = _run([
            "clang",
            f"--target={target}",
            "-std=c11",
            "-Oz",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-nostdlib",
            "-c",
            C_SOURCE,
            f"-I{INCLUDE}",
            "-o",
            output,
        ])
        assert cp.returncode == 0, f"{target}: {cp.stderr}"
