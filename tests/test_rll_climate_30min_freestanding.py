"""Offline RLL climate patch crosswalk + freestanding falsification (synthetic ONLY)."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/climate_tornado_ionosphere/rll_climate_30min.c"
TEST = ROOT / "tests/c/test_rll_climate_30min_native.c"
REGISTRY = ROOT / "data/climate/rll_climate_multiphysics_registry.v1.json"


class ClimateTornadoIonosphere(unittest.TestCase):
    def test_rll_8x8_contract_remains_untouched(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertIs(data["claim_allowed"], False)
        self.assertEqual(data["matrix_contract"]["shape"], [8, 8])
        by_column = {s["column"]: s["id"] for s in data["sectors"]}
        self.assertEqual(by_column[2], "atmospheric_dynamics_clouds_vortices")
        self.assertEqual(by_column[6], "heliophysics_ionosphere_magnetosphere")
        self.assertEqual(by_column[7], "extremes_forecast_exposure_verification")

    def test_host_native_adversarial_vectors(self):
        compiler = shutil.which("cc") or shutil.which("clang")
        self.assertIsNotNone(compiler, "C compiler required for real execution")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "rll30"
            subprocess.run(
                [compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-pedantic", str(SOURCE), str(TEST), "-o", str(out)],
                check=True, capture_output=True, text=True, timeout=90,
            )
            p = subprocess.run([str(out)], capture_output=True, text=True, timeout=15)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_arm32_arm64_pure_objects(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if not clang or not nm:
            self.skipTest("cross-ABI inspection requires clang and nm")
        with tempfile.TemporaryDirectory() as d:
            for target in ("armv7a-linux-androideabi21", "aarch64-linux-android28"):
                with self.subTest(target=target):
                    output = str(Path(d) / (target + ".o"))
                    subprocess.run(
                        [clang, "--target=" + target, "-std=c11", "-O2",
                         "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
                         "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                         "-o", output],
                        check=True, capture_output=True, text=True, timeout=60,
                    )
                    undefined = subprocess.run(
                        [nm, "-u", output], check=True, capture_output=True, text=True,
                    ).stdout
                    self.assertEqual(undefined.strip(), "", undefined)


if __name__ == "__main__":
    unittest.main()
