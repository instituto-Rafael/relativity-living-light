#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = "core/lowlevel_runtime/include"
CANONICAL = "core/lowlevel_runtime/c/rll_canonical_coupling.c"
MODEL = "core/lowlevel_runtime/c/rll_hz_freestanding.c"
DATASET_C = "core/lowlevel_runtime/c/rll_hz_moresco_2022_q16.c"
DATASET_CSV = ROOT / "data/real/Hz_data_real.csv"
REFERENCE = ROOT / "results/moresco_hz_chi2.json"
REPORT = ROOT / "artifacts/canonical-coupling/hz-real-validation.json"
EXPECTED_SHA256 = "1194fe2066dc3d92b4870cfb03d2cdbe2a316deae2e1355943f7f2ccca6d52b6"
EXPECTED_FNV1A64 = 0x7BCBEEAF770538D3
EXPECTED_CRC32 = 0xDAD619BD
Q16 = 65536.0


def run(command: list[str]) -> dict[str, object]:
    cp = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": cp.returncode,
        "stdout": cp.stdout,
        "stderr": cp.stderr,
    }


def fnv1a64(data: bytes) -> int:
    value = 14695981039346656037
    for byte in data:
        value ^= byte
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    raw = DATASET_CSV.read_bytes()
    data_sha256 = hashlib.sha256(raw).hexdigest()
    data_fnv1a64 = fnv1a64(raw)
    data_crc32 = zlib.crc32(raw) & 0xFFFFFFFF

    with tempfile.TemporaryDirectory(prefix="rll-hz-") as tmp:
        tmpdir = Path(tmp)
        wrapper = tmpdir / "receipt.c"
        exe = tmpdir / "receipt"
        combined = tmpdir / "combined.o"
        wrapper.write_text(
            '#include <stdio.h>\n'
            '#include "rll_hz_freestanding.h"\n'
            'int main(void){\n'
            '  rll_hz_dual_receipt r=rll_hz_run_moresco_nominal_q16();\n'
            '  printf("%u %lld %lld %lld %llu %u %u\\n", '
            'r.rows,(long long)r.lcdm.chi2_q16,(long long)r.rll.chi2_q16,'
            '(long long)r.delta_chi2_q16,(unsigned long long)r.dataset_fnv1a64,'
            '(unsigned)r.dataset_crc32,(unsigned)r.claim_allowed);\n'
            '  return 0;\n'
            '}\n',
            encoding="utf-8",
        )

        commands = [
            [
                "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(wrapper), CANONICAL, MODEL, DATASET_C,
                f"-I{INCLUDE}", "-o", str(exe),
            ],
            [str(exe)],
            [
                "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
                "-nostdlib", "-r", CANONICAL, MODEL, DATASET_C,
                f"-I{INCLUDE}", "-o", str(combined),
            ],
            ["nm", "-u", str(combined)],
            [
                "clang", "--target=armv7a-none-eabi", "-std=c11", "-Oz",
                "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-builtin",
                "-fno-stack-protector", "-nostdlib", "-c", MODEL,
                f"-I{INCLUDE}", "-o", str(tmpdir / "armv7.o"),
            ],
            [
                "clang", "--target=aarch64-none-elf", "-std=c11", "-Oz",
                "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-builtin",
                "-fno-stack-protector", "-nostdlib", "-c", MODEL,
                f"-I{INCLUDE}", "-o", str(tmpdir / "aarch64.o"),
            ],
        ]
        results = [run(command) for command in commands]

    receipt_values: dict[str, object] = {}
    if results[1]["returncode"] == 0:
        fields = str(results[1]["stdout"]).strip().split()
        if len(fields) == 7:
            rows, lcdm_q16, rll_q16, delta_q16, fnv, crc, claim = map(int, fields)
            receipt_values = {
                "rows": rows,
                "lcdm_chi2_q16": lcdm_q16,
                "rll_chi2_q16": rll_q16,
                "delta_chi2_q16": delta_q16,
                "lcdm_chi2": lcdm_q16 / Q16,
                "rll_chi2": rll_q16 / Q16,
                "delta_chi2": delta_q16 / Q16,
                "dataset_fnv1a64": f"{fnv:016x}",
                "dataset_crc32": f"{crc:08x}",
                "claim_allowed": bool(claim),
            }

    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    reference_values = {
        "lcdm_chi2": float(reference["lcdm"]["chi2"]),
        "rll_chi2": float(reference["rll"]["chi2"]),
        "delta_chi2": float(reference["comparison"]["delta_chi2_rll_minus_lcdm"]),
    }
    parity = bool(receipt_values) and all(
        abs(float(receipt_values[key]) - value) <= 0.005
        for key, value in reference_values.items()
    )
    undefined_empty = results[3]["returncode"] == 0 and not str(results[3]["stdout"]).strip()
    data_anchor_ok = (
        data_sha256 == EXPECTED_SHA256
        and data_fnv1a64 == EXPECTED_FNV1A64
        and data_crc32 == EXPECTED_CRC32
    )
    commands_ok = all(item["returncode"] == 0 for item in results)
    status = "PASS" if commands_ok and undefined_empty and data_anchor_ok and parity else "FAIL"

    report = {
        "schema": "rll_hz_real_freestanding_validation_v1",
        "status": status,
        "claim_allowed": False,
        "source": {
            "path": "data/real/Hz_data_real.csv",
            "git_blob": "3ac5da2594bfc127c28c6b4e817259e1bee28085",
            "bytes": len(raw),
            "line_ending": "CRLF",
            "rows": 33,
            "sha256": data_sha256,
            "fnv1a64": f"{data_fnv1a64:016x}",
            "crc32": f"{data_crc32:08x}",
            "anchor_ok": data_anchor_ok,
        },
        "parameters_q16": {
            "H0": 4417126,
            "Omega_m": 20644,
            "Omega_s0": 1311,
            "z_t": 65536,
            "w_t": 19661,
        },
        "receipt": receipt_values,
        "reference_float64": reference_values,
        "q16_float64_parity_abs_tolerance": 0.005,
        "parity_ok": parity,
        "combined_undefined_symbols_empty": undefined_empty,
        "armv7_object": results[4]["returncode"] == 0,
        "aarch64_object": results[5]["returncode"] == 0,
        "sha256": {
            "header": sha256("core/lowlevel_runtime/include/rll_hz_freestanding.h"),
            "model": sha256(MODEL),
            "compiled_dataset": sha256(DATASET_C),
        },
        "boundaries": {
            "nominal_parameters_not_fitted": True,
            "result_is_not_mcmc": True,
            "result_is_not_independent_replication": True,
            "claim_allowed": False,
        },
        "commands": results,
    }

    if args.write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "rows": receipt_values.get("rows"),
        "lcdm_chi2": receipt_values.get("lcdm_chi2"),
        "rll_chi2": receipt_values.get("rll_chi2"),
        "delta_chi2": receipt_values.get("delta_chi2"),
        "parity_ok": parity,
        "armv7": report["armv7_object"],
        "aarch64": report["aarch64_object"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
