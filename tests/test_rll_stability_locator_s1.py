"""Research-only CI bridge; no network, requests, pip or synthetic skill claims."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"native/climate_stability_locator/rll_stability_locator.c"
TEST=ROOT/"tests/c/test_rll_stability_locator_native.c"
BRIDGE=ROOT/"scripts/rll_stability_information_bridge.py"
CONTRACT=ROOT/"data/contracts/rll_stability_locator_s1.v1.json"

class StabilityLocatorS1(unittest.TestCase):
    def test_claim_and_source_contract(self):
        d=json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertIs(d["claim_allowed"],False)
        self.assertEqual(d["forecast_horizon_minutes_max"],20160)
        self.assertEqual(d["rapid_observation_minutes_max"],30)
        self.assertEqual(d["data_status"],"SOURCE_POINTERS_ONLY")
        self.assertEqual(len(d["forecast_features"]),5)

    def test_host_c_adversarial_falsifiers(self):
        cc=shutil.which("cc") or shutil.which("clang")
        self.assertIsNotNone(cc)
        with tempfile.TemporaryDirectory() as tmp:
            exe=Path(tmp)/"rll_locator"
            r=subprocess.run([cc,"-std=c11","-O2","-Wall","-Wextra","-Werror",
                "-pedantic",str(SRC),str(TEST),"-o",str(exe)],capture_output=True,
                text=True,timeout=90)
            self.assertEqual(r.returncode,0,r.stderr)
            q=subprocess.run([str(exe)],capture_output=True,text=True,timeout=30)
            self.assertEqual(q.returncode,0,q.stdout+q.stderr)

    def test_armv7_and_aarch64_no_undefined(self):
        cc=shutil.which("clang");nm=shutil.which("nm")
        if not cc or not nm:self.skipTest("cross compiler not available")
        with tempfile.TemporaryDirectory() as tmp:
            for target in ("armv7a-linux-androideabi21","aarch64-linux-android28"):
                with self.subTest(target=target):
                    out=str(Path(tmp)/(target+".o"))
                    r=subprocess.run([cc,"--target="+target,"-std=c11","-O2",
                      "-Wall","-Wextra","-Werror","-ffreestanding","-fno-builtin",
                      "-fno-stack-protector","-c",str(SRC),"-o",out],
                      capture_output=True,text=True,timeout=90)
                    self.assertEqual(r.returncode,0,r.stderr)
                    n=subprocess.run([nm,"-u",out],capture_output=True,text=True,timeout=30)
                    self.assertEqual(n.returncode,0,n.stderr)
                    self.assertEqual(n.stdout.strip(),"")

    def test_compression_and_predecessor_boundary(self):
        spec=importlib.util.spec_from_file_location("rll_info",BRIDGE)
        assert spec and spec.loader
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        receipt=mod.run()
        self.assertFalse(receipt["forecast_skill_established"])
        self.assertFalse(receipt["physical_coupling_established"])
        v=list(receipt["synthetic_fixture"].values())
        self.assertTrue(all(x["lossless"] for x in v))
        self.assertNotEqual(len({x["compressed_to_raw_ratio"]["gzip"] for x in v}),1)
        self.assertEqual(receipt["scd1"]["records"],10449)
        self.assertEqual(receipt["scd1"]["seed_vs_verbose_pct"],22.474)
        self.assertEqual(receipt["scd1"]["seed_vs_plain_pct"],4.885)

if __name__=="__main__":unittest.main()
