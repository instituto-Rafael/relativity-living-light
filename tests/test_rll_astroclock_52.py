"""Existing RLL Python test suite: check freestanding calendar and solar-model falsifiers."""
from __future__ import annotations
import importlib.util, json, shutil, subprocess, tempfile
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"native/astroclock52/rll_astroclock_calendar.c"
V=ROOT/"tests/c/test_rll_astroclock_calendar.c"
P=ROOT/"scripts/rll_astroclock_52.py"
class Astroclock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location("rll_astroclock_52",P)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        cls.model=mod
    def test_4x3_seasons_are_model_not_cultural_proof(self):
        self.assertEqual(len(self.model.rows()),72)
        self.assertEqual(len({x["sector_12"] for x in self.model.rows()}),12)
        self.assertTrue(all(x["is_historical_survey"] is False for x in self.model.rows()))
    def test_ideal_equinox_and_solstices(self):
        self.assertAlmostEqual(self.model.declination(0),0,places=9)
        self.assertAlmostEqual(self.model.declination(90),23.44,places=6)
        self.assertAlmostEqual(self.model.declination(270),-23.44,places=6)
        for _,lat,_,_ in self.model.SITES:
            _,az1,az2,_=self.model.solar_geometry(lat,0)
            self.assertAlmostEqual(az1,90,places=9)
            self.assertAlmostEqual(az2,270,places=9)
    def test_52_haab_not_solar_years(self):
        self.assertEqual(52*365,18980)
        self.assertEqual(73*260,18980)
        drift=52*self.model.TROPICAL_YEAR_DAYS-18980
        self.assertGreater(drift,12)
        self.assertLess(drift,13)
    def test_giza_south_meridian_conditional_not_date_proof(self):
        with tempfile.TemporaryDirectory() as d:
            receipt=self.model.run(d)
            self.assertFalse(receipt["giza_ancient_star_coordinates_calculated"])
            self.assertFalse(receipt["claim_allowed"])
            self.assertAlmostEqual(receipt["giza_conditional_target_declination_deg"],-15.021,places=3)
            self.assertTrue((Path(d)/"solar_12_sectors_ideal_horizon.csv").exists())
    def test_freestanding_C_real_execution(self):
        cc=shutil.which("cc") or shutil.which("clang")
        self.assertIsNotNone(cc)
        with tempfile.TemporaryDirectory() as d:
            binary=str(Path(d)/"calendar")
            p=subprocess.run([cc,"-std=c11","-O2","-Wall","-Wextra","-Werror",
                "-pedantic","-ffreestanding","-fno-builtin",str(C),str(V),"-o",binary],
                capture_output=True,text=True,timeout=90)
            self.assertEqual(p.returncode,0,p.stderr)
            run=subprocess.run([binary],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr)
    def test_freestanding_ARM_objects(self):
        cc=shutil.which("clang");nm=shutil.which("nm")
        if not cc or not nm:self.skipTest("Clang+nm not present")
        with tempfile.TemporaryDirectory() as d:
            for target in ("armv7a-linux-androideabi21","aarch64-linux-android28"):
                with self.subTest(target=target):
                    object_file=str(Path(d)/(target+".o"))
                    p=subprocess.run([cc,"--target="+target,"-std=c11","-O2",
                        "-ffreestanding","-fno-builtin","-fno-stack-protector",
                        "-Wall","-Wextra","-Werror","-c",str(C),"-o",object_file],
                        capture_output=True,text=True,timeout=90)
                    self.assertEqual(p.returncode,0,p.stderr)
                    p=subprocess.run([nm,"-u",object_file],capture_output=True,text=True,timeout=30)
                    self.assertEqual(p.returncode,0,p.stderr)
                    self.assertEqual(p.stdout.strip(),"")
if __name__=="__main__":unittest.main()
