from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = "core/lowlevel_runtime/include"
CANONICAL = "core/lowlevel_runtime/c/rll_canonical_coupling.c"
MODEL = "core/lowlevel_runtime/c/rll_hz_freestanding.c"
DATASET_C = "core/lowlevel_runtime/c/rll_hz_moresco_2022_q16.c"
HARNESS = "tests/c/rll_hz_real_vectors.c"
DATASET_CSV = ROOT / "data/real/Hz_data_real.csv"
Q16 = 65536
EXPECTED_SHA256 = "83e36c1fabdb31f6b9a192a1a235f61c7cb10d4dba0ef97c00f34a8a13482f15"
EXPECTED_FNV1A64 = 0x8FCFACCD5D192767
EXPECTED_CRC32 = 0x2840ACE1


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)


def _fnv1a64(data: bytes) -> int:
    value = 14695981039346656037
    for byte in data:
        value ^= byte
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


def test_real_hz_dataset_is_exactly_anchored_to_compiled_q16_rows() -> None:
    raw = DATASET_CSV.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    assert _fnv1a64(raw) == EXPECTED_FNV1A64
    assert zlib.crc32(raw) & 0xFFFFFFFF == EXPECTED_CRC32

    source = (ROOT / DATASET_C).read_text(encoding="utf-8")
    entries = re.findall(
        r"\{(-?\d+)ll,\s*(-?\d+)ll,\s*(-?\d+)ll,\s*(\d+)u,\s*(\d+)u\}",
        source,
    )
    with DATASET_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == len(entries) == 33
    for sequence, (row, encoded) in enumerate(zip(rows, entries, strict=True), start=1):
        z_q16, h_q16, sigma_q16, source_id, encoded_sequence = map(int, encoded)
        assert z_q16 == round(float(row["z"]) * Q16)
        assert h_q16 == round(float(row["H_obs"]) * Q16)
        assert sigma_q16 == round(float(row["sigma_H"]) * Q16)
        assert source_id == (2 if "BAO" in row["source"] else 1)
        assert encoded_sequence == sequence


def test_real_hz_models_run_inside_the_canonical_coupling_region() -> None:
    exe = Path("/tmp/rll_hz_real_vectors")
    cp = _run([
        "gcc",
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        HARNESS,
        CANONICAL,
        MODEL,
        DATASET_C,
        f"-I{INCLUDE}",
        "-o",
        str(exe),
    ])
    assert cp.returncode == 0, cp.stderr
    run = _run([str(exe)])
    assert run.returncode == 0, f"real H(z) vector failure code={run.returncode}: {run.stderr}"


def test_combined_real_hz_runtime_has_no_external_symbols() -> None:
    obj = Path("/tmp/rll_hz_real_combined.o")
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
        "-r",
        CANONICAL,
        MODEL,
        DATASET_C,
        f"-I{INCLUDE}",
        "-o",
        str(obj),
    ])
    assert cp.returncode == 0, cp.stderr
    nm = _run(["nm", "-u", str(obj)])
    assert nm.returncode == 0, nm.stderr
    assert nm.stdout.strip() == ""


def test_real_hz_model_cross_compiles_for_armv7_and_aarch64() -> None:
    for target, output in {
        "armv7a-none-eabi": "/tmp/rll_hz_real_armv7.o",
        "aarch64-none-elf": "/tmp/rll_hz_real_aarch64.o",
    }.items():
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
            MODEL,
            f"-I{INCLUDE}",
            "-o",
            output,
        ])
        assert cp.returncode == 0, f"{target}: {cp.stderr}"
