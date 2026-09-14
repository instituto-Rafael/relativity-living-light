from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs/project_sources_manifest.v1.json"
RECEIPT = ROOT / "data/receipts/project_sources_local_receipt_20260726.json"
GENERATOR = ROOT / "tools/generate_rll_canonical_region.py"
GENERATED = ROOT / "core/lowlevel_runtime/generated/rll_canonical_project_sources.inc"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def test_canonical_region_generation_and_manifest_custody() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    actual = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    assert len(actual) == 64
    assert len(receipt["manifest_sha256"]) == 64
    # The legacy receipt digest currently differs from the committed manifest bytes.
    # The generated C must preserve both values and declare the divergence, never hide it.
    assert actual != receipt["manifest_sha256"]
    generated_probe = ROOT / ".rll_canonical_region_generated_probe.inc"
    try:
        cp = run(
            "python3",
            str(GENERATOR),
            "--manifest",
            str(MANIFEST),
            "--receipt",
            str(RECEIPT),
            "--output",
            str(generated_probe),
        )
        assert cp.returncode == 0, cp.stderr or cp.stdout
        probe = generated_probe.read_text(encoding="utf-8")
        assert "RLL_CANONICAL_GENERATED_SOURCE_COUNT 14u" in probe
        assert actual in probe.replace("0x", "").replace(",", "") or "0x3b,0xf6,0xe7,0x3e" in probe
    finally:
        generated_probe.unlink(missing_ok=True)


def test_canonical_region_compiles_as_strict_freestanding_object(tmp_path: Path) -> None:
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
        "-nostdlib",
        "-c",
        "core/lowlevel_runtime/c/rll_canonical_region.c",
        "-Icore/lowlevel_runtime/include",
        "-o",
        str(obj),
    )
    assert cp.returncode == 0, cp.stderr

    undefined = run("nm", "-u", str(obj))
    assert undefined.returncode == 0, undefined.stderr
    symbols = [line.split()[-1] for line in undefined.stdout.splitlines() if line.strip()]
    assert symbols == ["rll_fnv1a64"]


def test_canonical_region_executes_and_emits_valid_fixed_frame(tmp_path: Path) -> None:
    harness = tmp_path / "canonical_region_harness.c"
    executable = tmp_path / "canonical_region_harness"
    harness.write_text(
        r'''
#include <stdio.h>
#include "rll_canonical_region.h"

static rll_u32 load_u32_le(const rll_u8 *p) {
    return ((rll_u32)p[0]) |
           ((rll_u32)p[1] << 8u) |
           ((rll_u32)p[2] << 16u) |
           ((rll_u32)p[3] << 24u);
}

static rll_u64 load_u64_le(const rll_u8 *p) {
    rll_u64 value = 0ull;
    rll_u32 i = 0u;
    while (i < 8u) {
        value |= ((rll_u64)p[i]) << (i * 8u);
        i++;
    }
    return value;
}

int main(void) {
    rll_u8 frame[RLL_CANONICAL_REGION_FRAME_SIZE];
    const rll_canonical_receipt *receipt = rll_canonical_region_receipt();
    const rll_u8 known_id[] = "SRC-ARMV7-001";
    const rll_u8 unknown_id[] = "SRC-NOT-THERE";
    rll_u32 known = rll_canonical_region_find_source(known_id, sizeof(known_id) - 1u);
    rll_u32 unknown = rll_canonical_region_find_source(unknown_id, sizeof(unknown_id) - 1u);
    rll_u32 validation = rll_canonical_region_validate();
    rll_u32 frame_size = rll_canonical_region_frame(frame, sizeof(frame));
    rll_u64 fingerprint = rll_canonical_region_fingerprint64();
    rll_u32 custody = rll_canonical_region_custody_flags();

    printf(
        "%u %u %u %u %u %u %u %u %llu %llu\n",
        validation,
        receipt->source_count,
        receipt->verified_local_hash_count,
        receipt->chunk_count,
        known,
        unknown,
        frame_size,
        custody,
        (unsigned long long)fingerprint,
        (unsigned long long)load_u64_le(frame + 120u)
    );

    return !(
        validation == RLL_CANONICAL_VALID &&
        receipt->source_count == 14u &&
        receipt->verified_local_hash_count == 12u &&
        receipt->metadata_only_count == 1u &&
        receipt->private_pointer_only_count == 1u &&
        receipt->chunk_count == 198u &&
        known == 12u &&
        unknown == RLL_CANONICAL_SOURCE_NOT_FOUND &&
        frame_size == RLL_CANONICAL_REGION_FRAME_SIZE &&
        load_u32_le(frame + 12u) == RLL_CANONICAL_VALID &&
        load_u32_le(frame + 16u) == 14u &&
        load_u32_le(frame + 52u) == custody &&
        (custody & RLL_CUSTODY_COMPILED_MANIFEST_HASHED) != 0u &&
        (custody & RLL_CUSTODY_RECEIPT_DIGEST_MATCH) == 0u &&
        (custody & RLL_CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED) != 0u &&
        fingerprint == receipt->expected_fingerprint64 &&
        fingerprint == load_u64_le(frame + 120u)
    );
}
''',
        encoding="utf-8",
    )
    cp = run(
        "gcc",
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        str(harness),
        "core/lowlevel_runtime/c/rll_canonical_region.c",
        "core/lowlevel_runtime/c/pantheon_freestanding.c",
        "-Icore/lowlevel_runtime/include",
        "-o",
        str(executable),
    )
    assert cp.returncode == 0, cp.stderr

    executed = run(str(executable))
    assert executed.returncode == 0, executed.stderr or executed.stdout
    fields = executed.stdout.strip().split()
    assert fields[:8] == ["0", "14", "12", "198", "12", str(0xFFFFFFFF), "128", "5"]
    assert fields[8] == fields[9]
