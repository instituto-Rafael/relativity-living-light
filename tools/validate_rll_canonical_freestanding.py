#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("core/lowlevel_runtime/c/rll_canonical_coupling.c")
HEADER = Path("core/lowlevel_runtime/include/rll_canonical_coupling.h")
HARNESS = Path("tests/c/rll_canonical_coupling_vectors.c")
REPORT = Path("artifacts/canonical-coupling/validation.json")


def sha256(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def run(command: list[str]) -> dict[str, object]:
    cp = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": cp.returncode,
        "stdout": cp.stdout,
        "stderr": cp.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    host_obj = "/tmp/rll_canonical_coupling.o"
    host_exe = "/tmp/rll_canonical_coupling_vectors"
    commands = [
        [
            "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
            "-nostdlib", "-c", str(SOURCE),
            "-Icore/lowlevel_runtime/include", "-o", host_obj,
        ],
        ["nm", "-u", host_obj],
        [
            "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(HARNESS), str(SOURCE),
            "-Icore/lowlevel_runtime/include", "-o", host_exe,
        ],
        [host_exe],
        [
            "clang", "--target=armv7a-none-eabi", "-std=c11", "-Oz",
            "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-builtin",
            "-fno-stack-protector", "-nostdlib", "-c", str(SOURCE),
            "-Icore/lowlevel_runtime/include", "-o", "/tmp/rll_canonical_armv7.o",
        ],
        [
            "clang", "--target=aarch64-none-elf", "-std=c11", "-Oz",
            "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-builtin",
            "-fno-stack-protector", "-nostdlib", "-c", str(SOURCE),
            "-Icore/lowlevel_runtime/include", "-o", "/tmp/rll_canonical_aarch64.o",
        ],
    ]

    results = [run(command) for command in commands]
    undefined_symbols_empty = results[1]["returncode"] == 0 and not str(results[1]["stdout"]).strip()
    status = "PASS" if all(item["returncode"] == 0 for item in results) and undefined_symbols_empty else "FAIL"
    report = {
        "schema": "rll_canonical_freestanding_validation_v1",
        "status": status,
        "claim_allowed": False,
        "source_contract": {
            "no_heap": True,
            "no_libc_calls": undefined_symbols_empty,
            "fixed_point": "Q16.16",
            "host_vector_exit_zero": results[3]["returncode"] == 0,
            "armv7_object": results[4]["returncode"] == 0,
            "aarch64_object": results[5]["returncode"] == 0,
        },
        "boundaries": {
            "local_geophysics_is_cosmological_evidence": False,
            "synthetic_is_observational_evidence": False,
            "exact_geometry_is_physical_validation": False,
            "token_vazio_is_zero": False,
        },
        "sha256": {
            "header": sha256(HEADER),
            "source": sha256(SOURCE),
            "harness": sha256(HARNESS),
        },
        "commands": results,
    }

    if args.write_report:
        (ROOT / REPORT).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / REPORT).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": status,
        "undefined_symbols_empty": undefined_symbols_empty,
        "armv7": report["source_contract"]["armv7_object"],
        "aarch64": report["source_contract"]["aarch64_object"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
