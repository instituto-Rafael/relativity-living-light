from __future__ import annotations

import csv
import re
import shutil
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "core/lowlevel_runtime/include"
SOURCES = [
    ROOT / "core/lowlevel_runtime/c/rll_canonical_freestanding.c",
    ROOT / "core/lowlevel_runtime/c/rll_canonical_hz_data.c",
    ROOT / "core/lowlevel_runtime/c/rll_canonical_entry.c",
]
EXPECTED = (
    "RLLCAN1 rows=33 valid=33 rejected=0 chi2_rll_q16=1541113 "
    "chi2_lcdm_q16=1541113 delta_q16=0 data_crc32=c7e56bca "
    "data_fnv64=f48a2db3d131c45f params_crc32=2505dec9 "
    "phase20_crc32=1b6c7c85 joint_n=1677 lnB10_q16=-405682 "
    "lnB10_err_q16=45263 delta_bic_q16=1459487 os0_ul95_q16=116 "
    "joint_best=LCDM receipt_crc32=34387926 best=TIE claim_allowed=0 "
    "token_vazio=7 numeric_flags=0"
)


def _run(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def _q16(value: str) -> int:
    return int(
        (Decimal(value) * Decimal(65536)).to_integral_value(rounding=ROUND_HALF_UP)
    )


def test_host_elf_is_freestanding_and_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "rll-canonical"
    cp = _run([str(ROOT / "scripts/build_rll_canonical_freestanding.sh"), str(output)])
    assert cp.returncode == 0, cp.stderr
    assert cp.stdout.strip() == EXPECTED

    nm = _run(["nm", "-u", str(output)])
    assert nm.returncode == 0
    assert nm.stdout.strip() == ""

    file_cp = _run(["file", str(output)])
    assert file_cp.returncode == 0
    assert "statically linked" in file_cp.stdout


def test_armv7_combined_object_has_no_runtime_helpers(tmp_path: Path) -> None:
    clang = shutil.which("clang")
    lld = shutil.which("ld.lld")
    nm_tool = shutil.which("nm")
    if not (clang and lld and nm_tool):
        return

    objects: list[Path] = []
    for source in SOURCES:
        obj = tmp_path / f"{source.stem}.o"
        cp = _run(
            [
                clang,
                "--target=armv7a-none-eabi",
                "-std=c11",
                "-O2",
                "-ffreestanding",
                "-fno-builtin",
                "-fno-stack-protector",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                f"-I{INCLUDE}",
                "-c",
                str(source),
                "-o",
                str(obj),
            ]
        )
        assert cp.returncode == 0, cp.stderr
        objects.append(obj)

    combined = tmp_path / "rll-canonical-armv7.o"
    link = _run([lld, "-r", *map(str, objects), "-o", str(combined)])
    assert link.returncode == 0, link.stderr

    undefined = _run([nm_tool, "-u", str(combined)])
    assert undefined.returncode == 0
    assert undefined.stdout.strip() == ""


def test_embedded_hz_rows_are_exact_materialization_of_csv() -> None:
    source = (ROOT / "core/lowlevel_runtime/c/rll_canonical_hz_data.c").read_text(
        encoding="utf-8"
    )
    embedded = [
        tuple(map(int, match))
        for match in re.findall(
            r"\{\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(\d+)u\s*\}",
            source,
        )
    ]

    source_ids = {
        "CC_Moresco2022": 1,
        "CC+BAO_BOSS": 2,
        "BAO_Lya": 3,
    }
    with (ROOT / "data/real/Hz_data_real.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        expected = [
            (
                _q16(row["z"]),
                _q16(row["H_obs"]),
                _q16(row["sigma_H"]),
                source_ids[row["source"]],
            )
            for row in csv.DictReader(handle)
        ]

    assert len(embedded) == 33
    assert embedded == expected


def test_c_sources_have_no_hosted_headers_or_heap_calls() -> None:
    forbidden = (
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <string.h>",
        "#include <math.h>",
        "malloc(",
        "calloc(",
        "realloc(",
        "free(",
        "printf(",
        "fprintf(",
        "snprintf(",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in SOURCES)
    for token in forbidden:
        assert token not in text
