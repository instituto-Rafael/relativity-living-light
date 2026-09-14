from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT / "core" / "lowlevel_runtime" / "include"
SRC = ROOT / "core" / "lowlevel_runtime" / "c"
CORE = SRC / "rll_canonical_real.c"
DATA = SRC / "rll_canonical_real_data.c"
SELFTEST = SRC / "rll_canonical_real_selftest.c"


def _compiler() -> str:
    cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        raise RuntimeError("C compiler not found")
    return cc


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)


def test_canonical_real_core_is_freestanding_and_self_validating() -> None:
    cc = _compiler()
    forbidden = ("<stdio.h>", "<stdlib.h>", "<string.h>", "<math.h>", "malloc(", "calloc(", "realloc(", "free(", "printf(")
    for path in (CORE, DATA, SELFTEST):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"forbidden runtime dependency {token!r} in {path}"

    with tempfile.TemporaryDirectory(prefix="rll-canonical-real-") as tmp:
        out = Path(tmp) / "rll_canonical_real.elf"
        command = [
            cc,
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-fno-pie",
            "-no-pie",
            "-nostdlib",
            "-static",
            "-ffunction-sections",
            "-fdata-sections",
            "-DRLL_FREESTANDING_ENTRY",
            f"-I{INC}",
            str(CORE),
            str(DATA),
            str(SELFTEST),
            "-Wl,--gc-sections,--build-id=none",
            "-o",
            str(out),
        ]
        _run(*command)
        completed = subprocess.run([str(out)], check=False)
        assert completed.returncode == 0

        nm = shutil.which("nm")
        if nm:
            undefined = _run(nm, "-u", str(out)).stdout.strip()
            assert undefined == "", undefined

        assert out.stat().st_size > 0
        assert hashlib.sha256(out.read_bytes()).hexdigest()


def test_embedded_real_sources_and_reference_receipt() -> None:
    receipt = json.loads((ROOT / "results" / "rll_canonical_real_freestanding.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS_LOCAL_FREESTANDING"
    assert receipt["claim_allowed"] is False
    assert receipt["runtime"]["libc"] is False
    assert receipt["runtime"]["malloc"] is False
    assert receipt["runtime"]["heap"] is False
    assert receipt["runtime"]["undefined_symbols"] == 0
    assert receipt["datasets"]["real_hz"]["n"] == 33
    assert receipt["datasets"]["real_fsigma8"]["n"] == 16
    assert receipt["datasets"]["desi_dr2_bao"]["n"] == 13
    assert receipt["datasets"]["planck_cmb_prior"]["n"] == 3
    assert receipt["crosscheck"]["fase18e_hz_abs_error"] < 2.0e-4
    assert receipt["crosscheck"]["fase18e_desi_abs_error"] < 2.0e-4
    assert receipt["crosscheck"]["fase18e_cmb_abs_error"] < 2.0e-4
