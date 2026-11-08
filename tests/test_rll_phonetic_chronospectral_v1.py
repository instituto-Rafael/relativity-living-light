"""stdlib standalone test: python -m unittest discover -s tests -p test_rll_phonetic_chronospectral_v1.py -v"""
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("target",ROOT/"scripts/rll_phonetic_chronospectral_v1.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DATA=ROOT/"data/experiments/rll_phonetic_chronospectral_v1/pilot_10_languages.json"

class TestTypedSeparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(DATA.read_text(encoding="utf-8"))
    def test_ten_distinct_languages(self):
        self.assertEqual(len(self.doc["language_items"]),10)
        self.assertEqual(len({e["id"] for e in self.doc["language_items"]}),10)
    def test_same_han_glyph_different_ipa(self):
        d={e["id"]:e for e in self.doc["language_items"]}
        self.assertEqual(d["ja"]["word"],d["zh"]["word"])
        self.assertNotEqual(d["ja"]["ipa"],d["zh"]["ipa"])
    def test_portuguese_spanish_same_spelling_different_ipa(self):
        d={e["id"]:e for e in self.doc["language_items"]}
        self.assertEqual(d["pt"]["word"].encode(),d["es"]["word"].encode())
        self.assertNotEqual(d["pt"]["ipa"],d["es"]["ipa"])
    def test_arabic_bidirectional_metadata(self):
        ar=next(e for e in self.doc["language_items"] if e["id"]=="ar")
        q=mod.word_measure(ar)
        self.assertEqual(q["writing_direction"],"RTL")
        self.assertGreater(q["bidi_classes_logical_codepoints"].get("AL",0),0)
    def test_lossless_source_encoding(self):
        self.assertTrue(all(mod.word_measure(x)["zlib_exact_roundtrip"] for x in self.doc["language_items"]))
    def test_phoneme_token_entropy_not_language_entropy(self):
        self.assertTrue(mod.word_measure(self.doc["language_items"][0])["not_a_language_entropy_estimate"])
    def test_shannon_constant_simple(self):
        self.assertAlmostEqual(mod.entropy(["a","a","b","b"]),1.0,10)
    def test_empty_entropy_rejected(self):
        with self.assertRaises(ValueError):mod.entropy([])
    def test_synthetic_f0_contrast(self):
        self.assertEqual(mod.f0_hz("ma1_high_level",0.5),208)
        self.assertLess(mod.f0_hz("ma3_fall_rise",0.6),mod.f0_hz("ma3_fall_rise",0))
        self.assertGreater(mod.f0_hz("ma3_fall_rise",1),mod.f0_hz("ma3_fall_rise",0.6))
    def test_wave_sample_bounds(self):
        a,f=mod.make_waveform("ma1_high_level")
        self.assertEqual(len(a),mod.SAMPLE_COUNT)
        self.assertLessEqual(max(abs(x) for x in a),1)
        self.assertEqual(len(f),len(a))
    def test_dft_finite_nonzero(self):
        a,_=mod.make_waveform("ma3_fall_rise")
        feat=mod.dft_summary(a[900:1156])
        self.assertTrue(math.isfinite(feat["centroid_hz"]))
        self.assertTrue(math.isfinite(feat["spectral_power_entropy_bits"]))
    def test_beta_proper_time_and_c(self):
        v=mod.special_relativity(0.6)
        self.assertAlmostEqual(v["gamma"],1.25,12)
        self.assertAlmostEqual(v["moving_clock_proper_dt_per_frame_dt"],0.8,12)
        self.assertAlmostEqual(v["receding_radial_doppler_1_plus_z"],2.0,12)
        self.assertEqual(v["local_light_speed_m_s"],299792458.0)
    def test_no_superluminal_inertial_beta(self):
        with self.assertRaises(ValueError):mod.special_relativity(1.0)
    def test_age_difference_with_covariance(self):
        x=mod.stellar_age_discrepancy((12,1),(2,0.5),0)
        self.assertAlmostEqual(x["difference_z_score"],10/math.sqrt(1.25),12)
    def test_no_unmatched_age_epochs(self):
        with self.assertRaises(ValueError):mod.stellar_age_discrepancy((12,1),(2,0.5),common_epoch=False)
    def test_no_unphysical_variance(self):
        with self.assertRaises(ValueError):mod.stellar_age_discrepancy((12,0),(2,0))
    def test_full_standalone_reproduction(self):
        with tempfile.TemporaryDirectory() as td:
            result=mod.produce(self.doc,td)
            self.assertEqual(len(result["phonetic_items"]),10)
            self.assertFalse(result["claim_allowed"])
            self.assertFalse(result["real_cosmology_observations"])
            self.assertIn("TOKEN_VAZIO_NO_CALIBRATION",result["synthetic_tonal_waves"]["ma1_high_level"]["physical_acoustic_pressure_pa"])
            self.assertEqual(len(list(Path(td).glob("*.wav"))),2)
            with wave.open(str(next(Path(td).glob("*.wav"))),"rb") as f:
                self.assertEqual(f.getframerate(),mod.SAMPLE_RATE)
            self.assertTrue(Path(td,"receipt.json").exists())
    def test_no_implicit_energy_claim(self):
        with tempfile.TemporaryDirectory() as td:
            result=mod.produce(self.doc,td)
            self.assertFalse(result["native_speech_measured"])
            self.assertIn("acoustic pressure wave != quantum wavefunction != gravitational strain",result["non_equivalences"])

if __name__=="__main__":unittest.main()
