"""Falsify the 51-year period premise at the code/evidence boundary, offline."""
from __future__ import annotations
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/climate/rll_gravity_climate_51y_source_registry.v1.json"
SRC=ROOT/"native/geocycle_51y/rll_geocycle_falsifier.c"
VECTORS=ROOT/"tests/c/test_rll_geocycle_51y_native.c"

class Geocycle51Falsification(unittest.TestCase):
    def test_catalog_does_not_claim_hydrated_or_verified_period(self):
        obj=json.loads(REG.read_text(encoding="utf-8"))
        self.assertIs(obj["claim_allowed"],False)
        self.assertEqual(obj["status"],"SOURCE_CATALOG_ONLY_NOT_INGESTED")
        self.assertEqual(obj["scope"]["years_inclusive"],51)
        self.assertIn("UNIDENTIFIABLE",obj["scope"]["periodicity_conclusion"])
        self.assertGreaterEqual(len(obj["sources"]),8)
        self.assertTrue(all(x["state"].startswith(("TOKEN_VAZIO","REFERENCE_ONLY")) for x in obj["sources"]))
        ids=[x["id"] for x in obj["sources"]]
        self.assertEqual(len(ids),len(set(ids)))

    def test_existing_rll_8x8_compatibility(self):
        registry=json.loads((ROOT/"data/climate/rll_climate_multiphysics_registry.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["matrix_contract"]["shape"],[8,8])
        self.assertIs(registry["claim_allowed"],False)

    def test_native_host_negative_vectors(self):
        cc=shutil.which("cc") or shutil.which("clang")
        self.assertIsNotNone(cc,"Native C compiler required to actually test code")
        with tempfile.TemporaryDirectory() as tmp:
            exe=Path(tmp)/"rll51"
            p=subprocess.run([cc,"-std=c11","-O2","-Wall","-Wextra",
                "-Werror","-pedantic",str(SRC),str(VECTORS),"-o",str(exe)],
                capture_output=True,text=True,timeout=90)
            self.assertEqual(p.returncode,0,p.stderr)
            run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    def test_arm32_arm64_freestanding_object_no_libc(self):
        clang=shutil.which("clang")
        nm=shutil.which("nm")
        if not clang or not nm:self.skipTest("clang + nm required for cross ABI")
        with tempfile.TemporaryDirectory() as tmp:
            for target in ("armv7a-linux-androideabi21","aarch64-linux-android28"):
                with self.subTest(target=target):
                    output=str(Path(tmp)/(target+".o"))
                    p=subprocess.run([clang,"--target="+target,"-std=c11",
                        "-O2","-ffreestanding","-fno-builtin",
                        "-fno-stack-protector","-Wall","-Wextra","-Werror",
                        "-c",str(SRC),"-o",output],
                        capture_output=True,text=True,timeout=90)
                    self.assertEqual(p.returncode,0,p.stderr)
                    p=subprocess.run([nm,"-u",output],capture_output=True,text=True,timeout=30)
                    self.assertEqual(p.returncode,0,p.stderr)
                    self.assertEqual(p.stdout.strip(),"",p.stdout)

if __name__=="__main__":
    unittest.main()
